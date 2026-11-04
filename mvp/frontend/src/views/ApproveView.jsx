import { useState } from "react";
import { CheckCircle2, Download, ShieldCheck, XCircle } from "lucide-react";
import { useApp } from "../store.jsx";
import { Field, Note, Section } from "../components/ui.jsx";
import { eventText, fmt, payloadText, solverText, when } from "../utils";

export function DecisionPanel() {
  const { run: r, decide, exportZip } = useApp();
  const [comment, setComment] = useState("");
  const draft = r.state === "draft";
  const c = r.comparison;
  const failed = r.verify.optimised_violations.length > 0;
  return (
    <div>
      <Section title={`Decision on plan ${r.id}`} hint="Nothing is executed by Nordic Flow. An approved plan is exported for the existing ERP, WMS and TMS.">
        <div className="card card-pad">
          <p className="text-[15px] text-slate-700">
            Optimised cost <b className="text-slate-900">{fmt(c.optimised.total)}</b>
            {c.saving != null ? `, saving ${fmt(c.saving)} (${fmt(c.saving_pct, 1)}%)` : ", no saving reported"} · {solverText(r.status).toLowerCase()} · checks {failed ? "failed" : "passed"}
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

    </div>
  );
}

export function AuditTrail() {
  const { audit, chain } = useApp();
  return (
    <div>
      <Section title="Audit trail" hint="Who did what, and when, for this scenario.">
        {chain && (
          <Note tone={chain.ok ? "ok" : "err"}>
            {chain.ok
              ? <><ShieldCheck size={14} className="mr-1 inline" aria-hidden="true" />Audit trail verified ({chain.events} events). Each entry is linked to the one before it, so any edit would be detected. This is tamper-evident, not tamper-proof.</>
              : "The audit trail failed verification. Entries may have been changed."}
          </Note>
        )}
        <ol className="card mt-4 divide-y divide-slate-100">
          {audit.map((a, i) => (
            <li key={i} className="px-5 py-3 text-sm">
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <span className="font-medium text-slate-900">{eventText(a.type)}</span>
                <span className="text-xs text-slate-500">{a.actor} · {when(a.ts)}</span>
              </div>
              <details className="mt-1">
                <summary className="cursor-pointer text-xs text-slate-500">Details</summary>
                <p className="mt-1 break-words font-mono text-xs text-slate-500">{payloadText(a.payload)} #{a.hash}</p>
              </details>
            </li>
          ))}
          {!audit.length && <li className="px-5 py-6 text-center text-sm text-slate-500">No events yet.</li>}
        </ol>
      </Section>
    </div>
  );
}
