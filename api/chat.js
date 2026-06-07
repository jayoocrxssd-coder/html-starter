// Vercel serverless proxy — keeps Anthropic calls server-side so the user's
// API key never appears in browser request headers visible to third parties.
export const config = { runtime: 'edge' };

export default async function handler(req) {
  if (req.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 });
  }

  let body;
  try {
    body = await req.json();
  } catch {
    return new Response('Bad request', { status: 400 });
  }

  // Key comes from the request body (user-supplied, stored in their localStorage).
  // Fall back to an env var for deployments where the operator provides the key.
  const apiKey = body._key || process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return new Response(JSON.stringify({ error: { message: 'No API key provided.' } }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // Strip the internal _key field before forwarding to Anthropic.
  const { _key, ...payload } = body;

  const upstream = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify(payload),
  });

  const data = await upstream.text();
  return new Response(data, {
    status: upstream.status,
    headers: { 'Content-Type': 'application/json' },
  });
}
