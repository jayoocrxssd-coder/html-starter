// Tiny fetch wrapper for the ATHLYST API. Throws on non-2xx with the server's
// error message so pages can surface it in a Polaris banner/toast.
async function req(method, path, body) {
  const res = await fetch(`/api${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const j = await res.json();
      msg = j.error || msg;
    } catch {}
    throw new Error(msg);
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  get: (p) => req('GET', p),
  post: (p, b) => req('POST', p, b),
  put: (p, b) => req('PUT', p, b),
  del: (p) => req('DELETE', p),
};

export const money = (n) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(Number(n) || 0);

export const compactNumber = (n) =>
  new Intl.NumberFormat('en-US', { notation: 'compact' }).format(Number(n) || 0);

// Month options for the switcher: current month back 11 months.
export function monthOptions() {
  const opts = [];
  const d = new Date();
  for (let i = 0; i < 12; i++) {
    const dt = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth() - i, 1));
    const key = `${dt.getUTCFullYear()}-${String(dt.getUTCMonth() + 1).padStart(2, '0')}`;
    const label = dt.toLocaleString('en-US', { month: 'long', year: 'numeric', timeZone: 'UTC' });
    opts.push({ label, value: key });
  }
  return opts;
}
