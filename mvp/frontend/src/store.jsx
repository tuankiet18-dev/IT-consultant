import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import { api } from "./api";

const Ctx = createContext(null);
export const useApp = () => useContext(Ctx);

export function AppProvider({ children }) {
  const [config, setConfig] = useState(null);
  const [scenario, setScenario] = useState(null);
  const [run, setRun] = useState(null);
  const [runs, setRuns] = useState([]);
  const [explanation, setExplanation] = useState(null);
  const [audit, setAudit] = useState([]);
  const [chain, setChain] = useState(null);
  const [tab, setTab] = useState("data");
  const [busy, setBusy] = useState(false);
  const [toasts, setToasts] = useState([]);
  const [whatif, setWhatif] = useState({ changes: [], result: null });
  const [mapping, setMapping] = useState(null);
  const busyRef = useRef(false);

  const toast = useCallback((msg, err) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((t) => [...t, { id, msg, err }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), err ? 7000 : 3500);
  }, []);

  useEffect(() => {
    api("/config").then(setConfig).catch(() => setConfig({ llm_enabled: false }));
  }, []);

  // Runs one action at a time, shows errors as toasts.
  const act = useCallback(async (fn) => {
    if (busyRef.current) return;
    busyRef.current = true; setBusy(true);
    try { await fn(); } catch (e) { toast(e.message, true); } finally { busyRef.current = false; setBusy(false); }
  }, [toast]);

  const ent = useMemo(() => {
    const e = scenario ? scenario.entities : { suppliers: {}, warehouses: {}, zones: {}, skus: {} };
    return {
      raw: e,
      wh: (id) => (e.warehouses[id] || {}).name || id,
      zone: (id) => (e.zones[id] || {}).name || id,
      sku: (id) => e.skus[id] || id,
      supplier: (id) => e.suppliers[id] || id,
      capacity: (id) => (e.warehouses[id] || {}).capacity,
    };
  }, [scenario]);

  const loadAudit = useCallback(async (r) => {
    if (!r) return;
    try {
      setAudit(await api(`/audit?scenario_id=${r.scenario_id}`));
      setChain(await api("/audit/verify"));
    } catch (e) { toast(e.message, true); }
  }, [toast]);

  const loadExplanation = useCallback(async (r) => {
    try { const e = await api(`/runs/${r.id}/explanation`); setExplanation(e.text ? e : null); }
    catch (e) { toast(e.message, true); }
  }, [toast]);

  const refreshRuns = useCallback(async (sid) => { setRuns(await api(`/scenarios/${sid}/runs`)); }, []);

  const go = useCallback((t) => {
    setTab(t);
    if (t === "review" && run) loadExplanation(run);
    if (t === "audit" && run) loadAudit(run);
    window.scrollTo({ top: 0 });
  }, [run, loadAudit, loadExplanation]);

  const resetRun = () => {
    setRun(null); setRuns([]); setExplanation(null); setAudit([]); setChain(null);
    setWhatif({ changes: [], result: null }); setMapping(null);
  };

  const actions = {
    loadSample: (name) => act(async () => {
      setScenario(await api("/scenarios/sample", { method: "POST", json: { name } })); resetRun(); toast("Scenario loaded");
    }),
    upload: (files) => act(async () => {
      const fd = new FormData(); for (const f of files) fd.append("files", f); const list = [...files]; fd.append("name", list.length === 1 ? list[0].name.replace(/\.(zip|csv)$/i, "") : `${list.length} uploaded files`);
      setScenario(await api("/scenarios", { method: "POST", form: fd })); resetRun();
    }),
    runOpt: (mode, time_limit) => act(async () => {
      const r = await api(`/scenarios/${scenario.id}/runs`, { method: "POST", json: { mode, time_limit } });
      setRun(r); setExplanation(null); await refreshRuns(scenario.id); setTab("results"); window.scrollTo({ top: 0 });
    }),
    openRun: (id, nextTab) => act(async () => {
      const r = await api(`/runs/${id}`); setRun(r); setExplanation(null); setAudit([]); await refreshRuns(r.scenario_id);
      if (nextTab) setTab(nextTab);
      if (nextTab === "review" || (!nextTab && tab === "review")) await loadExplanation(r);
    }),
    explain: (use_llm) => act(async () => {
      setExplanation(await api(`/runs/${run.id}/explanation`, { method: "POST", json: { use_llm } }));
    }),
    approveExpl: (text) => act(async () => {
      setExplanation(await api(`/runs/${run.id}/explanation/approve`, { method: "POST", json: { text, actor: "planner" } }));
      toast("Explanation approved");
    }),
    clearExplanation: () => setExplanation(null),
    applyOverride: (body) => act(async () => {
      const r = await api(`/runs/${run.id}/overrides`, { method: "POST", json: body });
      setRun(r); setExplanation(null); await refreshRuns(r.scenario_id); toast(`New run ${r.id} created`); setTab("results"); window.scrollTo({ top: 0 });
    }),
    applyRoute: (body) => act(async () => {
      const r = await api(`/runs/${run.id}/routes`, { method: "POST", json: body });
      setRun(r); setExplanation(null); await refreshRuns(r.scenario_id); toast(`Manual route saved in plan ${r.id}`); setTab("results"); window.scrollTo({ top: 0 });
    }),
    removeRoute: (index) => act(async () => {
      const r = await api(`/runs/${run.id}/routes/${index}`, { method: "DELETE" });
      setRun(r); setExplanation(null); await refreshRuns(r.scenario_id); toast(`Route constraint removed in plan ${r.id}`); setTab("results"); window.scrollTo({ top: 0 });
    }),
    decide: (decision, comment) => act(async () => {
      const r = await api(`/runs/${run.id}/decision`, { method: "POST", json: { decision, comment, actor: "planner" } });
      setRun(r); await refreshRuns(r.scenario_id); await loadAudit(r);
      toast(decision === "approve" ? "Plan approved" : "Plan rejected");
    }),
    exportZip: () => act(async () => {
      const b = await api(`/runs/${run.id}/export`, { blob: true });
      const a = document.createElement("a"); a.href = URL.createObjectURL(b); a.download = `nordic-flow-run-${run.id}.zip`;
      document.body.append(a); a.click(); a.remove(); await loadAudit(run);
    }),
    suggestMap: (items, use_llm) => act(async () => {
      setMapping(await api("/mapping/suggest", { method: "POST", json: { scenario_id: scenario.id, items, use_llm } }));
    }),
    confirmMap: (i) => act(async () => {
      const m = mapping[i];
      await api("/mapping/confirm", { method: "POST", json: { scenario_id: scenario.id, external: m.external, sku_id: m.candidates[0].sku_id } });
      setMapping((arr) => arr.map((x, j) => (j === i ? { ...x, confirmed: true } : x))); toast("Match confirmed and logged");
    }),
    setWhatifChanges: (fn) => setWhatif((w) => ({ ...w, changes: fn(w.changes) })),
    runWhatIf: () => act(async () => {
      const result = await api(`/scenarios/${scenario.id}/whatif`, { method: "POST", json: { changes: whatif.changes, mode: "milp", time_limit: 30 } });
      setWhatif((w) => ({ ...w, result }));
    }),
  };

  const value = { config, scenario, run, runs, explanation, audit, chain, tab, busy, toasts, whatif, mapping, ent, go, toast, ...actions };
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}
