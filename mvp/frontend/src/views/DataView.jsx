import { useRef, useState } from "react";
import { FileUp, FlaskConical, Loader2, Play, Sparkles } from "lucide-react";
import { useApp } from "../store.jsx";
import { Field, Kpi, Note, PageHead, Section, Tag } from "../components/ui.jsx";
import { fmt } from "../utils";

function Choice({ icon: Icon, title, text, onClick }) {
  return (
    <button type="button" onClick={onClick}
      className="card card-pad group flex cursor-pointer flex-col items-start gap-2 text-left transition-colors duration-200 hover:border-brand-300 hover:bg-brand-50/40">
      <span className="grid h-9 w-9 place-items-center rounded-lg bg-brand-50 text-brand-700"><Icon size={18} aria-hidden="true" /></span>
      <span className="text-base font-semibold text-slate-900">{title}</span>
      <span className="text-sm text-slate-500">{text}</span>
    </button>
  );
}

function Mapping() {
  const { scenario, mapping, suggestMap, confirmMap, toast, ent } = useApp();
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
        Advanced: match products from another catalogue
        <span className="text-xs font-normal text-slate-500 group-open:hidden">Optional</span>
      </summary>
      <div className="border-t border-slate-100 px-5 py-4">
        <p className="hint">Paste one product per line as "code, name". We suggest the closest SKU in this scenario. Nothing changes until you confirm a match.</p>
        <textarea className="input mt-3" value={text} onChange={(e) => setText(e.target.value)} placeholder={"CEM-25, cement standard\nRF-L, roofing sheet large"} />
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
  const { scenario: s, loadSample, upload, runOpt, toast, busy } = useApp();
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
      <PageHead title="Choose the data" lead="Start with an example, or upload your own eight CSV files (as a ZIP or selected together). Everything is checked before any plan is calculated." />
      <div className="grid gap-4 md:grid-cols-3">
        <Choice icon={FlaskConical} title="Synthetic demo" text="2 suppliers, 3 warehouses, 6 zones, 20 SKUs. Same size as the Round 1 pilot." onClick={() => loadSample("demo")} />
        <Choice icon={Sparkles} title="Worked example" text="The small example from the Round 1 proposal: cost falls from 700 to 500." onClick={() => loadSample("golden")} />
        <div className="card card-pad">
          <span className="grid h-9 w-9 place-items-center rounded-lg bg-brand-50 text-brand-700"><FileUp size={18} aria-hidden="true" /></span>
          <div className="mt-2 text-base font-semibold text-slate-900">Upload files</div>
          <input ref={fileRef} type="file" multiple accept=".csv,.zip" aria-label="Choose CSV or ZIP files"
            className="mt-2 block w-full cursor-pointer text-sm text-slate-600 file:mr-3 file:cursor-pointer file:rounded-lg file:border-0 file:bg-slate-100 file:px-3 file:py-2 file:text-sm file:font-medium file:text-slate-700 hover:file:bg-slate-200" />
          <button type="button" className="btn btn-secondary mt-3" onClick={onUpload}>Upload and check</button>
        </div>
      </div>

      {s && (
        <>
          <Section title={s.name}>
            <div className="mb-4"><Tag tone={s.valid ? "good" : "bad"}>{s.valid ? "Valid" : "Has errors"}</Tag></div>
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              <Kpi label="Suppliers" value={s.summary.suppliers} />
              <Kpi label="Warehouses" value={s.summary.warehouses} />
              <Kpi label="Zones" value={s.summary.zones} />
              <Kpi label="SKUs" value={s.summary.skus} />
            </div>
            <p className="hint mt-3">Total demand {fmt(s.summary.demand_pallets)} pallets; total warehouse capacity {fmt(s.summary.capacity_total)} pallet-equivalents per week.</p>
          </Section>

          {s.issues.length === 0 && <Note tone="ok">All data checks passed: no errors and no warnings.</Note>}
          {s.issues.length > 0 && (
            <Section title={`Data checks: ${errs.length} error(s), ${warns.length} warning(s)`}>
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
            <Section title="Calculate the plan" hint="We build the preferred-warehouse baseline and the lowest-cost plan, then check both independently.">
              <div className="card card-pad">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <p className="text-sm text-slate-600">Uses whole pallets and usually takes a few seconds.</p>
                  <button type="button" className="btn btn-primary" disabled={busy} onClick={() => runOpt(mode, tl)}>
                    {busy ? <Loader2 size={16} className="animate-spin" aria-hidden="true" /> : <Play size={16} aria-hidden="true" />} Calculate plan
                  </button>
                </div>
                <details className="mt-4 border-t border-slate-100 pt-3">
                  <summary className="cursor-pointer text-sm font-medium text-slate-600">Advanced settings</summary>
                  <div className="mt-3 grid gap-4 md:grid-cols-2">
                    <Field label="Method">
                      <select className="input" value={mode} onChange={(e) => setMode(e.target.value)}>
                        <option value="milp">Whole pallets (recommended)</option>
                        <option value="lp">Fractional pallets (lower bound)</option>
                      </select>
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
