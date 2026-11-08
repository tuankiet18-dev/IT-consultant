import { useState } from "react";
import { Download } from "lucide-react";
import { useApp } from "../store.jsx";
import { PageHead } from "../components/ui.jsx";

const FILES = [
  { name: "suppliers.csv", purpose: "Suppliers and factories", columns: [
    ["supplier_id", "Text", "Unique code, for example SUP1. Use exactly this code in the rate and supply files."],
    ["name", "Text", "Display name of the supplier or factory."],
  ], csv: "supplier_id,name\nSUP1,Factory" },
  { name: "warehouses.csv", purpose: "All existing warehouses, including intermediate ones", columns: [
    ["warehouse_id", "Text", "Unique warehouse code. The letter or number in the code does not decide the order in which goods pass through warehouses."],
    ["name", "Text", "Warehouse name shown in the diagram."],
    ["capacity_pallets", "Number ≥ 0", "Receiving capacity for the planning period, in pallet-equivalents. 0 closes the warehouse. Quantity received × pallet_factor uses this capacity."],
    ["handling_in", "Number ≥ 0", "Fee to receive one pallet at the warehouse, from a supplier or from another warehouse."],
    ["handling_out", "Number ≥ 0", "Fee to dispatch one pallet from the warehouse, to a customer or to another warehouse."],
  ], csv: "warehouse_id,name,capacity_pallets,handling_in,handling_out\nW01,Warehouse 1,10,1,1\nW02,Warehouse 2,10,1,1" },
  { name: "zones.csv", purpose: "Customer zones and the baseline's preferred warehouse", columns: [
    ["zone_id", "Text", "Unique customer zone code, for example Z1."],
    ["name", "Text", "Customer or zone name shown to the planner."],
    ["preferred_warehouse", "Warehouse code", "The final-delivery warehouse that the baseline prefers. It does not force the optimiser to use it. For a zone served only by direct delivery, keep the column and leave the value empty."],
  ], csv: "zone_id,name,preferred_warehouse\nZ1,Customer,W02", note: "Direct-only example: Z1,Customer, (the trailing comma leaves preferred_warehouse empty)." },
  { name: "skus.csv", purpose: "Product catalogue", columns: [
    ["sku_id", "Text", "Unique product code, for example SKU-01."],
    ["name", "Text", "Product name shown to the planner."],
    ["pallet_factor", "Number > 0", "Warehouse capacity used by one pallet of the product. With a factor of 2, receiving 10 pallets uses 20 capacity units at every warehouse it passes through."],
  ], csv: "sku_id,name,pallet_factor\nSKU-01,Example product,1" },
  { name: "inbound_rates.csv", purpose: "Allowed supplier → warehouse lanes", columns: [
    ["supplier_id", "Supplier code", "Refers to suppliers.csv."], ["warehouse_id", "Warehouse code", "Refers to warehouses.csv."],
    ["cost_per_pallet", "Number ≥ 0", "Freight for one pallet on this leg only, before warehouse handling fees."],
  ], csv: "supplier_id,warehouse_id,cost_per_pallet\nSUP1,W01,2" },
  { name: "outbound_rates.csv", purpose: "Allowed warehouse → customer lanes", columns: [
    ["warehouse_id", "Warehouse code", "The warehouse that makes the final delivery."], ["zone_id", "Zone code", "Refers to zones.csv."],
    ["cost_per_pallet", "Number ≥ 0", "Freight for one pallet from the warehouse to the customer zone, before the dispatch fee."],
  ], csv: "warehouse_id,zone_id,cost_per_pallet\nW02,Z1,3" },
  { name: "supply.csv", purpose: "Maximum supply by supplier and product", columns: [
    ["supplier_id", "Supplier code", "Refers to suppliers.csv."], ["sku_id", "Product code", "Refers to skus.csv."],
    ["max_pallets", "Number ≥ 0", "Total the supplier can provide in the period, shared by all routes. With whole pallets, fractional supply is rounded down and a warning is shown."],
  ], csv: "supplier_id,sku_id,max_pallets\nSUP1,SKU-01,10" },
  { name: "demand.csv", purpose: "Customer demand by product", columns: [
    ["zone_id", "Zone code", "Refers to zones.csv."], ["sku_id", "Product code", "Refers to skus.csv."],
    ["pallets", "Number ≥ 0", "Demand that must be fully delivered in the period. Whole pallets needs integers; fractional pallets allows decimals."],
  ], csv: "zone_id,sku_id,pallets\nZ1,SKU-01,10" },
  { name: "transfer_rates.csv", optional: true, purpose: "Warehouse → warehouse lanes (extension for chained warehouses)", columns: [
    ["from_warehouse_id", "Warehouse code", "Dispatching warehouse."], ["to_warehouse_id", "Warehouse code", "Receiving warehouse; must differ from the dispatching one."],
    ["cost_per_pallet", "Number ≥ 0", "Freight for the transfer leg. The system also adds handling_out at the dispatching warehouse and handling_in at the receiving one."],
    ["max_pallets", "Optional: number ≥ 0", "Limit for the lane in the period, summed over all products. Leave the column or cell empty for no lane limit; 0 closes the lane. Warehouse capacity still applies."],
  ], csv: "from_warehouse_id,to_warehouse_id,cost_per_pallet,max_pallets\nW01,W02,1,10", note: "Lanes have a direction. W01 → W02 does not create W02 → W01. The transfer network must not contain loops, even through lanes with max_pallets equal to 0." },
  { name: "direct_rates.csv", optional: true, purpose: "Supplier → customer lanes that skip warehouses (extension)", columns: [
    ["supplier_id", "Supplier code", "Supplier that delivers directly."], ["zone_id", "Zone code", "Customer zone that receives directly."],
    ["cost_per_pallet", "Number ≥ 0", "Full freight of the supplier → customer leg. No handling fee and no warehouse capacity is used."],
    ["max_pallets", "Optional: number ≥ 0", "Limit for the direct lane, shared by all products. Empty or missing means no lane limit; 0 closes it. Supply and demand still limit the quantity."],
  ], csv: "supplier_id,zone_id,cost_per_pallet,max_pallets\nSUP1,Z1,7,10", note: "Without this file, direct delivery is not allowed. A scenario that uses no warehouse must still send all 8 required files; warehouses.csv, inbound_rates.csv and outbound_rates.csv then contain only their header row." },
  { name: "warehouse_skus.csv", optional: true, purpose: "Products each warehouse may receive", columns: [
    ["warehouse_id", "Warehouse code", "Warehouse that may receive the product."], ["sku_id", "Product code", "Allowed product; one pair per row."],
  ], csv: "warehouse_id,sku_id\nW01,SKU-01\nW02,SKU-01", note: "Without the file, every product is allowed at every warehouse. With it, only the listed pairs are allowed, and a warehouse that is left out receives no product. The rule applies at every intermediate warehouse; direct delivery uses no warehouse." },
];

