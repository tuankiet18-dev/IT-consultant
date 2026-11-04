import { AlertTriangle, CheckCircle2, Info, XCircle } from "lucide-react";

export function PageHead({ title, lead, children }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div className="max-w-3xl">
        <h2 className="text-2xl font-semibold text-slate-900">{title}</h2>
        {lead && <p className="mt-1 text-[15px] leading-relaxed text-slate-600">{lead}</p>}
      </div>
      {children && <div className="flex flex-wrap gap-2">{children}</div>}
    </div>
  );
}

export function Section({ title, hint, children, className = "" }) {
  return (
    <section className={"mt-8 " + className}>
      {title && <h3 className="text-base font-semibold text-slate-900">{title}</h3>}
      {hint && <p className="hint mt-0.5">{hint}</p>}
      <div className={title || hint ? "mt-3" : ""}>{children}</div>
    </section>
  );
}

const TAG = {
  neutral: "bg-slate-100 text-slate-700 border-slate-200",
  info: "bg-brand-50 text-brand-800 border-brand-200",
  good: "bg-emerald-50 text-emerald-800 border-emerald-200",
  warn: "bg-amber-50 text-amber-800 border-amber-200",
  bad: "bg-red-50 text-red-800 border-red-200",
};
export function Tag({ tone = "neutral", children, icon: Icon }) {
  return (
    <span className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium ${TAG[tone]}`}>
      {Icon && <Icon size={12} aria-hidden="true" />}
      {children}
    </span>
  );
}

const NOTE = {
  info: ["border-brand-200 bg-brand-50 text-brand-800", Info],
  warn: ["border-amber-200 bg-amber-50 text-amber-900", AlertTriangle],
  ok: ["border-emerald-200 bg-emerald-50 text-emerald-900", CheckCircle2],
  err: ["border-red-200 bg-red-50 text-red-900", XCircle],
};
export function Note({ tone = "info", children }) {
  const [cls, Icon] = NOTE[tone];
  return (
    <div role={tone === "err" ? "alert" : "note"} className={`mt-4 flex gap-3 rounded-lg border px-4 py-3 text-sm leading-relaxed ${cls}`}>
      <Icon size={18} className="mt-0.5 shrink-0" aria-hidden="true" />
      <div>{children}</div>
    </div>
  );
}

export function Kpi({ label, value, sub, tone = "default", big = false }) {
  const valueCls = tone === "good" ? "text-emerald-700" : tone === "bad" ? "text-red-700" : tone === "brand" ? "text-brand-700" : "text-slate-900";
  return (
    <div className={"card card-pad " + (tone === "good" ? "border-emerald-200" : "")}>
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</div>
      <div className={`mt-2 font-semibold leading-none ${big ? "text-4xl" : "text-3xl"} ${valueCls}`}>{value}</div>
      {sub && <div className="mt-2 text-sm text-slate-500">{sub}</div>}
    </div>
  );
}

export function Field({ label, children, className = "" }) {
  return (
    <label className={"block " + className}>
      <span className="label">{label}</span>
      {children}
    </label>
  );
}

export function Legend({ items }) {
  return (
    <ul className="mt-3 flex flex-wrap gap-x-5 gap-y-1 text-sm text-slate-600">
      {items.map(([label, color]) => (
        <li key={label} className="flex items-center gap-2">
          <span className="inline-block h-3 w-3 rounded-sm" style={{ background: color }} aria-hidden="true" />
          {label}
        </li>
      ))}
    </ul>
  );
}

export function RunBanner({ run }) {
  const { fmt } = { fmt: (n) => Number(n).toLocaleString("en-US", { maximumFractionDigits: 0 }) };
  return (
    <>
      {run.kind === "override" && (
        <Note tone="info">
          This run includes {run.pins.length} planner decision(s) fixed by hand. They cost {fmt(run.cost_of_planner_decisions)} cost units more than the unconstrained optimum.
        </Note>
      )}
      {run.kind === "whatif" && <Note tone="info">This is a what-if run on a modified copy of the data.</Note>}
      {run.state !== "draft" && (
        <Note tone={run.state === "approved" ? "ok" : "err"}>This run is {run.state}. It can no longer be changed.</Note>
      )}
    </>
  );
}
