"use strict";
/* Nordic Flow MVP front end. No build step; talks to the JSON API under /api. All numbers shown come from the backend. */

const state = {config: null, scenario: null, run: null, runs: [], explanation: null, audit: [], chain: null, tab: "data", whatif: {changes: [], result: null}, mapping: null, busy: false};
const view = document.getElementById("view");

// ---------- helpers ----------
function el(tag, props, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(props || {})) {
    if (k === "class") e.className = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
    else if (k === "html") e.innerHTML = v;            // only used with static strings
    else if (v !== false && v != null) e.setAttribute(k, v === true ? "" : v);
  }
  for (const kid of kids.flat()) if (kid != null && kid !== false) e.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  return e;
}
const fmt = (n, d = 0) => n == null ? "n/a" : Number(n).toLocaleString("en-US", {minimumFractionDigits: d, maximumFractionDigits: d});
const pct = (x) => fmt(x * 100, 0) + "%";
function toast(msg, err) {
  const t = el("div", {class: "toast" + (err ? " err" : "")}, msg);
  document.getElementById("toasts").append(t); setTimeout(() => t.remove(), err ? 7000 : 3500);
}
async function api(path, opts = {}) {
  const init = {method: opts.method || "GET", headers: {}};
  if (opts.json !== undefined) { init.body = JSON.stringify(opts.json); init.headers["Content-Type"] = "application/json"; }
  if (opts.form) init.body = opts.form;
  const r = await fetch("/api" + path, init);
  if (opts.blob && r.ok) return r.blob();
  let data = null; try { data = await r.json(); } catch (_) {}
  if (!r.ok) { const e = new Error((data && data.message) || "Request failed"); e.code = data && data.code; e.details = data && data.details; throw e; }
  return data;
}
async function act(fn) {
  if (state.busy) return; state.busy = true; view.classList.add("spin");
  try { await fn(); } catch (e) { toast(e.message, true); } finally { state.busy = false; view.classList.remove("spin"); render(); }
}
const ent = () => state.scenario ? state.scenario.entities : {suppliers: {}, warehouses: {}, zones: {}, skus: {}};
const whName = (id) => (ent().warehouses[id] || {}).name || id;
const zoneName = (id) => (ent().zones[id] || {}).name || id;
const skuName = (id) => ent().skus[id] || id;
const COST = [["inbound_freight", "Inbound freight", "#1e2b33"], ["inbound_handling", "Inbound handling", "#68757d"], ["outbound_freight", "Outbound freight", "#0f766e"], ["outbound_handling", "Outbound handling", "#8fc9c1"]];

// ---------- navigation ----------
const TABS = [["data", "Data"], ["results", "Results"], ["plan", "Plan"], ["review", "Review & adjust"], ["approve", "Approve & audit"], ["whatif", "What-if"]];
function renderSteps() {
  const nav = document.getElementById("steps"); nav.replaceChildren();
  TABS.forEach(([id, label], i) => {
    const disabled = id !== "data" && !state.run;
    nav.append(el("button", {class: state.tab === id ? "on" : "", disabled, onclick: () => go(id)}, el("span", {class: "n"}, i + 1), label));
  });
}
function go(tab) { state.tab = tab; if (tab === "approve") loadAudit(); if (tab === "review" && state.run) loadExplanation(); render(); }
async function loadAudit() { if (!state.run) return; try { state.audit = await api(`/audit?scenario_id=${state.run.scenario_id}`); state.chain = await api("/audit/verify"); render(); } catch (e) { toast(e.message, true); } }
async function loadExplanation() { try { const e = await api(`/runs/${state.run.id}/explanation`); state.explanation = e.text ? e : null; render(); } catch (e) { toast(e.message, true); } }
async function refreshRuns() { state.runs = await api(`/scenarios/${state.scenario.id}/runs`); }
async function openRun(id) { state.run = await api(`/runs/${id}`); state.explanation = null; state.audit = []; await refreshRuns(); }

function render() {
  renderSteps(); view.replaceChildren();
  const fn = {data: viewData, results: viewResults, plan: viewPlan, review: viewReview, approve: viewApprove, whatif: viewWhatIf}[state.tab];
  view.append(fn());
}