const CASES = [
  ["10_direct_factory_customer.zip", "No warehouse", "Factory → Customer", "70", "70"],
  ["11_chain_3_warehouses.zip", "Through 3 warehouses", "Factory → W01 → W02 → W03 → Customer", "130", "130"],
  ["12_chain_4_warehouses.zip", "Through 4 warehouses", "Factory → W01 → … → W04 → Customer", "160", "160"],
  ["13_chain_5_warehouses.zip", "Through 5 warehouses", "Factory → W01 → … → W05 → Customer", "190", "190"],
  ["14_chain_8_warehouses.zip", "Through 8 warehouses", "Factory → W01 → … → W08 → Customer", "280", "280"],
  ["15_chain_12_warehouses.zip", "Through 12 warehouses", "Factory → W01 → … → W12 → Customer", "400", "400"],
  ["16_mixed_direct_chain_5.zip", "Direct + through 5 warehouses", "3 pallets direct, 7 pallets through W01…W05", "190", "145"],
];

function InputGuide() {
  return <>
    <div className="card card-pad">
      <h3 className="text-lg font-semibold text-slate-900">Format of the files you upload</h3>
      <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm leading-relaxed text-slate-600">
        <li>Send <b>all 8 required CSV files together</b>, or one ZIP that contains them. The 3 optional CSV files below can be added.</li>
        <li>Files must be <b>UTF-8 CSV</b> (with or without BOM), comma-separated, with the exact column names in the first row. Every data row has the same number of cells as the header. Excel .xlsx files are not read directly.</li>
        <li>Decimals use a dot: <code>12.5</code>. Do not add currency units, % signs or thousands separators. Negative numbers, NaN and infinity are not allowed.</li>
        <li>Supplier, warehouse, customer and SKU codes must match across files and are case-sensitive. Each key or lane is declared on one row; missing lanes are never inferred.</li>
        <li>Inside a ZIP, the CSV files sit <b>in the root folder</b>, not inside a subfolder, with no images or reports. File names are exactly as listed below.</li>
        <li>ZIP limits: at most 5,000,000 bytes after extraction in total and 2,000,000 bytes per CSV. All figures belong to the same planning period and the same currency unit.</li>
      </ol>
      <p className="hint mt-3">In Excel, save as CSV UTF-8 (Comma delimited). If your machine writes semicolons, switch to commas. Values that contain a comma go in double quotes, for example <code>SUP1,"Factory, North"</code>.</p>
      <a className="btn btn-secondary mt-4" href="/examples/13_chain_5_warehouses.zip" download><Download size={15} aria-hidden="true" />Download a valid sample set</a>
    </div>
    <div className="mt-5 flex flex-wrap items-center gap-3 text-sm"><b className="text-slate-900">8 required files + 3 optional files</b><span className="text-slate-500">Open a file to see its columns, meaning and an example. The core pilot needs only the 8 required files.</span></div>
    <div className="mt-3 space-y-3">{FILES.map(file => <details key={file.name} className="card">
      <summary className="cursor-pointer px-5 py-4"><code className="text-sm font-semibold text-brand-800">{file.name}</code><span className="ml-3 text-xs text-slate-500">{file.optional ? "Optional" : "Required"}</span><span className="mt-1 block pl-4 text-sm text-slate-600">{file.purpose}</span></summary>
      <div className="border-t border-slate-100 px-5 py-4">
        <div className="overflow-x-auto"><table className="tbl"><thead><tr><th>Column</th><th>Type</th><th>Meaning and rules</th></tr></thead><tbody>{file.columns.map(([name, type, description]) => <tr key={name}><td><code>{name}</code></td><td className="whitespace-nowrap">{type}</td><td>{description}</td></tr>)}</tbody></table></div>
        <p className="mt-4 text-xs font-semibold uppercase tracking-wide text-slate-500">Example CSV content</p>
        <pre className="mt-2 overflow-x-auto rounded-lg bg-slate-900 p-4 text-xs leading-relaxed text-slate-100">{file.csv}</pre>
        {file.note && <p className="mt-3 text-sm leading-relaxed text-amber-900">{file.note}</p>}
      </div>
    </details>)}</div>
    <div className="card card-pad mt-5"><h3 className="font-semibold text-slate-900">How cost is calculated across several warehouses</h3><p className="mt-2 text-sm leading-relaxed text-slate-600">A path through N warehouses has N − 1 transfer legs. Total cost = supplier → first warehouse freight + every warehouse → warehouse freight + last warehouse → customer freight + receiving and dispatch fees at each warehouse. A pallet that passes through 5 warehouses pays receiving and dispatch fees at all 5 and uses receiving capacity at each. The model sets no fixed limit of 3 or 5 warehouses; lanes must connect to the customer and must not form a loop.</p></div>
  </>;
}

