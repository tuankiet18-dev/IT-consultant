import { useState } from "react";
import { CheckCircle2, Download, ShieldCheck, XCircle } from "lucide-react";
import { useApp } from "../store.jsx";
import { Field, Note, PageHead, RunBanner, Section } from "../components/ui.jsx";
import { fmt, payloadText } from "../utils";

export default function ApproveView() {
  const { run: r, audit, chain, decide, exportZip } = useApp();
  const [comment, setComment] = useState("");
  const draft = r.state === "draft";
  const c = r.comparison;
  const failed = r.verify.optimised_violations.length > 0;
  return (
    <div>
      <PageHead title="Approve & audit" lead="Nothing is executed by Nordic Flow. An approved plan is exported for the existing ERP, WMS and TMS." />
      <RunBanner run={r} />

      <Section title={`Decision on run ${r.id}`}>
        <div className="card card-pad">
          <p className="text-[15px] text-slate-700">
            Optimised cost <b className="text-slate-900">{fmt(c.optimised.total)}</b>
            {c.saving != null ? `, saving ${fmt(c.saving)} (${fmt(c.saving_pct, 1)}%)` : ", no saving reported"} · solver {r.status} · checks {failed ? "failed" : "passed"}
          </p>
          <Field label="Comment (required if rejecting)" className="mt-4">
            <input className="input" value={comment} onChange={(e) => setComment(e.target.value)} placeholder="Reviewed cost, capacity and lanes" disabled={!draft} />
          </Field>
          <div className="mt-4 flex flex-wrap gap-3">
            <button type="button" className="btn btn-success" disabled={!draft} onClick={() => decide("approve", comment)}><CheckCircle2 size={16} aria-hidden="true" /> Approve plan</button>
            <button type="button" className="btn btn-danger" disabled={!draft} onClick={() => decide("reject", comment)}><XCircle size={16} aria-hidden="true" /> Reject</button>
            <button type="button" className="btn btn-secondary" disabled={r.state !== "approved"} title={r.state === "approved" ? "" : "Only approved plans can be exported"} onClick={exportZip}>
              <Download size={16} aria-hidden="true" /> Export approved plan (ZIP)
            </button>
          </div>
        </div>
      </Section>

      <Section title="Audit log for this scenario">
        {chain && (
          <Note tone={chain.ok ? "ok" : "err"}>
            {chain.ok
              ? <><ShieldCheck size={14} className="mr-1 inline" aria-hidden="true" />Event chain verified ({chain.events} events). Each event includes a hash of the one before it, so edits are detectable. This is tamper-evident, not tamper-proof.</>
              : `Chain broken at event ${chain.broken_at_event}.`}
          </Note>
        )}
        <ol className="card mt-4 divide-y divide-slate-100">
          {audit.map((a, i) => (
            <li key={i} className="grid gap-1 px-5 py-3 text-sm md:grid-cols-[170px_220px_1fr] md:gap-4">
              <span className="font-mono text-xs text-slate-500">{a.ts.replace("T", " ").replace("+00:00", " UTC")}</span>
              <span className="font-medium capitalize text-slate-900">{a.type.replaceAll("_", " ").toLowerCase()} · {a.actor}</span>
              <span className="break-words font-mono text-xs text-slate-500">{payloadText(a.payload) + "  #" + a.hash}</span>
            </li>
          ))}
          {!audit.length && <li className="px-5 py-6 text-center text-sm text-slate-500">No events yet.</li>}
        </ol>
      </Section>
    </div>
  );
}