// ---------- 1. Data ----------
function viewData() {
  const s = state.scenario, root = el("div");
  root.append(el("section", {}, el("h2", {}, "1. Choose the data"), el("p", {class: "lead"}, "Load an example, or upload the eight CSV files (as a ZIP or selected together). The data is checked before anything is calculated."),
    el("div", {class: "grid g3"},
      el("button", {class: "card choice", onclick: () => loadSample("demo")}, el("b", {}, "Synthetic demo"), el("span", {}, "2 suppliers, 3 warehouses, 6 zones, 20 SKUs. Same size as the Round 1 pilot.")),
      el("button", {class: "card choice", onclick: () => loadSample("golden")}, el("b", {}, "Worked example (700 → 500)"), el("span", {}, "The hand-checkable example from the Round 1 proposal.")),
      el("div", {class: "card"}, el("b", {style: "font-family:var(--serif);font-size:17px"}, "Upload files"),
        el("div", {class: "drop", style: "margin-top:8px"}, el("input", {type: "file", id: "up", multiple: true, accept: ".csv,.zip"})),
        el("button", {class: "btn ghost", style: "margin-top:8px", onclick: upload}, "Check files")))));
  if (!s) return root;
  const errs = s.issues.filter(i => i.severity === "error"), warns = s.issues.filter(i => i.severity === "warning");
  root.append(el("section", {}, el("h2", {}, "Scenario"),
    el("p", {class: "lead"}, s.name, " ", el("span", {class: "tag " + (s.valid ? "good" : "err")}, s.valid ? "Valid" : "Has errors")),
    el("div", {class: "grid g4"}, ...[["Suppliers", s.summary.suppliers], ["Warehouses", s.summary.warehouses], ["Zones", s.summary.zones], ["SKUs", s.summary.skus]].map(([l, v]) => el("div", {class: "card kpi"}, el("div", {class: "label"}, l), el("div", {class: "value"}, v)))),
    el("p", {class: "hint"}, `Total demand ${fmt(s.summary.demand_pallets)} pallets; total warehouse capacity ${fmt(s.summary.capacity_total)} pallet-equivalents per week.`)));
  if (s.issues.length) root.append(el("section", {}, el("h3", {}, `Data checks: ${errs.length} error(s), ${warns.length} warning(s)`),
    el("table", {}, el("thead", {}, el("tr", {}, ...["Severity", "File", "Row", "Message"].map(h => el("th", {}, h)))),
      el("tbody", {}, s.issues.map(i => el("tr", {}, el("td", {}, el("span", {class: "tag " + (i.severity === "error" ? "err" : "warnT")}, i.severity)), el("td", {}, i.file), el("td", {}, i.row ?? ""), el("td", {}, i.message)))))),
    errs.length ? el("div", {class: "note err"}, "Errors block the run. Fix the files and upload them again.") : null);
  if (s.valid) root.append(el("section", {}, el("h2", {}, "2. Run the optimisation"),
    el("p", {class: "lead"}, "The service calculates the preferred-warehouse baseline and the lowest-cost plan, then checks both independently."),
    el("div", {class: "row"}, el("div", {}, el("label", {}, "Method"), el("select", {id: "mode"}, el("option", {value: "milp"}, "MILP: whole pallets (recommended)"), el("option", {value: "lp"}, "LP: fractional pallets (lower bound)"))),
      el("div", {}, el("label", {}, "Time limit (seconds)"), el("input", {id: "tl", type: "number", value: 30, min: 1, max: 300})),
      el("div", {class: "fit"}, el("button", {class: "btn teal", onclick: runOpt}, "Run optimisation")))));
  root.append(viewMapping(s));
  return root;
}
async function loadSample(name) { await act(async () => { state.scenario = await api("/scenarios/sample", {method: "POST", json: {name}}); state.run = null; state.runs = []; toast("Scenario loaded"); }); }
async function upload() {
  const f = document.getElementById("up").files; if (!f.length) return toast("Choose files first", true);
  await act(async () => { const fd = new FormData(); for (const x of f) fd.append("files", x); fd.append("name", "Uploaded scenario");
    state.scenario = await api("/scenarios", {method: "POST", form: fd}); state.run = null; state.runs = []; });
}
async function runOpt() {
  await act(async () => { const mode = document.getElementById("mode").value, tl = +document.getElementById("tl").value;
    state.run = await api(`/scenarios/${state.scenario.id}/runs`, {method: "POST", json: {mode, time_limit: tl}}); state.explanation = null; await refreshRuns(); state.tab = "results"; });
}
function viewMapping(s) {
  const out = el("section", {}, el("details", {}, el("summary", {}, "Optional: map another catalogue to these SKUs"),
    el("p", {class: "hint"}, "Paste one item per line as \"code, name\". Suggestions use text similarity (and the AI, if you tick it); nothing changes until you confirm a match."),
    el("textarea", {id: "mapin", placeholder: "CEM-25, cement standard\nRF-L, roofing sheet large"}),
    el("div", {class: "row", style: "margin-top:8px"}, el("div", {class: "fit"}, el("label", {style: "display:inline"}, el("input", {type: "checkbox", id: "mapllm", style: "width:auto"}), " Also ask the AI to pick (Groq)")),
      el("div", {class: "fit"}, el("button", {class: "btn ghost", onclick: suggestMap}, "Suggest matches")))));
  if (state.mapping) out.querySelector("details").append(el("table", {style: "margin-top:12px"}, el("thead", {}, el("tr", {}, ...["External item", "Best candidates", "AI pick", ""].map(h => el("th", {}, h)))),
    el("tbody", {}, state.mapping.map((m, i) => el("tr", {}, el("td", {}, (m.external.code || "") + " " + m.external.name),
      el("td", {}, m.candidates.map(c => el("div", {}, `${c.name} `, el("span", {class: "tag " + (c.confidence > 0.75 ? "good" : "warnT")}, c.confidence.toFixed(2))))),
      el("td", {}, m.llm_pick ? `${skuName(m.llm_pick.sku_id)}: ${m.llm_pick.reason || ""}` : "–"),
      el("td", {}, m.confirmed ? el("span", {class: "tag good"}, "Confirmed") : el("button", {class: "btn ghost", onclick: () => confirmMap(i)}, "Confirm top match"))))))); 
  return out;
}
async function suggestMap() {
  const lines = document.getElementById("mapin").value.split("\n").map(l => l.trim()).filter(Boolean);
  if (!lines.length) return toast("Paste at least one line", true);
  const items = lines.map(l => { const [code, ...rest] = l.split(","); return rest.length ? {code: code.trim(), name: rest.join(",").trim()} : {code: "", name: code.trim()}; });
  await act(async () => { state.mapping = await api("/mapping/suggest", {method: "POST", json: {scenario_id: state.scenario.id, items, use_llm: document.getElementById("mapllm").checked}}); });
}
async function confirmMap(i) {
  const m = state.mapping[i];
  await act(async () => { await api("/mapping/confirm", {method: "POST", json: {scenario_id: state.scenario.id, external: m.external, sku_id: m.candidates[0].sku_id}}); m.confirmed = true; toast("Match confirmed and logged"); });
}

