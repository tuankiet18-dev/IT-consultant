import { useRef, useState } from "react";
import { ArrowRight, FileUp, FlaskConical, Loader2, Network, Play, Sparkles } from "lucide-react";
import { useApp } from "../store.jsx";
import { Field, Kpi, Note, PageHead, Section, Tag } from "../components/ui.jsx";
import { fmt } from "../utils";
import BranchingNetwork from "../components/BranchingNetwork.jsx";

function Choice({ icon: Icon, title, text, onClick }) {
  return (
    <button type="button" aria-label={title} onClick={onClick}
      className="card card-pad group flex cursor-pointer flex-col items-start gap-2 text-left transition-colors duration-200 hover:border-brand-300 hover:bg-brand-50/40">
      <span className="grid h-9 w-9 place-items-center rounded-lg bg-brand-50 text-brand-700"><Icon size={18} aria-hidden="true" /></span>
      <span className="text-base font-semibold text-slate-900">{title}</span>
      <span className="text-sm text-slate-500">{text}</span>
    </button>
  );
}

function Mapping() {
  const { mapping, suggestMap, confirmMap, toast, ent } = useApp();
  const [text, setText] = useState("");
  const [llm, setLlm] = useState(false);
  const submit = () => {
    const lines = text.split("\n").map((l) => l.trim()).filter(Boolean);
    if (!lines.length) return toast("Paste at least one line", true);
    const items = lines.map((l) => { const [code, ...rest] = l.split(","); return rest.length ? { code: code.trim(), name: rest.join(",").trim() } : { code: "", name: code.trim() }; });
    suggestMap(items, llm);
  };
  return (
    <details className="card group mt-8">
      <summary className="flex cursor-pointer list-none items-center justify-between px-5 py-4 text-sm font-semibold text-slate-900">
        Match products from another catalogue
        <span className="text-xs font-normal text-slate-500 group-open:hidden">Optional</span>
      </summary>
      <div className="border-t border-slate-100 px-5 py-4">
        <p className="hint">Enter one product per line as code, name. Review and confirm each suggested match.</p>
        <textarea aria-label="Products to match" className="input mt-3" value={text} onChange={(e) => setText(e.target.value)} placeholder={"CEM-25, cement standard\nRF-L, roofing sheet large"} />
        <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
          <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-700">
            <input type="checkbox" checked={llm} onChange={(e) => setLlm(e.target.checked)} className="h-4 w-4 accent-brand-600" /> Ask the AI assistant to help
          </label>
          <button type="button" className="btn btn-secondary" onClick={submit}>Suggest matches</button>
        </div>
        {mapping && (
          <div className="mt-4 overflow-x-auto">
            <table className="tbl">
              <thead><tr><th>Your product</th><th>Closest matches</th><th>AI suggestion</th><th /></tr></thead>
              <tbody>
                {mapping.map((m, i) => (
                  <tr key={i}>
                    <td>{(m.external.code || "") + " " + m.external.name}</td>
                    <td>{m.candidates.map((c) => <div key={c.sku_id}>{c.name} <Tag tone={c.confidence > 0.75 ? "good" : "warn"}>{c.confidence.toFixed(2)}</Tag></div>)}</td>
                    <td>{m.llm_pick ? `${ent.sku(m.llm_pick.sku_id)}: ${m.llm_pick.reason || ""}` : "–"}</td>
                    <td>{m.confirmed ? <Tag tone="good">Confirmed</Tag> : <button type="button" className="btn btn-secondary" onClick={() => confirmMap(i)}>Confirm best match</button>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </details>
  );
}

export default function DataView() {
  const { scenario: s, loadSample, upload, runOpt, toast, busy, go } = useApp();
  const fileRef = useRef(null);
  const [mode, setMode] = useState("milp");
  const [tl, setTl] = useState(30);
  const onUpload = () => {
    const f = fileRef.current.files;
    if (!f.length) return toast("Choose files first", true);
    upload(f);
  };
  const errs = s ? s.issues.filter((i) => i.severity === "error") : [];
  const warns = s ? s.issues.filter((i) => i.severity === "warning") : [];
  return (
    <div>
      <PageHead title={s ? "Check the data" : "Choose the data"} lead={s ? "Review the checks, then calculate the plan." : "Load an example or upload your scenario CSVs or ZIP."}><button type="button" className="btn btn-secondary" onClick={() => go("guide")}>Input format guide</button></PageHead>
      {!s && (
        <div className="mb-6 flex flex-wrap items-center gap-x-4 gap-y-2 rounded-xl border border-slate-200 bg-white px-5 py-4 text-sm text-slate-600" aria-label="Planning steps">
          <span><b className="text-slate-900">1</b> Load & check data</span><ArrowRight size={16} aria-hidden="true" />
          <span><b className="text-slate-900">2</b> Compare allocations</span><ArrowRight size={16} aria-hidden="true" />
          <span><b className="text-slate-900">3</b> Review & export</span>
        </div>
      )}
      <details key={s ? s.id : "initial-source-picker"} open={!s} className={s ? "mb-6 rounded-lg border border-slate-200 bg-white" : ""}>
        <summary className={s ? "flex cursor-pointer items-center justify-between gap-3 px-4 py-3 text-sm font-semibold text-slate-800" : "sr-only"}>
          Change data
          {s && <span className="text-xs font-normal text-slate-500">Examples or upload</span>}
        </summary>
        <div className={s ? "border-t border-slate-100 p-4" : ""}>
          <div className="grid gap-4 md:grid-cols-2">
            <Choice icon={FlaskConical} title="Synthetic demo" text="Pilot scale: 2 suppliers, 3 existing warehouses, 6 customer zones and 20 products." onClick={() => loadSample("demo")} />
            <Choice icon={Sparkles} title="Worked example" text="A small allocation with 2 warehouses and 1 product, easy to check by hand." onClick={() => loadSample("golden")} />
            <details className="card md:col-span-2">
              <summary className="flex cursor-pointer items-center justify-between gap-3 px-5 py-4 text-sm font-semibold text-slate-900">
                Extended network examples
                <span className="text-xs font-normal text-slate-500">Optional, beyond the Round 1 pilot</span>
              </summary>
              <div className="border-t border-slate-100 p-4">
                <p className="hint mb-3">The pilot needs only suppliers, existing warehouses and customer zones. These examples add optional transfers between existing warehouses.</p>
                <div className="grid gap-4 md:grid-cols-2">
                  <Choice icon={Network} title="Multi-warehouse example" text="Compare 3 receiving warehouses and 3 delivery warehouses across 9 transfer routes." onClick={() => loadSample("branching")} />
                  <Choice icon={Network} title="Warehouse transfer chain" text="Trace goods through 3 warehouses in sequence before customer delivery." onClick={() => loadSample("transshipment")} />
                </div>
              </div>
            </details>
            <div className="card card-pad md:col-span-2">
              <span className="grid h-9 w-9 place-items-center rounded-lg bg-brand-50 text-brand-700"><FileUp size={18} aria-hidden="true" /></span>
              <div className="mt-2 text-base font-semibold text-slate-900">Upload files</div>
              <p className="mt-1 text-sm text-slate-500">Select all scenario CSVs together, or one ZIP.</p>
              <input ref={fileRef} type="file" multiple accept=".csv,.zip" aria-label="Choose CSV or ZIP files"
                className="mt-2 block w-full cursor-pointer text-sm text-slate-600 file:mr-3 file:cursor-pointer file:rounded-lg file:border-0 file:bg-slate-100 file:px-3 file:py-2 file:text-sm file:font-medium file:text-slate-700 hover:file:bg-slate-200" />
              <button type="button" className="btn btn-secondary mt-3" disabled={busy} onClick={onUpload}>Upload and check</button>
              <details className="mt-3 text-xs text-slate-500">
                <summary className="cursor-pointer">Required files</summary>
                <p className="mt-2 leading-relaxed">suppliers.csv, warehouses.csv, zones.csv, skus.csv, inbound_rates.csv, outbound_rates.csv, supply.csv, demand.csv</p>
                <p className="mt-2 font-medium text-slate-700">Optional extensions beyond the Round 1 pilot: warehouse transfers and direct delivery</p>
                <p className="mt-1 leading-relaxed">transfer_rates.csv links warehouses using from_warehouse_id, to_warehouse_id and cost_per_pallet. The optional max_pallets column limits the route across all products. A blank limit allows any quantity within warehouse capacity. Zero closes that route.</p>
                <p className="mt-2 leading-relaxed">List every warehouse in warehouses.csv. Transfer routes must move forward through an acyclic network. warehouse_skus.csv can restrict which products each warehouse accepts.</p>
                <p className="mt-2 leading-relaxed">For factory-to-customer delivery without a warehouse, add direct_rates.csv with supplier_id, zone_id, cost_per_pallet and optional max_pallets. See Input format guide for the complete contract.</p>
              </details>
            </div>
          </div>
        </div>
      </details>

      {s && (
        <>
          <Section title={s.source === "sample:golden" ? "Worked example" : s.source === "sample:branching" ? "Multi-warehouse example" : s.source === "sample:transshipment" ? "Warehouse transfer chain" : s.name}>
            <div className="mb-4"><Tag tone={s.valid ? "good" : "bad"}>{s.valid ? "Valid" : "Has errors"}</Tag></div>
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              <Kpi label="Suppliers" value={s.summary.suppliers} />
              <Kpi label="Warehouses" value={s.summary.warehouses} />
              <Kpi label="Zones" value={s.summary.zones} />
              <Kpi label="SKUs" value={s.summary.skus} />
            </div>
            <div className="mt-3 flex flex-wrap gap-x-6 gap-y-1 text-sm text-slate-600">
              <span>Demand <b className="text-slate-900">{fmt(s.summary.demand_pallets)} pallets</b></span>
              <span>Weekly handling capacity <b className="text-slate-900">{fmt(s.summary.capacity_total)} pallet-equivalents</b></span>
              {s.summary.transfer_lanes > 0 && <span>Transfer routes <b className="text-slate-900">{s.summary.transfer_lanes}</b></span>}
              {s.summary.direct_lanes > 0 && <span>Factory-to-customer routes <b className="text-slate-900">{s.summary.direct_lanes}</b></span>}
            </div>
            {s.source === "sample:transshipment" && <p className="hint mt-2">Each visited warehouse uses handling capacity. Costs include every transfer and handling step.</p>}
            {s.source === "sample:branching" && <BranchingNetwork scenario={s} />}
          </Section>

          {s.issues.length === 0 && <Note tone="ok">All data checks passed: no errors and no warnings.</Note>}
          {s.issues.length > 0 && (
            <Section title={`Data checks · ${errs.length} error(s), ${warns.length} warning(s)`}>
              <div className="card overflow-x-auto">
                <table className="tbl">
                  <thead><tr><th>Severity</th><th>File</th><th>Row</th><th>Message</th></tr></thead>
                  <tbody>
                    {s.issues.map((i, k) => (
                      <tr key={k}><td><Tag tone={i.severity === "error" ? "bad" : "warn"}>{i.severity}</Tag></td><td>{i.file}</td><td>{i.row ?? ""}</td><td>{i.message}</td></tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {errs.length > 0 && <Note tone="err">Errors block the run. Fix the files and upload them again.</Note>}
            </Section>
          )}

          {s.valid && (
            <Section title="Calculate the plan">
              <div className="card card-pad">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <p className="text-sm text-slate-600">{mode === "milp" ? "Whole-pallet allocation" : "Fractional-pallet allocation"} · Compared with the preferred-warehouse baseline</p>
                  <button type="button" className="btn btn-primary" disabled={busy} onClick={() => runOpt(mode, tl)}>
                    {busy ? <Loader2 size={16} className="animate-spin" aria-hidden="true" /> : <Play size={16} aria-hidden="true" />} Calculate plan
                  </button>
                </div>
                <details className="mt-4 border-t border-slate-100 pt-3">
                  <summary className="cursor-pointer text-sm font-medium text-slate-600">Advanced settings</summary>
                  <div className="mt-3 grid gap-4 md:grid-cols-2">
                    <Field label="Method">
                      <select className="input" aria-describedby="allocation-method-help" value={mode} onChange={(e) => setMode(e.target.value)}>
                        <option value="milp">Whole pallets (recommended)</option>
                        <option value="lp">Fractional pallets (lower bound)</option>
                      </select>
                      <p id="allocation-method-help" className="mt-2 text-xs leading-relaxed text-slate-500">{mode === "milp" ? "Uses whole pallets only, such as 6 or 7. Choose this when pallets must stay intact." : "Allows fractions such as 6.5 pallets. The minimum cost is a lower bound for the same whole-pallet problem and may require splitting pallets."}</p>
                    </Field>
                    <Field label="Time limit (seconds)">
                      <input className="input" type="number" min={1} max={300} value={tl} onChange={(e) => setTl(+e.target.value)} />
                    </Field>
                  </div>
                </details>
              </div>
            </Section>
          )}
          <Mapping />
        </>
      )}
    </div>
  );
}
