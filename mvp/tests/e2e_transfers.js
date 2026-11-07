// Start a disposable MVP server. Set BASE_URL and optionally BROWSER_CHANNEL.
const assert = require('node:assert/strict');
const { chromium } = require('playwright');

async function main() {
  const browser = await chromium.launch({ channel: process.env.BROWSER_CHANNEL });
  try {
    const page = await browser.newPage({ viewport: { width: 1360, height: 1000 } });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => {
      if (message.type() === 'error') errors.push(message.text());
    });
    const button = name => page.getByRole('button', { name, exact: true });
    const step = name => page.getByRole('navigation', { name: 'Workflow' }).getByRole('button', { name });
    await page.goto(process.env.BASE_URL || 'http://localhost:8000/');
    await button('Warehouse transfer chain').click();
    const [calculated] = await Promise.all([
      page.waitForResponse(response => /\/scenarios\/\d+\/runs$/.test(response.url()) && response.request().method() === 'POST'),
      button('Calculate plan').click(),
    ]);
    const run = await calculated.json();
    assert.equal(run.comparison.baseline.total, 210);
    assert.equal(run.comparison.optimised.total, 170);
    const diagram = page.getByRole('img', { name: /Allocation flow/ });
    await diagram.waitFor();
    assert.equal(await diagram.locator('rect').count(), 5);
    assert.equal(await diagram.locator('text').filter({ hasText: /^WAREHOUSES · STAGE/ }).count(), 3);
    await page.getByRole('combobox', { name: 'Highlight a warehouse' }).selectOption('REG');
    await page.getByRole('heading', { name: 'Plan details', exact: true }).click();
    await page.getByRole('heading', { name: 'Warehouse transfers' }).waitFor();
    await step('Review & approve').click();
    await button('Write standard summary').click();
    const text = await page.getByRole('textbox', { name: 'Explanation text' }).inputValue();
    assert.match(text, /Central hub to Regional warehouse/);
    assert.match(text, /Regional warehouse to Local warehouse/);
    await button('Approve explanation').click();
    await page.getByText('Approved by planner', { exact: true }).waitFor();
    await button('Approve plan').click();
    const [download] = await Promise.all([page.waitForEvent('download'), button('Export approved plan (ZIP)').click()]);
    assert.equal(await download.failure(), null);
    await step('What-if').click();
    await page.getByRole('combobox', { name: 'Warehouse', exact: true }).selectOption('REG');
    await button('Add change').click();
    const [changed] = await Promise.all([
      page.waitForResponse(response => response.url().endsWith('/whatif')),
      button('Run what-if').click(),
    ]);
    const result = await changed.json();
    assert.equal(result.comparison.optimised.total, 260);
    assert.deepEqual(result.optimised.transfers, []);
    await page.setViewportSize({ width: 390, height: 844 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    assert.deepEqual(errors, []);
    console.log('PASS: three warehouse stages, grounded summary, approval, export, intermediate closure and mobile layout');
  } finally {
    await browser.close();
  }
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