// ---------- 2. Results ----------
function runBanner(r) {
  const out = [];
  if (r.kind === "override") out.push(el("div", {class: "note info"}, `This run includes ${r.pins.length} planner decision(s) fixed by hand. They cost ${fmt(r.cost_of_planner_decisions)} cost units more than the unconstrained optimum.`));
  if (r.kind === "whatif") out.push(el("div", {class: "note info"}, "This is a what-if run on a modified copy of the data."));
  if (r.state !== "draft") out.push(el("div", {class: "note " + (r.state === "approved" ? "ok" : "err")}, `This run is ${r.state}. It can no longer be changed.`));
  return out;
}
function viewResults() {
  const r = state.run, c = r.comparison, root = el("div");
  root.append(el("h2", {}, "Results"), el("p", {class: "lead"}, `Run ${r.id} · ${r.mode.toUpperCase()} · solver ${r.status} in ${r.solve_seconds}s`), ...runBanner(r));
  if (!c.baseline_valid) root.append(el("div", {class: "note err"}, "The preferred-warehouse baseline could not serve all demand, so no saving is reported. The optimised plan below is still valid."));
  if (r.status === "FEASIBLE") root.append(el("div", {class: "note"}, "The solver stopped at its time limit. This plan is feasible, not proven optimal."));
  root.append(el("div", {class: "grid g4"},
    kpi("Preferred-warehouse baseline", c.baseline_valid ? fmt(c.baseline.total) : "unusable", "synthetic rule, not Company A's actual plan"),
    kpi("Optimised plan", fmt(c.optimised.total), r.status !== "OPTIMAL" ? "feasible within time limit" : r.pins.length ? "optimal with your decisions fixed" : "proven optimal", true),
    kpi("Saving", c.saving == null ? "n/a" : fmt(c.saving), c.saving_pct == null ? "no valid baseline" : fmt(c.saving_pct, 1) + "% of baseline", c.saving != null),
    kpi("Independent check", r.verify.optimised_violations.length ? "Failed" : "Passed", "supply, demand, capacity, lanes, balance")));
  root.append(el("section", {style: "margin-top:28px"}, el("h3", {}, "Where the cost sits (cost units)"), costChart(c), legend(COST.map(([, l, col]) => [l, col]))));
  root.append(el("section", {}, el("h3", {}, "Warehouse load (share of weekly capacity)"), loadChart(c), legend([["Baseline", "#68757d"], ["Optimised", "#0f766e"]])));
  const n = c.changes.length;
  root.append(el("div", {class: "note info"}, `${n} zone-and-SKU decision(s) differ from the baseline. `, el("a", {href: "#", onclick: (e) => { e.preventDefault(); go("plan"); }}, "See the plan")));
  return root;
}
function kpi(label, value, sub, good) { return el("div", {class: "card kpi" + (good ? " good" : "")}, el("div", {class: "label"}, label), el("div", {class: "value"}, value), el("div", {class: "sub"}, sub)); }
function legend(items) { return el("div", {class: "legend"}, items.map(([l, c]) => el("span", {}, el("i", {style: `background:${c}`}), l))); }
function costChart(c) {
  const max = Math.max(c.baseline.total, c.optimised.total, 1);
  const row = (label, d, valid) => el("div", {class: "barrow"}, el("div", {}, label),
    valid ? el("div", {class: "bar", style: `width:${d.total / max * 100}%`}, COST.map(([k, l, col]) => el("div", {title: `${l}: ${fmt(d[k])}`, style: `width:${d.total ? d[k] / d.total * 100 : 0}%;background:${col}`})))
          : el("div", {class: "bar hatch"}), el("div", {class: "t"}, valid ? fmt(d.total) : "unusable"));
  return el("div", {}, row("Baseline", c.baseline, c.baseline_valid), row("Optimised", c.optimised, true));
}
function loadChart(c) {
  return el("div", {}, Object.keys(c.utilisation_optimised).map(w => el("div", {style: "margin:12px 0"}, el("div", {class: "row", style: "gap:8px;margin-bottom:2px"}, el("b", {}, whName(w)),
    el("span", {class: "hint fit"}, `capacity ${fmt((ent().warehouses[w] || {}).capacity)}`)),
    el("div", {class: "load"}, el("div", {style: `width:${Math.min(c.utilisation_baseline[w], 1) * 100}%;background:#68757d`}), ),
    el("div", {class: "load"}, el("div", {style: `width:${Math.min(c.utilisation_optimised[w], 1) * 100}%;background:#0f766e`})),
    el("div", {class: "hint"}, `baseline ${pct(c.utilisation_baseline[w])} → optimised ${pct(c.utilisation_optimised[w])}`))));
}

