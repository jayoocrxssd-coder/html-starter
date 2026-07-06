// Password reset — called by /forgot-password.html.
// Proxies to Supabase's recover endpoint so the reset email links back to
// our /reset-password.html page. Uses the public anon key (safe to embed);
// SUPABASE_URL / SUPABASE_ANON_KEY env vars override the defaults.

const SUPABASE_URL =
  process.env.SUPABASE_URL || 'https://xtvvbylcejvkgvyrcist.supabase.co';
const SUPABASE_ANON_KEY =
  process.env.SUPABASE_ANON_KEY ||
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh0dnZieWxjZWp2a2d2eXJjaXN0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE4Mjg2MDUsImV4cCI6MjA5NzQwNDYwNX0.WwT1ZxdW5XuRTr9OKcCTjSPO9DKAJd0E86DcL2_iyV4';

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Use POST.' });
    return;
  }

  const email = String((req.body && req.body.email) || '').trim().toLowerCase();
  if (!email || !email.includes('@')) {
    res.status(400).json({ error: 'Enter a valid email address.' });
    return;
  }

  const proto = req.headers['x-forwarded-proto'] || 'https';
  const host = req.headers['x-forwarded-host'] || req.headers.host;
  const redirectTo = `${proto}://${host}/reset-password.html`;

  try {
    const upstream = await fetch(`${SUPABASE_URL}/auth/v1/recover`, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        apikey: SUPABASE_ANON_KEY,
      },
      body: JSON.stringify({ email, gotrue_meta_security: {}, redirect_to: redirectTo }),
    });

    // Always report success to the caller (don't leak which emails exist),
    // unless Supabase itself is rejecting the request outright.
    if (upstream.status >= 500) {
      res.status(502).json({ error: 'Reset service unavailable. Try again shortly.' });
      return;
    }
    res.status(200).json({ ok: true });
  } catch (err) {
    res.status(502).json({ error: 'Reset service unavailable. Try again shortly.' });
  }
};
