// Stripe Checkout for donations — called by /donate.html.
// Creates a Checkout Session ($ once or monthly) and returns its URL.
// Requires the STRIPE_SECRET_KEY env var (sk_test_... or sk_live_...).

const MIN_CENTS = 100; // $1
const MAX_CENTS = 2_000_000; // $20,000

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Use POST.' });
    return;
  }

  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) {
    res.status(503).json({
      error: 'Donations are not configured yet — the operator must set STRIPE_SECRET_KEY.',
    });
    return;
  }

  const body = req.body || {};
  const amount = Math.round(Number(body.amount));
  const email = String(body.email || '').trim().toLowerCase();
  const monthly = body.frequency === 'monthly';

  if (!Number.isFinite(amount) || amount < MIN_CENTS || amount > MAX_CENTS) {
    res.status(400).json({ error: 'Enter an amount between $1 and $20,000.' });
    return;
  }

  const proto = req.headers['x-forwarded-proto'] || 'https';
  const host = req.headers['x-forwarded-host'] || req.headers.host;
  const base = `${proto}://${host}/donate.html`;

  const params = new URLSearchParams();
  params.set('mode', monthly ? 'subscription' : 'payment');
  params.set('success_url', base + '?success=true');
  params.set('cancel_url', base + '?canceled=true');
  if (email && email.includes('@')) params.set('customer_email', email);
  params.set('line_items[0][quantity]', '1');
  params.set('line_items[0][price_data][currency]', 'usd');
  params.set('line_items[0][price_data][unit_amount]', String(amount));
  params.set(
    'line_items[0][price_data][product_data][name]',
    monthly ? 'Warroom monthly supporter' : 'Warroom beta donation'
  );
  if (monthly) params.set('line_items[0][price_data][recurring][interval]', 'month');
  params.set('metadata[source]', 'donate_page');

  try {
    const upstream = await fetch('https://api.stripe.com/v1/checkout/sessions', {
      method: 'POST',
      headers: {
        Authorization: 'Bearer ' + key,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params.toString(),
    });
    const data = await upstream.json();
    if (!upstream.ok || !data.url) {
      const msg = (data.error && data.error.message) || 'Payment setup failed. Please try again.';
      res.status(502).json({ error: msg });
      return;
    }
    res.status(200).json({ url: data.url });
  } catch (err) {
    res.status(502).json({ error: 'Payment service unavailable. Try again shortly.' });
  }
};
