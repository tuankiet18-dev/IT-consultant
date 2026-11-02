// Browser walk-through of the whole journey (Playwright). Start the server first: uvicorn api.main:app --port 8765
// Run: NODE_PATH=$(npm root -g) SHOTS=/tmp/shots node tests/e2e_ui.js
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({viewport:{width:1280,height:900}});
  const errors=[]; p.on('pageerror',e=>errors.push('pageerror '+e.message)); p.on('console',m=>{if(m.type()==='error')errors.push('console '+m.text())});
  await p.goto('http://localhost:8765/'); await p.waitForSelector('text=Synthetic demo');
  await p.screenshot({path:(process.env.SHOTS||'shots')+'/1-start.png'});
  await p.click('text=Synthetic demo'); await p.waitForSelector('text=Run optimisation');
  await p.screenshot({path:(process.env.SHOTS||'shots')+'/2-data.png',fullPage:true});
  await p.click('button:has-text("Run optimisation")'); await p.waitForSelector('text=Where the cost sits');
  await p.screenshot({path:(process.env.SHOTS||'shots')+'/3-results.png',fullPage:true});
  await p.click('#steps >> text=Plan'); await p.waitForSelector('text=Inbound flows');
  await p.screenshot({path:(process.env.SHOTS||'shots')+'/4-plan.png',fullPage:true});
  await p.click('#steps >> text=Review & adjust'); await p.waitForSelector('text=Generate summary');
  await p.click('text=Generate summary'); await p.waitForSelector('text=Deterministic summary');
  await p.screenshot({path:(process.env.SHOTS||'shots')+'/5-review.png',fullPage:true});
  await p.click('text=Approve explanation'); await p.waitForSelector('text=Approved by planner');
  // override: take whatever is selected and pin it exactly (current allocation) with a changed warehouse
  await p.fill('#or','Customer contract names this warehouse');
  const opts = await p.$$eval('#ow option', o=>o.map(x=>x.value));
  const cur = await p.inputValue('#ow'); const other = opts.find(x=>x!==cur); await p.selectOption('#ow', other);
  await p.click('text=Apply and re-optimise'); await p.waitForSelector('text=includes 1 planner decision');
  await p.screenshot({path:(process.env.SHOTS||'shots')+'/6-override.png',fullPage:true});
  await p.click('#steps >> text=Approve & audit'); await p.waitForSelector('text=Audit log');
  await p.fill('#dc','Reviewed'); await p.click('button:has-text("Approve plan")'); await p.waitForSelector('text=This run is approved');
  await p.screenshot({path:(process.env.SHOTS||'shots')+'/7-approve.png',fullPage:true});
  const dl = p.waitForEvent('download'); await p.click('text=Export approved plan'); const d = await dl; console.log('download', d.suggestedFilename());
  await p.click('#steps >> text=What-if'); await p.selectOption('#wt','close_warehouse'); await p.click('text=Add change'); await p.click('text=Run what-if'); await p.waitForSelector('text=Result:');
  await p.screenshot({path:(process.env.SHOTS||'shots')+'/8-whatif.png',fullPage:true});
  console.log('errors', JSON.stringify(errors)); await b.close();
})().catch(e=>{console.error('FAIL',e.message);process.exit(1)});