// ---------- 3. Plan ----------
function allocMap(rows) { const m = {}; for (const r of rows) { const k = r.zone + "|" + r.sku; (m[k] = m[k] || {})[r.warehouse] = r.pallets; } return m; }
function viewPlan() {
  const r = state.run, base = allocMap(r.baseline.outbound), opt = allocMap(r.optimised.outbound), keys = Object.keys(opt).sort();
  const zoneSel = el("select", {id: "fz"}, el("option", {value: ""}, "All zones"), Object.keys(ent().zones).map(z => el("option", {value: z}, zoneName(z))));
  const only = el("input", {type: "checkbox", id: "fo", style: "width:auto"}), q = el("input", {id: "fq", placeholder: "Search SKU"});
  const tbody = el("tbody");
  const fill = () => {
    tbody.replaceChildren();
    for (const k of keys) {
      const [z, s] = k.split("|"), changed = JSON.stringify(base[k] || {}) !== JSON.stringify(opt[k]);
      if (zoneSel.value && zoneSel.value !== z) continue; if (only.checked && !changed) continue; if (q.value && !skuName(s).toLowerCase().includes(q.value.toLowerCase()) && !s.toLowerCase().includes(q.value.toLowerCase())) continue;
      const fmtA = (m) => Object.entries(m || {}).map(([w, p]) => `${whName(w)} ${fmt(p)}`).join(", ") || "–";
      tbody.append(el("tr", {class: changed ? "changed" : ""}, el("td", {}, zoneName(z)), el("td", {}, skuName(s)), el("td", {}, fmtA(opt[k])), el("td", {}, r.comparison.baseline_valid ? fmtA(base[k]) : "unusable"), el("td", {}, changed ? el("span", {class: "tag info"}, "changed") : "")));
    }
  };
  [zoneSel, only, q].forEach(x => x.addEventListener("input", fill)); fill();
  const lanes = {}; for (const x of r.optimised.inbound) { const k = x.supplier + ">" + x.warehouse; lanes[k] = (lanes[k] || 0) + x.pallets; }
  return el("div", {}, el("h2", {}, "Plan"), el("p", {class: "lead"}, "Which warehouse serves each zone and SKU, in pallets per week. Shaded rows differ from the baseline."),
    el("div", {class: "row"}, el("div", {}, el("label", {}, "Zone"), zoneSel), el("div", {}, el("label", {}, "SKU"), q), el("div", {class: "fit"}, el("label", {style: "display:inline"}, only, " Changed only"))),
    el("table", {style: "margin-top:12px"}, el("thead", {}, el("tr", {}, ...["Zone", "SKU", "Optimised: served from (pallets)", "Baseline: served from (pallets)", ""].map(h => el("th", {}, h)))), tbody),
    el("section", {style: "margin-top:28px"}, el("h3", {}, "Inbound flows (supplier to warehouse, pallets)"),
      el("table", {}, el("thead", {}, el("tr", {}, ...["Supplier", "Warehouse", "Pallets"].map((h, i) => el("th", {class: i === 2 ? "num" : ""}, h)))),
        el("tbody", {}, Object.entries(lanes).sort().map(([k, v]) => { const [s, w] = k.split(">"); return el("tr", {}, el("td", {}, ent().suppliers[s] || s), el("td", {}, whName(w)), el("td", {class: "num"}, fmt(v))); })))));
}

