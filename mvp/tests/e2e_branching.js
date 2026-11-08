// Use a disposable MVP server; BASE_URL, BROWSER_CHANNEL and SHOTS are optional.
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
    await page.goto(process.env.BASE_URL || 'http://localhost:8000/');
    await page.getByText('Extended network examples').click();
    await button('Multi-warehouse example').click();
    const available = page.getByRole('img', { name: /^Available routes:/ });
    await available.waitFor();
    assert.equal(await available.locator('rect').count(), 8);
    assert.equal(await available.locator('path').filter({ has: page.locator('title') }).count(), 15);
    await page.getByText('Orange border marks a warehouse', { exact: false }).waitFor();
    await page.getByText('Advanced settings', { exact: true }).click();
    const method = page.getByRole('combobox', { name: 'Method' });
    await method.selectOption('lp');
    await page.getByText('Allows fractions such as 6.5 pallets.', { exact: false }).waitFor();
    await method.selectOption('milp');
    await page.getByText('Uses whole pallets only', { exact: false }).waitFor();
    if (process.env.SHOTS) {
      fs.mkdirSync(process.env.SHOTS, { recursive: true });
      await page.screenshot({ path: path.join(process.env.SHOTS, 'branching-data.png'), fullPage: true });
    }
    await page.setViewportSize({ width: 390, height: 844 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    await page.setViewportSize({ width: 1360, height: 1000 });
    const [calculated] = await Promise.all([
      page.waitForResponse(r => /\/scenarios\/\d+\/runs$/.test(r.url()) && r.request().method() === 'POST'),
      button('Calculate plan').click(),
    ]);
    const run = await calculated.json();
    assert.equal(run.comparison.baseline.total, 168);
    assert.equal(run.comparison.optimised.total, 102);
    assert.deepEqual(run.optimised.transfers.map(r => [r.from_warehouse, r.to_warehouse, r.pallets]), [['A', 'D', 6], ['B', 'E', 6]]);
    const chosen = page.getByRole('img', { name: /Allocation flow/ });
    await chosen.waitFor();
    assert.equal(await chosen.locator('rect').count(), 8);
    assert.equal(await chosen.locator('path[data-route-kind]').count(), 15);
    assert.equal(await chosen.locator('path[data-route-kind="Warehouse transfer"]').count(), 9);
    assert.equal(await chosen.locator('path[data-used="true"]').count(), 6);
    const route = (a, b) => chosen.locator(`path[data-route-from="${a}"][data-route-to="${b}"]`);
    assert.equal(await route('B', 'D').getAttribute('data-used'), 'false');
    assert.equal(await route('B', 'D').getAttribute('data-available'), 'true');
    assert.equal(await route('B', 'D').getAttribute('stroke-dasharray'), '5 5');
    await route('B', 'D').focus();
    await route('B', 'D').press('Enter');
    await page.getByText('Warehouse B → Warehouse D', { exact: true }).waitFor();
    await page.getByText('This leg costs 6 per pallet including handling.', { exact: false }).waitFor();
    const showUnused = page.getByRole('checkbox', { name: 'Show unused routes' });
    await showUnused.uncheck();
    assert.equal(await chosen.locator('rect').count(), 6);
    assert.equal(await chosen.locator('path[data-route-kind]').count(), 6);
    await showUnused.check();
    await page.getByRole('combobox', { name: 'Highlight a warehouse' }).selectOption('D');
    assert.equal(await route('A', 'D').getAttribute('opacity'), '0.85');
    assert.equal(await route('B', 'E').getAttribute('opacity'), '0.18');
    assert.equal(await route('B', 'D').getAttribute('data-used'), 'false');
    await page.getByRole('combobox', { name: 'Highlight a warehouse' }).selectOption('');
    await page.setViewportSize({ width: 390, height: 844 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    await page.setViewportSize({ width: 1360, height: 1000 });
    if (process.env.SHOTS) await page.screenshot({ path: path.join(process.env.SHOTS, 'branching-results.png'), fullPage: true });
    await page.getByRole('navigation', { name: 'Workflow' }).getByRole('button', { name: 'Review & approve' }).click();
    await button('Generate explanation').click();
    const text = await page.getByRole('textbox', { name: 'Explanation text' }).inputValue();
    assert.match(text, /Warehouse A to Warehouse D/);
    assert.match(text, /Warehouse B to Warehouse E/);
    await page.getByRole('navigation', { name: 'Workflow' }).getByRole('button', { name: 'What-if' }).click();
    await page.getByRole('combobox', { name: 'Warehouse', exact: true }).selectOption('D');
    await button('Add change').click();
    await button('Run what-if').click();
    await button('View full results').click();
    await chosen.waitFor();
    assert.equal(await route('B', 'D').getAttribute('data-available'), 'false');
    assert.equal(await route('B', 'D').getAttribute('stroke'), '#DC2626');
    assert.equal(await route('B', 'E').getAttribute('data-used'), 'true');
    assert.deepEqual(errors, []);
    console.log('PASS: methods explained, 15 declared routes, 6 selected, unused B→D costs, hide/trace controls, closure availability and mobile layout');
  } finally {
    await browser.close();
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
