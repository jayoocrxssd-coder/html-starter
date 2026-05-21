const Stripe = require('stripe');
const { getApps, initializeApp, getApp, cert } = require('firebase-admin/app');
const { getAuth } = require('firebase-admin/auth');
const { getFirestore } = require('firebase-admin/firestore');

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

function getAdminApp() {
  if (getApps().length > 0) return getApp();
  return initializeApp({ credential: cert(JSON.parse(process.env.FIREBASE_ADMIN_SDK)) });
}

exports.handler = async (event) => {
  if (event.httpMethod === 'OPTIONS') return { statusCode: 200, headers: CORS, body: '' };
  if (event.httpMethod !== 'POST')    return { statusCode: 405, headers: CORS, body: JSON.stringify({ error: 'Method not allowed' }) };

  const idToken = (event.headers.authorization || '').replace('Bearer ', '');
  if (!idToken) return { statusCode: 401, headers: CORS, body: JSON.stringify({ error: 'Unauthorized' }) };

  try {
    const app = getAdminApp();
    const decoded = await getAuth(app).verifyIdToken(idToken);
    const { uid }  = decoded;

    const db     = getFirestore(app);
    const doc    = await db.collection('war_room_data').doc(uid).get();

    let stripeCustomerId = doc.exists ? doc.data()?.stripeCustomerId : null;
    if (!stripeCustomerId && doc.exists && doc.data()?.data) {
      try { stripeCustomerId = JSON.parse(doc.data().data)?.profile?.stripeCustomerId || null; } catch (_) {}
    }

    if (!stripeCustomerId) {
      return { statusCode: 400, headers: CORS, body: JSON.stringify({ error: 'No subscription found. Please upgrade first.' }) };
    }

    const stripe      = new Stripe(process.env.STRIPE_SECRET_KEY);
    const { returnUrl } = JSON.parse(event.body || '{}');
    const origin      = event.headers.origin || `https://${event.headers.host}`;

    const portalSession = await stripe.billingPortal.sessions.create({
      customer:   stripeCustomerId,
      return_url: returnUrl || `${origin}/app.html`,
    });

    return { statusCode: 200, headers: { ...CORS, 'Content-Type': 'application/json' }, body: JSON.stringify({ url: portalSession.url }) };
  } catch (err) {
    console.error('[stripe-portal]', err.message);
    return { statusCode: 500, headers: CORS, body: JSON.stringify({ error: err.message }) };
  }
};
