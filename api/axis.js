// AXIS AI proxy — forwards the app's chat/briefing requests to Anthropic.
//
// Key resolution:
//   1. A user-pasted key sent by the app in `x-api-key` (bring-your-own-key)
//   2. Otherwise the operator's ANTHROPIC_API_KEY env var (set in Vercel)
//
// GET is used by the app as a reachability check.

const WINDOW_MS = 60_000;
const MAX_PER_WINDOW = 20; // per-IP requests/min when using the server key
const buckets = new Map(); // best-effort, per warm instance only

function rateLimited(ip) {
  const now = Date.now();
  const b = buckets.get(ip) || { start: now, n: 0 };
  if (now - b.start > WINDOW_MS) {
    b.start = now;
    b.n = 0;
  }
  b.n += 1;
  buckets.set(ip, b);
  if (buckets.size > 5000) buckets.clear();
  return b.n > MAX_PER_WINDOW;
}

module.exports = async (req, res) => {
  if (req.method === 'GET') {
    res.status(200).json({ ok: true, configured: Boolean(process.env.ANTHROPIC_API_KEY) });
    return;
  }
  if (req.method !== 'POST') {
    res.status(405).json({ error: { type: 'method_not_allowed', message: 'Use POST.' } });
    return;
  }

  const userKey = req.headers['x-api-key'];
  const usingServerKey = !(userKey && String(userKey).startsWith('sk-ant'));
  const key = usingServerKey ? process.env.ANTHROPIC_API_KEY : userKey;

  if (!key) {
    res.status(503).json({
      error: {
        type: 'not_configured',
        message:
          'AXIS is not configured yet. Paste your own Anthropic API key in Settings, ' +
          'or the site operator must set the ANTHROPIC_API_KEY environment variable.',
      },
    });
    return;
  }

  if (usingServerKey) {
    const ip =
      (req.headers['x-forwarded-for'] || '').split(',')[0].trim() ||
      req.socket?.remoteAddress ||
      'unknown';
    if (rateLimited(ip)) {
      res.status(429).json({
        error: { type: 'rate_limited', message: 'Too many requests — slow down and try again in a minute.' },
      });
      return;
    }
  }

  const body = req.body || {};
  // Cost guardrails when the operator's key is footing the bill.
  if (usingServerKey) {
    body.max_tokens = Math.min(Number(body.max_tokens) || 800, 2000);
    delete body.stream;
  }

  try {
    const upstream = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-api-key': key,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify(body),
    });
    const data = await upstream.json();
    res.status(upstream.status).json(data);
  } catch (err) {
    res.status(502).json({
      error: { type: 'upstream_error', message: 'Could not reach the AI service. Try again shortly.' },
    });
  }
};
