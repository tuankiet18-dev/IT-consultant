// Verify a human can choose a more expensive path, review its cost, and remove it.
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
    const button = name => page.getByRole('button', { name, exact: true });
    const step = name => page.getByRole('navigation', { name: 'Workflow' }).getByRole('button', { name });
    const shots = process.env.SHOTS;
    if (shots) fs.mkdirSync(shots, { recursive: true });
    await page.goto(process.env.BASE_URL || 'http://localhost:8000/');
    await page.getByText('Extended network examples').click();
    await button('Multi-warehouse example').click();
    const [calculated] = await Promise.all([
      page.waitForResponse(r => /\/scenarios\/\d+\/runs$/.test(r.url()) && r.request().method() === 'POST'),
      button('Calculate plan').click(),
    ]);
    const original = await calculated.json();
    assert.equal(original.comparison.optimised.total, 102);
    await page.getByRole('combobox', { name: 'Highlight a warehouse' }).selectOption('E');
    const sameRun = await (await page.request.get(`${process.env.BASE_URL || 'http://localhost:8000'}/api/runs/${original.id}`)).json();
    assert.equal(sameRun.comparison.optimised.total, 102);
    await page.getByText('Highlighting changes the view only.', { exact: false }).waitFor();
    await button('Create manual route').click();
    await page.getByRole('combobox', { name: 'Warehouse stop 1', exact: true }).selectOption('B');
    await button('Add warehouse stop').click();
    await page.getByRole('combobox', { name: 'Warehouse stop 2', exact: true }).selectOption('D');
    await page.getByRole('spinbutton', { name: 'Route pallets', exact: true }).fill('6');
    const reason = 'Maintain agreed partner allocation';
    await page.getByRole('textbox', { name: 'Route reason (required)', exact: true }).fill(reason);
    await page.getByText('12 cost units per pallet, including all freight', { exact: false }).waitFor();
    if (shots) await page.screenshot({ path: path.join(shots, 'manual-route-form.png'), fullPage: true });
    const [saved] = await Promise.all([
      page.waitForResponse(r => /\/runs\/\d+\/routes$/.test(r.url()) && r.request().method() === 'POST'),
      button('Save route and recalculate').click(),
    ]);
    assert.equal(saved.status(), 200, await saved.text());
    const child = await saved.json();
    assert.equal(child.comparison.optimised.total, 132);
    assert.equal(child.cost_of_planner_decisions, 30);
    assert.equal(child.parent_run_id, original.id);
    assert.deepEqual(child.route_pins[0].warehouses, ['B', 'D']);
    await page.getByText('Cost difference from the original plan: +30 cost units.', { exact: false }).waitFor();
    const diagram = page.getByRole('img', { name: /Allocation flow/ });
    await diagram.waitFor();
    assert.equal(await diagram.locator('path[data-route-from="B"][data-route-to="D"]').getAttribute('data-used'), 'true');
    if (shots) await page.screenshot({ path: path.join(shots, 'manual-route-result.png'), fullPage: true });
    await button('Create manual route').click();
    await page.getByText(reason, { exact: false }).waitFor();
    const [removed] = await Promise.all([
      page.waitForResponse(r => /\/routes\/0$/.test(r.url()) && r.request().method() === 'DELETE'),
      button('Remove manual route 1').click(),
    ]);
    assert.equal(removed.status(), 200, await removed.text());
    const restored = await removed.json();
    assert.equal(restored.comparison.optimised.total, 102);
    assert.deepEqual(restored.route_pins, []);
    await button('Create manual route').click();
    await page.getByRole('combobox', { name: 'Warehouse stop 1', exact: true }).selectOption('A');
    await button('Add warehouse stop').click();
    await page.getByRole('combobox', { name: 'Warehouse stop 2', exact: true }).selectOption('E');
    await page.getByRole('spinbutton', { name: 'Route pallets', exact: true }).fill('6');
    await page.getByRole('textbox', { name: 'Route reason (required)', exact: true }).fill('Customer requested handling location');
    const [savedAgain] = await Promise.all([
      page.waitForResponse(r => /\/runs\/\d+\/routes$/.test(r.url()) && r.request().method() === 'POST'),
      button('Save route and recalculate').click(),
    ]);
    assert.equal((await savedAgain.json()).comparison.optimised.total, 114);
    await step('Review & approve').click();
    await button('Generate explanation').click();
    assert.match(await page.getByRole('textbox', { name: 'Explanation text' }).inputValue(), /manual|reserved/i);
    await button('Approve plan').click();
    await button('Export approved plan (ZIP)').waitFor();
    await page.getByText(/^Manual decisions \(/).waitFor();
    await button('Save route and recalculate').waitFor({ state: 'detached' });
    assert.equal(await button('Save route and recalculate').count(), 0);
    await page.setViewportSize({ width: 390, height: 844 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);

    // A separate declared network can place E before A; warehouse letters are not stages.
    await page.goto(process.env.BASE_URL || 'http://localhost:8000/');
    await page.getByLabel('Choose CSV or ZIP files').setInputFiles(path.join(__dirname, '../data/testcases/09_reordered_warehouses.zip'));
    await button('Upload and check').click();
    await button('Calculate plan').click();
    await page.getByRole('img', { name: /Allocation flow/ }).waitFor();
    const reverse = page.getByRole('img', { name: /Allocation flow/ });
    assert.equal(await reverse.locator('path[data-route-from="E"][data-route-to="A"]').getAttribute('data-used'), 'true');
    const eX = await reverse.locator('g').filter({ has: page.locator('title', { hasText: /^Warehouse E ·/ }) }).locator('rect').getAttribute('x');
    const aX = await reverse.locator('g').filter({ has: page.locator('title', { hasText: /^Warehouse A ·/ }) }).locator('rect').getAttribute('x');
    assert.ok(Number(eX) < Number(aX));
    assert.deepEqual(errors, []);
    console.log('PASS: highlighting leaves cost unchanged, manual BD6 costs132 (+30), removal restores102, AE6 costs114, locked review and E→A rendering');
  } finally {
    await browser.close();
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
