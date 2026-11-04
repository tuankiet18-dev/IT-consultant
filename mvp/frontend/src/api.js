// Thin wrapper over the JSON API under /api. All numbers shown in the UI come from the backend.
export async function api(path, opts = {}) {
  const init = { method: opts.method || "GET", headers: {} };
  if (opts.json !== undefined) {
    init.body = JSON.stringify(opts.json);
    init.headers["Content-Type"] = "application/json";
  }
  if (opts.form) init.body = opts.form;
  const r = await fetch("/api" + path, init);
  if (opts.blob && r.ok) return r.blob();
  let data = null;
  try { data = await r.json(); } catch (_) { /* no body */ }
  if (!r.ok) {
    const e = new Error((data && data.message) || "Request failed");
    e.code = data && data.code;
    e.details = data && data.details;
    throw e;
  }
  return data;
}