// ---------- 4. Review & adjust ----------
function viewReview() {
  const r = state.run, root = el("div", {}, el("h2", {}, "Review & adjust"), el("p", {class: "lead"}, "Read the explanation, then change a decision if the business needs it. Every change needs a reason and is logged."), ...runBanner(r));
  const e = state.explanation, locked = r.state !== "draft";
  const box = el("section", {}, el("h3", {}, "Explanation"));
  if (!e) box.append(el("p", {class: "hint"}, "No explanation yet. The default is a deterministic summary built only from the calculated numbers. The AI option (Groq) writes it in smoother prose, but its numbers are checked and it stays a draft until you approve it."),
    el("div", {class: "row"}, el("div", {class: "fit"}, el("button", {class: "btn ghost", onclick: () => explain(false)}, "Generate summary")),
      el("div", {class: "fit"}, el("button", {class: "btn teal", disabled: !(state.config && state.config.llm_enabled), title: state.config && state.config.llm_enabled ? "" : "Set GROQ_API_KEY to enable", onclick: () => explain(true)}, "Generate with AI (Groq)"))));
  else {
    const ta = el("textarea", {id: "etext", style: "min-height:150px;font:16px/1.55 var(--serif)"}); ta.value = e.text;
    box.append(el("div", {style: "display:flex;gap:8px;margin-bottom:8px"}, el("span", {class: "tag " + (e.source === "deterministic" ? "info" : "warnT")}, e.source === "deterministic" ? "Deterministic summary" : "AI draft · " + e.source),
      el("span", {class: "tag " + (e.status === "approved" ? "good" : "")}, e.status === "approved" ? `Approved by ${e.approved_by}${e.edited ? " (edited)" : ""}` : "Draft: needs your review")),
      ...(e.reason ? [el("div", {class: "note"}, "AI not used: " + e.reason)] : []), ta,
      el("div", {class: "row", style: "margin-top:8px"}, el("div", {class: "fit"}, el("button", {class: "btn teal", disabled: locked || e.status === "approved", onclick: approveExpl}, "Approve explanation")),
        el("div", {class: "fit"}, el("button", {class: "btn ghost", onclick: () => { state.explanation = null; render(); }}, "Regenerate"))),
      el("p", {class: "hint"}, "The numbers on the Results tab are the source of truth. This text only restates them."));
  }
  root.append(box);
  // override form
  const pairs = Object.keys(allocMap(r.optimised.outbound)).sort(), cur = allocMap(r.optimised.outbound);
  const zs = el("select", {id: "oz"}, [...new Set(pairs.map(k => k.split("|")[0]))].map(z => el("option", {value: z}, zoneName(z))));
  const ss = el("select", {id: "os"}), ws = el("select", {id: "ow"}, Object.keys(ent().warehouses).map(w => el("option", {value: w}, whName(w)))), pal = el("input", {id: "op", type: "number", min: 0, step: 1, value: 0}), hint = el("div", {class: "hint"});
  const syncSku = () => { ss.replaceChildren(...pairs.filter(k => k.startsWith(zs.value + "|")).map(k => el("option", {value: k.split("|")[1]}, skuName(k.split("|")[1])))); syncHint(); };
  const syncHint = () => { const a = cur[zs.value + "|" + ss.value] || {}; hint.textContent = "Currently: " + (Object.entries(a).map(([w, p]) => `${whName(w)} ${fmt(p)}`).join(", ") || "–"); const first = Object.entries(a)[0]; if (first) { ws.value = first[0]; pal.value = first[1]; } };
  zs.addEventListener("input", syncSku); ss.addEventListener("input", syncHint); syncSku();
  root.append(el("section", {}, el("h3", {}, "Change a decision"),
    el("p", {class: "hint"}, "Fix exactly this many pallets of one SKU from one warehouse to one zone. The rest of the plan is re-optimised around it, and the extra cost is shown."),
    el("div", {class: "grid g4"}, el("div", {}, el("label", {}, "Zone"), zs), el("div", {}, el("label", {}, "SKU"), ss), el("div", {}, el("label", {}, "Serve from"), ws), el("div", {}, el("label", {}, "Exactly (pallets)"), pal)), hint,
    el("label", {}, "Reason (required)"), el("input", {id: "or", placeholder: "e.g. Customer contract names this warehouse"}),
    el("div", {style: "margin-top:10px"}, el("button", {class: "btn", disabled: locked, onclick: applyOverride}, "Apply and re-optimise")),
    r.pins.length ? el("div", {style: "margin-top:14px"}, el("h3", {}, "Planner decisions in this run"), el("table", {}, el("thead", {}, el("tr", {}, ...["Zone", "SKU", "Warehouse", "Pallets", "Reason"].map(h => el("th", {}, h)))),
      el("tbody", {}, r.pins.map(p => el("tr", {}, el("td", {}, zoneName(p.zone)), el("td", {}, skuName(p.sku)), el("td", {}, whName(p.warehouse)), el("td", {}, fmt(p.pallets)), el("td", {}, p.reason)))))) : null));
  if (state.runs.length > 1) root.append(el("section", {}, el("h3", {}, "Runs for this scenario"), el("table", {}, el("thead", {}, el("tr", {}, ...["Run", "Kind", "State", "Status", ""].map(h => el("th", {}, h)))),
    el("tbody", {}, state.runs.map(x => el("tr", {class: x.id === r.id ? "changed" : ""}, el("td", {}, x.id), el("td", {}, x.kind), el("td", {}, x.state), el("td", {}, x.status), el("td", {}, x.id === r.id ? "open" : el("button", {class: "btn ghost", onclick: () => act(() => openRun(x.id))}, "Open"))))))));
  return root;
}
async function explain(useLlm) { await act(async () => { state.explanation = await api(`/runs/${state.run.id}/explanation`, {method: "POST", json: {use_llm: useLlm}}); }); }
async function approveExpl() { await act(async () => { state.explanation = await api(`/runs/${state.run.id}/explanation/approve`, {method: "POST", json: {text: document.getElementById("etext").value, actor: "planner"}}); toast("Explanation approved"); }); }
async function applyOverride() {
  const body = {zone: val("oz"), sku: val("os"), warehouse: val("ow"), pallets: +val("op"), reason: val("or")};
  await act(async () => { state.run = await api(`/runs/${state.run.id}/overrides`, {method: "POST", json: body}); state.explanation = null; await refreshRuns(); toast(`New run ${state.run.id} created`); state.tab = "results"; });
}
const val = (id) => document.getElementById(id).value;

