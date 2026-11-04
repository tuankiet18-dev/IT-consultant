import { BarChart3, Boxes, ClipboardCheck, Database, FlaskConical, Loader2, ShieldCheck } from "lucide-react";
import { useApp } from "./store.jsx";
import { Tag } from "./components/ui.jsx";
import { solverText, stateText } from "./utils";
import DataView from "./views/DataView.jsx";
import ResultsView from "./views/ResultsView.jsx";
import ReviewView from "./views/ReviewView.jsx";
import WhatIfView from "./views/WhatIfView.jsx";
import AuditView from "./views/AuditView.jsx";

const STEPS = [
  { id: "data", label: "Data", icon: Database, view: DataView },
  { id: "results", label: "Results", icon: BarChart3, view: ResultsView },
  { id: "review", label: "Review & approve", icon: ClipboardCheck, view: ReviewView },
  { id: "audit", label: "Audit trail", icon: ShieldCheck, view: AuditView },
  { id: "whatif", label: "What-if", icon: FlaskConical, view: WhatIfView },
];

function StatusStrip() {
  const { config, run } = useApp();
  const ai = config && config.llm_enabled;
  return (
    <div className="flex flex-wrap items-center gap-2">
      <Tag tone="warn">Synthetic data</Tag>
      <span className="hidden sm:inline-flex"><Tag tone={ai ? "good" : "neutral"}>{config == null ? "AI: checking" : ai ? "AI assistant on" : "AI assistant off"}</Tag></span>
      {run && <Tag tone={run.state === "approved" ? "good" : run.state === "rejected" ? "bad" : "info"}>Plan {run.id} · {stateText(run.state)}</Tag>}
    </div>
  );
}

function NavItem({ step, index, active, disabled, onClick, compact }) {
  const Icon = step.icon;
  return (
    <button
      type="button" disabled={disabled} onClick={onClick} aria-current={active ? "page" : undefined}
      className={
        "flex cursor-pointer items-center gap-3 rounded-lg text-sm font-medium transition-colors duration-200 disabled:cursor-not-allowed disabled:opacity-40 " +
        (compact ? "shrink-0 px-3 py-2 " : "w-full px-3 py-2.5 ") +
        (active ? "bg-brand-50 text-brand-800" : "text-slate-600 hover:bg-slate-100")
      }
    >
      <span className={"grid h-6 w-6 shrink-0 place-items-center rounded-md text-xs " + (active ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-600")}>
        {index + 1}
      </span>
      <Icon size={16} aria-hidden="true" className="hidden shrink-0 sm:block" />
      <span className="whitespace-nowrap">{step.label}</span>
    </button>
  );
}

function Toasts() {
  const { toasts } = useApp();
  return (
    <div className="fixed bottom-5 right-5 z-50 flex max-w-sm flex-col gap-2" aria-live="polite">
      {toasts.map((t) => (
        <div key={t.id} className={"rounded-lg px-4 py-3 text-sm text-white shadow-lg " + (t.err ? "bg-red-600" : "bg-slate-900")}>{t.msg}</div>
      ))}
    </div>
  );
}

export default function App() {
  const { tab, go, run, scenario, busy } = useApp();
  const current = STEPS.find((s) => s.id === tab) || STEPS[0];
  const View = current.view;
  return (
    <div className="min-h-screen lg:flex">
      <aside className="hidden w-64 shrink-0 flex-col border-r border-slate-200 bg-white lg:fixed lg:inset-y-0 lg:flex">
        <div className="flex items-center gap-3 px-5 py-5">
          <span className="grid h-9 w-9 place-items-center rounded-lg bg-brand-600 text-white"><Boxes size={20} aria-hidden="true" /></span>
          <div>
            <div className="text-base font-semibold leading-tight text-slate-900">Nordic Flow</div>
            <div className="text-xs text-slate-500">Warehouse allocation</div>
          </div>
        </div>
        <nav aria-label="Workflow" className="flex-1 space-y-1 px-3 py-2">
          {STEPS.map((s, i) => (
            <NavItem key={s.id} step={s} index={i} active={tab === s.id} disabled={s.id !== "data" && !run} onClick={() => go(s.id)} />
          ))}
        </nav>
        <div className="m-3 rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600">
          <div className="font-medium text-slate-800">{scenario ? scenario.name : "No scenario loaded"}</div>
          <div className="mt-1">{run ? `Plan ${run.id} · ${stateText(run.state)}` : "Load data to begin"}</div>
        </div>
        <p className="px-5 pb-5 text-xs leading-relaxed text-slate-500">
          NEW AURA · IT Consultant Challenge 2026, Round 2 MVP. Costs are synthetic cost units, not a forecast for Company A.
        </p>
      </aside>

      <div className="min-w-0 flex-1 lg:pl-64">
        <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/90 backdrop-blur">
          <div className="flex items-center justify-between gap-3 px-4 py-3 sm:px-8">
            <div className="flex items-center gap-2 lg:hidden">
              <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand-600 text-white"><Boxes size={18} aria-hidden="true" /></span>
              <b className="whitespace-nowrap text-slate-900">Nordic Flow</b>
            </div>
            <div className="hidden text-sm text-slate-500 lg:block">
              Step {STEPS.indexOf(current) + 1} of {STEPS.length} · <span className="font-medium text-slate-800">{current.label}</span>
            </div>
            <div className="flex items-center gap-3">
              {busy && <Loader2 size={16} className="animate-spin text-brand-600" aria-label="Working" />}
              <StatusStrip />
            </div>
          </div>
          <nav aria-label="Workflow" className="flex gap-1 overflow-x-auto border-t border-slate-100 px-3 py-2 lg:hidden">
            {STEPS.map((s, i) => (
              <NavItem key={s.id} compact step={s} index={i} active={tab === s.id} disabled={s.id !== "data" && !run} onClick={() => go(s.id)} />
            ))}
          </nav>
        </header>
        <main className={"mx-auto max-w-6xl px-4 pb-16 pt-8 transition-opacity sm:px-8 " + (busy ? "opacity-70" : "")}>
          <View />
        </main>
      </div>
      <Toasts />
    </div>
  );
}
