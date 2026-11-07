// Route editing and plan approval must be separate tasks, without losing advanced controls.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');

async function main() {
  const browser = await chromium.launch({ channel: process.env.BROWSER_CHANNEL });
  try {
    const page = await browser.newPage({ viewport: { width: 1360, height: 1000 } });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    const base = process.env.BASE_URL || 'http://localhost:8000';
    const button = name => page.getByRole('button', { name, exact: true });
    const shot = async name => {
      if (process.env.SHOTS) {
        fs.mkdirSync(process.env.SHOTS, { recursive: true });
        await page.screenshot({ path: path.join(process.env.SHOTS, name + '.png'), fullPage: true });
      }
    };
    await page.goto(base);
    await button('Multi-warehouse example').click();
    await button('Calculate plan').waitFor();
    assert.equal(await button('Multi-warehouse example').isVisible(), false);
    await shot('focused-data');
    const [calculated] = await Promise.all([
      page.waitForResponse(r => /\/scenarios\/\d+\/runs$/.test(r.url()) && r.request().method() === 'POST'),
      button('Calculate plan').click(),
    ]);
    const original = await calculated.json();
    await page.getByRole('heading', { name: 'Where the cost sits' }).waitFor();
    for (const name of ['Where the cost sits', 'Warehouse load', 'Plan details']) {
      assert.equal(await page.getByRole('heading', { name, exact: true }).locator('xpath=../..').getAttribute('open'), null);
    }
    const mutations = [];
    page.on('request', request => {
      if (['POST', 'DELETE'].includes(request.method()) && /\/(routes|overrides)(\/\d+)?$/.test(request.url())) mutations.push(request.url());
    });
    await button('Create manual route').click();
    await page.getByRole('heading', { name: 'Manual route', exact: true }).waitFor();
    assert.equal(await page.getByRole('textbox', { name: 'Explanation text' }).count(), 0);
    assert.equal(await page.getByRole('heading', { name: 'Explanation', exact: true }).count(), 0);
    assert.equal(await button('Approve plan').count(), 0);
    assert.equal(await page.getByRole('combobox', { name: 'Serve from' }).count(), 0);
    await page.getByRole('combobox', { name: 'Warehouse stop 1', exact: true }).selectOption('B');
    await page.getByRole('textbox', { name: 'Route reason (required)' }).fill('Unsaved route draft');
    await shot('focused-route');
    await page.setViewportSize({ width: 390, height: 844 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    await page.setViewportSize({ width: 1360, height: 1000 });
    await button('Back to Results').click();
    assert.deepEqual(mutations, []);
    await button('Review & approve').click();
    await page.getByRole('heading', { name: 'Review & approve', exact: true }).waitFor();
    assert.equal(await page.getByRole('combobox', { name: 'Warehouse stop 1', exact: true }).count(), 0);
    assert.equal(await page.getByRole('combobox', { name: 'Serve from' }).count(), 0);
    assert.equal(await button('Export approved plan (ZIP)').count(), 0);
    assert.equal(await button('Write standard summary').isVisible(), true);
    assert.equal(await button('Write with AI assistant').isVisible(), true);
    await button('Write standard summary').click();
    const originalText = await page.getByRole('textbox', { name: 'Explanation text' }).inputValue();
    assert.match(originalText, /102/);
    await shot('focused-review');
    await page.getByText('Adjust plan', { exact: true }).click();
    await button('Change delivery warehouse').click();
    await page.getByRole('heading', { name: 'Delivery warehouse', exact: true }).waitFor();
    assert.equal(await page.getByRole('combobox', { name: 'Serve from' }).isVisible(), true);
    assert.equal(await page.getByRole('combobox', { name: 'Warehouse stop 1', exact: true }).count(), 0);
    assert.equal(await button('Approve plan').count(), 0);
    await button('Back to Results').click();
    assert.deepEqual(mutations, []);
    await button('Create manual route').click();
    await page.getByRole('combobox', { name: 'Warehouse stop 1', exact: true }).selectOption('B');
    await button('Add warehouse stop').click();
    await page.getByRole('combobox', { name: 'Warehouse stop 2', exact: true }).selectOption('D');
    await page.getByRole('spinbutton', { name: 'Route pallets' }).fill('6');
    const reason = 'Partner allocation retained';
    await page.getByRole('textbox', { name: 'Route reason (required)' }).fill(reason);
    const [saved] = await Promise.all([
      page.waitForResponse(r => /\/routes$/.test(r.url()) && r.request().method() === 'POST'),
      button('Save route and recalculate').click(),
    ]);
    const child = await saved.json();
    assert.equal(child.comparison.optimised.total, 132);
    await button('Review & approve').click();
    await page.getByText(/^Manual decisions \(/).click();
    await page.getByText(reason, { exact: false }).waitFor();
    assert.equal(await button('Save route and recalculate').count(), 0);
    assert.equal(await button('Remove manual route 1').count(), 0);
    await page.getByText(/^Version history \(/).click();
    const originalRow = page.getByRole('row').filter({ has: page.getByRole('cell', { name: `Plan ${original.id}`, exact: true }) });
    await Promise.all([
      page.waitForResponse(r => r.url().endsWith(`/runs/${original.id}/explanation`)),
      originalRow.getByRole('button', { name: 'Open', exact: true }).click(),
    ]);
    assert.equal(await page.getByRole('textbox', { name: 'Explanation text' }).inputValue(), originalText);
    const unchanged = await (await page.request.get(`${base}/api/runs/${original.id}`)).json();
    assert.equal(unchanged.comparison.optimised.total, 102);
    assert.deepEqual(unchanged.route_pins, []);
    assert.equal(mutations.length, 1);
    assert.deepEqual(errors, []);
    console.log('PASS: focused route/delivery editors, review without edit forms, cancelled changes untouched, child cost132, read-only decisions and version explanation reload');
  } finally { await browser.close(); }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
