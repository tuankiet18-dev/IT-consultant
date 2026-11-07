const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');

async function main() {
  const browser = await chromium.launch({ channel: process.env.BROWSER_CHANNEL });
  try {
    const page = await browser.newPage({ viewport: { width: 1360, height: 1000 } });
    const base = process.env.BASE_URL || 'http://localhost:8000';
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    const button = name => page.getByRole('button', { name, exact: true });
    const step = name => page.getByRole('navigation', { name: 'Workflow' }).getByRole('button', { name, exact: true });
    const shot = async name => {
      if (process.env.SHOTS) {
        fs.mkdirSync(process.env.SHOTS, { recursive: true });
        await page.screenshot({ path: path.join(process.env.SHOTS, name + '.png'), fullPage: true });
      }
    };
    await page.goto(base);
    await step('User guide').click();
    await page.getByRole('heading', { name: 'User guide', exact: true }).waitFor();
    assert.equal(await page.locator('summary').filter({ hasText: /\.csv/ }).count(), 11);
    await page.locator('summary').filter({ hasText: 'direct_rates.csv' }).click();
    await page.getByText('Toàn bộ cước chặng xưởng → khách.', { exact: false }).waitFor();
    await shot('guide-input');
    await button('Testcase mẫu').click();
    const examples = [
      ['10_direct_factory_customer.zip', 0, 70],
      ['11_chain_3_warehouses.zip', 3, 130],
      ['12_chain_4_warehouses.zip', 4, 160],
      ['13_chain_5_warehouses.zip', 5, 190],
      ['14_chain_8_warehouses.zip', 8, 280],
      ['15_chain_12_warehouses.zip', 12, 400],
      ['16_mixed_direct_chain_5.zip', 5, 145],
    ];
    for (const [file] of examples) {
      const response = await page.request.get(`${base}/examples/${file}`);
      assert.equal(response.status(), 200);
      assert.deepEqual(await response.body(), fs.readFileSync(path.join(__dirname, '../data/testcases', file)));
    }
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.getByRole('link', { name: 'Download 10_direct_factory_customer.zip', exact: true }).click(),
    ]);
    assert.equal(await download.failure(), null);
    await shot('guide-samples');
    for (const [file, warehouses, expected] of examples) {
      await page.goto(base);
      await page.getByLabel('Choose CSV or ZIP files').setInputFiles(path.join(__dirname, '../data/testcases', file));
      await button('Upload and check').click();
      const [calculated] = await Promise.all([
        page.waitForResponse(r => /\/scenarios\/\d+\/runs$/.test(r.url()) && r.request().method() === 'POST'),
        button('Calculate plan').click(),
      ]);
      const run = await calculated.json();
      assert.equal(run.comparison.optimised.total, expected);
      const graph = page.getByRole('img', { name: /Allocation flow/ });
      await graph.waitFor();
      assert.equal(await graph.locator('rect').count(), warehouses + 2);
      const table = page.getByRole('table', { name: 'Ranked complete routes' });
      await table.waitFor();
      await table.locator('tbody tr').first().getByRole('button').click();
      assert.equal(await graph.locator('path[data-path-preview="true"]').count(), file.startsWith('16') || warehouses === 0 ? 1 : warehouses + 1);
      await button('Clear route highlight').click();
      if (warehouses === 0) {
        assert.equal(run.optimised.direct[0].pallets, 10);
        assert.equal(run.comparison.optimised.inbound_handling, 0);
        assert.equal(run.comparison.optimised.outbound_handling, 0);
        assert.equal(await graph.locator('path[data-route-kind="Direct delivery"]').count(), 1);
        await shot('direct-results');
        await button('Create manual route').click();
        assert.equal(await page.getByRole('combobox', { name: 'Warehouse stop 1', exact: true }).count(), 0);
        await page.getByRole('spinbutton', { name: 'Route pallets', exact: true }).fill('5');
        await page.getByRole('textbox', { name: 'Route reason (required)' }).fill('Customer requests direct delivery');
        const [saved] = await Promise.all([
          page.waitForResponse(r => /\/runs\/\d+\/routes$/.test(r.url()) && r.request().method() === 'POST'),
          button('Save route and recalculate').click(),
        ]);
        const child = await saved.json();
        assert.equal(child.comparison.optimised.total, 70);
        assert.deepEqual(child.route_pins[0].warehouses, []);
        await button('Review & approve').click();
        await button('Write standard summary').click();
        const text = await page.getByRole('textbox', { name: 'Explanation text' }).inputValue();
        assert.match(text, /direct/i);
        await button('Approve plan').click();
        const [exported] = await Promise.all([page.waitForEvent('download'), button('Export approved plan (ZIP)').click()]);
        assert.equal(await exported.failure(), null);
      }
      if (warehouses === 12) {
        assert.equal(run.optimised.transfers.length, 11);
        assert.equal(await graph.locator('text').filter({ hasText: /^WAREHOUSES · STAGE/ }).count(), 12);
        await shot('twelve-warehouse-results');
      }
      if (file.startsWith('16')) {
        assert.equal(run.optimised.direct[0].pallets, 3);
        const direct = graph.locator('path[data-route-kind="Direct delivery"]');
        assert.match(await direct.getAttribute('d'), / Q /);
        await shot('mixed-direct-warehouse-results');
      }
      await page.setViewportSize({ width: 390, height: 844 });
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      await page.setViewportSize({ width: 1360, height: 1000 });
    }
    assert.deepEqual(errors, []);
    console.log('PASS: guide before loading, eleven CSV contracts, seven downloadable ZIPs, genuine direct delivery/manual/export, 3/4/5/8/12 stages and mobile layout');
  } finally { await browser.close(); }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