function WorkflowGuide() {
  const steps = [
    ["1. Data: load and check", "Choose an example or upload all CSV files or a ZIP, then select Upload and check. Fix errors by file, column and row before you select Calculate plan. Change data reopens the source picker. Whole pallets uses integer quantities only; fractional pallets allows splitting and gives a cost lower bound for the same problem."],
    ["2. Results: read the plan", "The KPIs show total cost, the baseline, the saving and the result of the independent checks. The baseline is a rule that prefers one final-delivery warehouse per zone; it is not Company A's actual plan. OPTIMAL means the plan is proven optimal; FEASIBLE means the best plan found within the time limit. If the baseline cannot serve all demand, no saving is reported."],
    ["3. Diagram and route ranking", "Coloured lines carry goods in this plan, grey dashed lines are unused options and red dashed lines are links that are currently blocked. Width shows pallets, not price. Select a line to see the freight and fees of that leg. The complete route cost ranking prices the whole path from supplier to customer: filter by customer and product, enter a comparison quantity and select a row to highlight that path in amber. Highlighting changes the view only, not the plan."],
    ["4. Create manual route: a human decision", "Opens a focused editor. Choose supplier, customer, product, the warehouses in order (if any), the pallets and a reason. Save route and recalculate creates a child version, keeps the original, optimises the remaining goods and shows the cost difference. Back to Results discards an unsent form. The reserved quantity is a minimum; the rest of the plan may still use the same lanes. Remove the constraint with Remove route constraint."],
    ["5. Change the delivery warehouse", "In Review & approve, open Adjust plan → Change delivery warehouse. Choose Serve from, the pallets and a reason. This fixes the exact quantity delivered from the final warehouse; the system still chooses the upstream suppliers and warehouses."],
    ["6. Review & approve: explain and decide", "Generate explanation writes text from the calculated numbers. When the AI assistant is configured, it rewrites that text in plain language; any figure that is not in the calculated facts causes the draft to be rejected and the standard summary is shown instead. The number check does not guarantee that every interpretation is right, so read it before approving. Approving the explanation and approving the plan are separate actions. Export approved plan (ZIP) appears only after approval; approved and rejected plans are locked. Version history reopens an earlier version with its saved explanation."],
    ["7. What-if and Audit trail", "What-if tests closing a warehouse, changing capacity or changing demand on a copy of the data and compares it with the current plan. Closing a warehouse does not block direct supplier → customer lanes, because they use no warehouse. The audit trail records data loads, calculations, route decisions, approvals and exports, each linked to the previous one (tamper-evident, not tamper-proof). Start a new version recalculates when a locked plan needs to change."],
  ];
  return <div className="space-y-4">{steps.map(([title, description]) => <div className="card card-pad" key={title}><h3 className="font-semibold text-slate-900">{title}</h3><p className="mt-2 text-sm leading-relaxed text-slate-600">{description}</p></div>)}</div>;
}

