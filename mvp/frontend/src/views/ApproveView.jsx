import { useState } from "react";
import { CheckCircle2, Download, ShieldCheck, XCircle } from "lucide-react";
import { useApp } from "../store.jsx";
import { Field, Note, Section } from "../components/ui.jsx";
import { eventText, fmt, payloadText, solverText, when } from "../utils";

export function DecisionPanel() {
  const { run: r, decide, exportZip, busy } = useApp();
  const [comment, setComment] = useState("");
  const draft = r.state === "draft";
  const c = r.comparison;
  const failed = r.verify.optimised_violations.length > 0;
  return (
    <div>
      <Section title={`Decision on plan ${r.id}`} hint={draft ? "Review the checks, then approve or reject." : r.state === "approved" ? "Approved and ready to export." : "This plan was rejected."}>
        <div className="card card-pad">
          <dl className="grid gap-4 sm:grid-cols-3">
            <div>
              <dt className="label">Plan cost</dt>
              <dd className="text-2xl font-semibold text-slate-900">{fmt(c.optimised.total)}</dd>
            </div>
            <div>
              <dt className="label">Saving against baseline</dt>
              <dd className="text-2xl font-semibold text-slate-900">
                {c.saving == null ? "n/a" : fmt(c.saving)}
                {c.saving != null && <span className="ml-2 text-sm font-normal text-slate-500">{fmt(c.saving_pct, 1)}%</span>}
              </dd>
            </div>
            <div>
              <dt className="label">Plan checks</dt>
              <dd className={"font-semibold " + (failed ? "text-red-700" : "text-emerald-700")}>{failed ? "Failed" : "Passed"}</dd>
              <dd className="mt-1 text-sm text-slate-500">{solverText(r.status)}</dd>
            </div>
          </dl>
          {draft && <>
            <Field label="Comment (required if rejecting)" className="mt-4">
              <input className="input" value={comment} onChange={(e) => setComment(e.target.value)} placeholder="Reviewed cost, capacity and lanes" />
            </Field>
            <div className="mt-4 flex flex-wrap gap-3">
              <button type="button" className="btn btn-success" disabled={busy} onClick={() => decide("approve", comment)}><CheckCircle2 size={16} aria-hidden="true" /> Approve plan</button>
              <button type="button" className="btn btn-danger" disabled={busy} onClick={() => decide("reject", comment)}><XCircle size={16} aria-hidden="true" /> Reject</button>
            </div>
          </>}
          {r.state === "approved" && <div className="mt-4">
            <button type="button" className="btn btn-primary" disabled={busy} onClick={exportZip}>
              <Download size={16} aria-hidden="true" /> Export approved plan (ZIP)
            </button>
          </div>}
        </div>
      </Section>

    </div>
  );
}

export function AuditTrail() {
  const { audit, chain } = useApp();
  return (
    <div>
      <Section>
        {chain && (
          <Note tone={chain.ok ? "ok" : "err"}>
            {chain.ok
              ? <>Audit trail verified ({chain.events} events). Each entry is linked to the one before it, so any edit would be detected. This is tamper-evident, not tamper-proof.</>
              : "Audit verification failed. Review the event history before using this plan."}
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
