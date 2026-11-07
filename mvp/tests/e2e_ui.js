// Run against a disposable instance on port 8000, or set BASE_URL.
const assert = require('node:assert/strict');
const path = require('node:path');
const { chromium } = require('playwright');

async function main() {
  const browser = await chromium.launch({ channel: process.env.BROWSER_CHANNEL });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => {
      if (message.type() === 'error') errors.push(message.text());
    });
    const button = name => page.getByRole('button', { name });
    const step = name => page.getByRole('navigation', { name: 'Workflow' })
      .getByRole('button', { name });
    const shot = async name => {
      if (process.env.SHOTS) {
        await page.screenshot({ path: path.join(process.env.SHOTS, name + '.png'), fullPage: true });
      }
    };

    await page.goto(process.env.BASE_URL || 'http://localhost:8000/');
    await button(/^Synthetic demo\b/).waitFor();
    await shot('1-start');
    await button(/^Synthetic demo\b/).click();
    await button('Calculate plan').waitFor();
    await shot('2-data');
    await button('Calculate plan').click();
    await page.getByRole('heading', { name: 'Where the cost sits' }).waitFor();
    await shot('3-results');

    await step('Review & approve').click();
    await button('Write standard summary').click();
    await page.getByText('Standard summary', { exact: true }).waitFor();
    await shot('5-review');
    await button('Approve explanation').click();
    await page.getByText('Approved by planner').waitFor();
    await page.getByText('Adjust plan', { exact: true }).click();
    await button('Change delivery warehouse').click();

    await page.getByRole('combobox', { name: 'Zone', exact: true }).selectOption('Z1');
    await page.getByRole('combobox', { name: 'SKU', exact: true }).selectOption('SKU-01');
    await page.getByText(/^Currently: Warehouse A 8/).waitFor();
    await page.getByRole('combobox', { name: 'Serve from' }).selectOption('WB');
    await page.getByRole('spinbutton', { name: 'Exactly (pallets)' }).fill('8');
    const reason = 'Customer contract names this warehouse';
    await page.getByRole('textbox', { name: 'Reason (required)', exact: true }).fill(reason);
    const [override] = await Promise.all([
      page.waitForResponse(response => response.url().endsWith('/overrides')),
      button('Apply decision and recalculate').click(),
    ]);
    assert.ok(override.ok(), await override.text());
    await page.getByRole('heading', { name: 'Where the cost sits' }).waitFor();
    await step('Review & approve').click();
    await page.getByText(/^Manual decisions \(/).click();
    await page.getByRole('cell', { name: reason }).waitFor();
    await shot('6-override');

    await page.getByRole('textbox', { name: 'Comment (required if rejecting)' }).fill('Reviewed');
    await button('Approve plan').click();
    const exportButton = button('Export approved plan (ZIP)');
    await exportButton.waitFor();
    await shot('7-approve');
    const [download] = await Promise.all([page.waitForEvent('download'), exportButton.click()]);
    assert.match(download.suggestedFilename(), /\.zip$/i);
    assert.equal(await download.failure(), null);

    await step('Audit trail').click();
    await page.getByText('Approved plan exported', { exact: true }).waitFor();
    await step('What-if').click();
    await page.getByRole('combobox', { name: 'Change', exact: true }).selectOption({ label: 'Close a warehouse' });
    await button('Add change').click();
    await button('Run what-if').click();
    await page.getByRole('heading', { name: /^Result:/ }).waitFor();
    await shot('8-whatif');
    assert.deepEqual(errors, [], 'Unexpected browser errors');
    console.log('PASS: demo, explanation, override, approval, ZIP, audit and what-if');
  } finally {
    await browser.close();
  }
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