function SamplesGuide() {
  return <div className="card card-pad"><h3 className="text-lg font-semibold text-slate-900">Extended test cases, ready to upload</h3><p className="mt-2 text-sm leading-relaxed text-slate-600">These cases go beyond the Round 1 pilot, which has one supplier tier, existing warehouses and customer zones. They show optional lanes for chained warehouses and direct delivery. Each ZIP contains a complete set of CSV files in the root folder. Download one, then go to Data → Change data → Upload files → Upload and check → Calculate plan. All use 10 pallets, pallet_factor = 1 and synthetic costs, so results can be checked by hand.</p>
    <div className="mt-4 overflow-x-auto"><table className="tbl"><thead><tr><th>Case</th><th>Route</th><th className="num">Baseline</th><th className="num">Optimum</th><th /></tr></thead><tbody>{CASES.map(([file, title, route, baseline, optimum]) => <tr key={file}><td className="font-medium">{title}</td><td>{route}</td><td className="num">{baseline}</td><td className="num">{optimum}</td><td><a className="text-brand-800 underline" href={`/examples/${file}`} download aria-label={`Download ${file}`}>Download ZIP</a></td></tr>)}</tbody></table></div>
    <p className="mt-4 text-sm leading-relaxed text-slate-600">For a chain of N warehouses: first leg 2, each transfer 1, last leg 3, each warehouse receives at 1 and dispatches at 1, so one pallet costs 3N + 4. With 5 warehouses: 19 × 10 = 190. The mixed case has a direct lane at 4 per pallet limited to 3 pallets, so 3 × 4 + 7 × 19 = 145. All figures are synthetic cost units.</p>
  </div>;
}

function QuestionsGuide() {
  const questions = [
    ["Why can't the plan be calculated?", "Check that all files are loaded with the right column names and reference codes. Red errors block the run; warnings should be read. Data that is valid in format can still have no plan that meets supply, demand and capacity. The system then says the plan is infeasible; it never invents routes or freight."],
    ["Why doesn't the cheapest route carry everything?", "Warehouses, lanes and supply have shared limits. The ranking gives the full-path cost per pallet; Standalone limit is the limit if that path were used alone. Exceeds limit means the comparison quantity is above it. The optimiser may need to split goods over several paths to reach the lowest total cost."],
    ["Do warehouse names fix the order?", "No. E → A is possible if the input declares every leg. A loop such as A → E → A is not supported. All legs happen within one planning period; delivery schedules, stock carried between periods and travel time are not modelled."],
    ["Where do internal prices or partner preferences go?", "Real prices go in cost_per_pallet of the matching lane, then upload the new data. A decision to use a route because of a relationship or contract is entered in Create manual route with a reason. The reason does not create a discount by itself."],
    ["Does the system know which physical pallet takes which path?", "No. The MVP calculates total flow by product. Where goods merge or split across warehouses, the plan breakdown is one way of decomposing cost for explanation; it does not identify individual pallets. Manual routes are reserved before the rest is decomposed."],
    ["Can I upload one CSV to change one rate?", "Each upload is a new scenario, so send the full set of 8 required files and any optional files you use. You can edit a rate inside a downloaded sample ZIP, compress it with the same structure and upload it."],
  ];
  return <div className="space-y-3">{questions.map(([question, answer]) => <details className="card" key={question}><summary className="cursor-pointer px-5 py-4 text-sm font-semibold text-slate-900">{question}</summary><p className="border-t border-slate-100 px-5 py-4 text-sm leading-relaxed text-slate-600">{answer}</p></details>)}</div>;
}

export default function GuideView() {
  const { go } = useApp();
  const [tab, setTab] = useState("input");
  const tabs = [["input", "Input format"], ["workflow", "How to use"], ["samples", "Extended test cases"], ["questions", "FAQ"]];
  return <div>
    <PageHead title="User guide" lead="How to prepare data and use Nordic Flow."><button type="button" className="btn btn-secondary" onClick={() => go("data")}>Go to Data</button></PageHead>
    <nav className="mb-5 flex flex-wrap gap-2" aria-label="Guide sections">{tabs.map(([id, label]) => <button type="button" key={id} aria-pressed={tab === id} className={`btn ${tab === id ? "btn-primary" : "btn-secondary"}`} onClick={() => setTab(id)}>{label}</button>)}</nav>
    {tab === "input" ? <InputGuide /> : tab === "workflow" ? <WorkflowGuide /> : tab === "samples" ? <SamplesGuide /> : <QuestionsGuide />}
  </div>;
}
