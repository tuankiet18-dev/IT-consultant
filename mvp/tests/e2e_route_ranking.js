const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');

async function main() {
  const browser = await chromium.launch({ channel: process.env.BROWSER_CHANNEL });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    const base = process.env.BASE_URL || 'http://localhost:8000';
    const button = name => page.getByRole('button', { name, exact: true });
    await page.goto(base);
    await button('Multi-warehouse example').click();
    const [calculated] = await Promise.all([
      page.waitForResponse(r => /\/scenarios\/\d+\/runs$/.test(r.url()) && r.request().method() === 'POST'),
      button('Calculate plan').click(),
    ]);
    const original = await calculated.json();
    const table = page.getByRole('table', { name: 'Ranked complete routes' });
    await table.waitFor();
    const rows = table.locator('tbody tr');
    assert.equal(await rows.count(), 9);
    assert.deepEqual(await rows.evaluateAll(elements => elements.map(row => Number(row.dataset.costPerPallet))), [7, 10, 12, 12, 14, 15, 15, 15, 16]);
    const row = (a, b) => rows.filter({ has: page.getByRole('button', { name: `Highlight complete route Factory → Warehouse ${a} → Warehouse ${b} → Customer`, exact: true }) });
    assert.match(await row('A', 'D').innerText(), /6 pallets\s+42 cost units/);
    assert.match(await row('B', 'E').innerText(), /6 pallets\s+60 cost units/);
    await page.getByRole('spinbutton', { name: 'Compare quantity (pallets)' }).fill('6');
    await table.getByRole('columnheader', { name: 'Cost for 6 pallets' }).waitFor();
    assert.equal(await row('A', 'D').locator('td').nth(3).innerText(), '42');
    assert.equal(await row('B', 'E').locator('td').nth(3).innerText(), '60');
    const graph = page.getByRole('img', { name: /Allocation flow/ });
    await page.getByRole('checkbox', { name: 'Show unused routes' }).uncheck();
    assert.equal(await graph.locator('rect').count(), 6);
    await row('C', 'F').getByRole('button').click();
    await page.getByRole('button', { name: 'Clear route highlight' }).waitFor();
    assert.equal(await graph.locator('rect').count(), 8);
    assert.equal(await graph.locator('path[data-path-preview="true"]').count(), 3);
    assert.equal(await graph.locator('path[data-route-from="SUP1"][data-route-to="C"]').getAttribute('data-path-preview'), 'true');
    assert.equal(await graph.locator('path[data-route-from="C"][data-route-to="F"]').getAttribute('stroke'), '#D97706');
    assert.equal(await graph.locator('path[data-route-from="F"][data-route-to="Z1"]').getAttribute('data-path-preview'), 'true');
    assert.equal(await graph.locator('path[data-route-from="A"][data-route-to="D"]').getAttribute('data-path-preview'), 'false');
    assert.equal(await graph.locator('g[data-path-preview="true"]').count(), 4);
    await page.getByText('Full-path cost 14 per pallet = 10 freight + 4 handling.', { exact: true }).waitFor();
    if (process.env.SHOTS) {
      fs.mkdirSync(process.env.SHOTS, { recursive: true });
      await page.screenshot({ path: path.join(process.env.SHOTS, 'ranked-route-preview.png'), fullPage: true });
      await page.getByRole('region', { name: 'Complete route cost ranking', exact: true }).screenshot({ path: path.join(process.env.SHOTS, 'route-ranking-table.png') });
      await graph.locator('..').locator('..').screenshot({ path: path.join(process.env.SHOTS, 'selected-path-diagram.png') });
    }
    await button('Clear route highlight').click();
    assert.equal(await graph.locator('path[data-path-preview="true"]').count(), 0);
    await page.getByRole('spinbutton', { name: 'Compare quantity (pallets)' }).fill('12');
    await table.getByRole('columnheader', { name: 'Cost for 12 pallets' }).waitFor();
    assert.equal(await row('A', 'D').locator('td').nth(3).innerText(), 'Exceeds limit');
    assert.equal(await row('B', 'E').locator('td').nth(3).innerText(), '120');
    const unchanged = await (await page.request.get(`${base}/api/runs/${original.id}`)).json();
    assert.equal(unchanged.comparison.optimised.total, 102);
    assert.deepEqual(unchanged.optimised, original.optimised);
    await page.setViewportSize({ width: 390, height: 844 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    assert.deepEqual(errors, []);
    console.log('PASS: nine full paths sorted, 42+60 allocation costs, six/twelve-pallet quotes, exact unused CF highlight, reveal hidden routes and unchanged plan');
  } finally {
    await browser.close();
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