// ---------- 5. Approve & audit ----------
function viewApprove() {
  const r = state.run, root = el("div", {}, el("h2", {}, "Approve & audit"), el("p", {class: "lead"}, "Nothing is executed by Nordic Flow. An approved plan is exported for the existing ERP, WMS and TMS."), ...runBanner(r));
  const draft = r.state === "draft";
  root.append(el("section", {}, el("h3", {}, "Decision on run " + r.id), el("div", {class: "card"},
    el("p", {}, "Optimised cost ", el("b", {}, fmt(r.comparison.optimised.total)), r.comparison.saving != null ? `, saving ${fmt(r.comparison.saving)} (${fmt(r.comparison.saving_pct, 1)}%)` : ", no saving reported", ` · solver ${r.status} · checks ${r.verify.optimised_violations.length ? "failed" : "passed"}`),
    el("label", {}, "Comment (required if rejecting)"), el("input", {id: "dc", placeholder: "Reviewed cost, capacity and lanes", disabled: !draft}),
    el("div", {class: "row", style: "margin-top:12px"}, el("div", {class: "fit"}, el("button", {class: "btn teal", disabled: !draft, onclick: () => decide("approve")}, "Approve plan")),
      el("div", {class: "fit"}, el("button", {class: "btn danger", disabled: !draft, onclick: () => decide("reject")}, "Reject")),
      el("div", {class: "fit"}, el("button", {class: "btn ghost", disabled: r.state !== "approved", title: r.state === "approved" ? "" : "Only approved plans can be exported", onclick: exportZip}, "Export approved plan (ZIP)"))))));
  const chain = state.chain;
  root.append(el("section", {}, el("h3", {}, "Audit log for this scenario"),
    chain ? el("p", {class: "hint"}, chain.ok ? `Event chain verified (${chain.events} events). Each event includes a hash of the one before it, so edits are detectable. This is tamper-evident, not tamper-proof.` : `Chain broken at event ${chain.broken_at_event}.`) : null,
    el("ul", {class: "timeline"}, state.audit.map(a => el("li", {}, el("span", {class: "mono"}, a.ts.replace("T", " ").replace("+00:00", " UTC")), el("span", {class: "ty"}, a.type.replaceAll("_", " ").toLowerCase() + " · " + a.actor), el("span", {class: "mono"}, payloadText(a.payload) + "  #" + a.hash))))));
  return root;
}
const payloadText = (p) => Object.entries(p).map(([k, v]) => `${k}=${typeof v === "object" ? JSON.stringify(v) : v}`).join("  ").slice(0, 220);
async function decide(d) { await act(async () => { state.run = await api(`/runs/${state.run.id}/decision`, {method: "POST", json: {decision: d, comment: val("dc"), actor: "planner"}}); await refreshRuns(); await loadAudit(); toast(d === "approve" ? "Plan approved" : "Plan rejected"); }); }
async function exportZip() {
  await act(async () => { const b = await api(`/runs/${state.run.id}/export`, {blob: true}); const a = el("a", {href: URL.createObjectURL(b), download: `nordic-flow-run-${state.run.id}.zip`}); document.body.append(a); a.click(); a.remove(); await loadAudit(); });
}

// ---------- 6. What-if ----------
function viewWhatIf() {
  const w = state.whatif, root = el("div", {}, el("h2", {}, "What-if"), el("p", {class: "lead"}, "Try a change on a copy of the data and compare it with the current plan. Nothing here alters the scenario or the approved plan."));
  const type = el("select", {id: "wt"}, [["close_warehouse", "Close a warehouse"], ["set_capacity", "Change warehouse capacity"], ["scale_demand", "Scale demand of a zone"]].map(([v, l]) => el("option", {value: v}, l)));
  const params = el("div", {class: "row"});
  const drawParams = () => {
    params.replaceChildren();
    const whSel = () => el("div", {}, el("label", {}, "Warehouse"), el("select", {id: "wp"}, Object.keys(ent().warehouses).map(x => el("option", {value: x}, whName(x)))));
    if (type.value === "close_warehouse") params.append(whSel());
    if (type.value === "set_capacity") params.append(whSel(), el("div", {}, el("label", {}, "New capacity (pallet-equivalents)"), el("input", {id: "wv", type: "number", min: 0, value: 100})));
    if (type.value === "scale_demand") params.append(el("div", {}, el("label", {}, "Zone"), el("select", {id: "wp"}, Object.keys(ent().zones).map(x => el("option", {value: x}, zoneName(x))))), el("div", {}, el("label", {}, "Multiply demand by"), el("input", {id: "wv", type: "number", step: 0.05, min: 0, value: 1.2})));
  };
  type.addEventListener("input", drawParams); drawParams();
  root.append(el("div", {class: "card"}, el("div", {class: "row"}, el("div", {}, el("label", {}, "Change"), type), params, el("div", {class: "fit"}, el("button", {class: "btn ghost", onclick: addChange}, "Add change"))),
    el("div", {class: "chips"}, w.changes.map((c, i) => el("span", {class: "chip"}, describeChange(c), el("button", {onclick: () => { w.changes.splice(i, 1); render(); }}, "×")))),
    el("button", {class: "btn teal", disabled: !w.changes.length, onclick: runWhatIf}, "Run what-if")));
  const res = w.result;
  if (res) {
    root.append(el("section", {style: "margin-top:24px"}, el("h3", {}, "Result: " + res.description)));
    if (!res.feasible) root.append(el("div", {class: "note err"}, el("b", {}, "No feasible plan exists with this change. "), "Diagnostic hints (not a proof): ", (res.diagnosis.likely_causes || []).join("; ") || "see data checks"),
      res.diagnosis.unmet_by_zone_sku.length ? el("table", {}, el("thead", {}, el("tr", {}, ...["Zone", "SKU", "Pallets that cannot be served"].map(h => el("th", {}, h)))), el("tbody", {}, res.diagnosis.unmet_by_zone_sku.slice(0, 15).map(u => el("tr", {}, el("td", {}, zoneName(u.zone)), el("td", {}, skuName(u.sku)), el("td", {}, fmt(u.pallets)))))) : null);
    else root.append(el("div", {class: "grid g3"}, kpi("Optimised cost with the change", fmt(res.comparison.optimised.total), `solver ${res.status}`, true),
      kpi("Current plan", res.reference ? fmt(res.reference.optimised_total) : "n/a", res.reference ? `run ${res.reference.run_id}` : "no reference run"),
      kpi("Difference", res.reference ? (res.reference.delta > 0 ? "+" : "") + fmt(res.reference.delta) : "n/a", res.reference && res.reference.delta > 0 ? "the change makes the plan dearer" : "cost units")),
      el("div", {style: "margin-top:12px"}, el("button", {class: "btn ghost", onclick: () => act(async () => { await openRun(res.id); state.tab = "results"; })}, "Open this what-if run")));
  }
  return root;
}
function describeChange(c) { return c.type === "close_warehouse" ? `Close ${whName(c.warehouse)}` : c.type === "set_capacity" ? `${whName(c.warehouse)} capacity = ${c.capacity}` : `${zoneName(c.zone)} demand × ${c.factor}`; }
function addChange() {
  const t = val("wt"), p = document.getElementById("wp") && val("wp"), v = document.getElementById("wv") && +val("wv");
  state.whatif.changes.push(t === "close_warehouse" ? {type: t, warehouse: p} : t === "set_capacity" ? {type: t, warehouse: p, capacity: v} : {type: t, zone: p, factor: v}); render();
}
async function runWhatIf() { await act(async () => { state.whatif.result = await api(`/scenarios/${state.scenario.id}/whatif`, {method: "POST", json: {changes: state.whatif.changes, mode: "milp", time_limit: 30}}); }); }

// ---------- boot ----------
(async function init() {
  try { state.config = await api("/config"); } catch (_) { state.config = {llm_enabled: false}; }
  const b = document.getElementById("llm-badge");
  b.textContent = state.config.llm_enabled ? `AI ready (${state.config.llm_model})` : "AI off: no key, deterministic summaries"; b.classList.toggle("ok", !!state.config.llm_enabled);
  render();
})();
