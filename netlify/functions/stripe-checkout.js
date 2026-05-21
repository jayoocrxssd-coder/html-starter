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

const PLAN_PRICES = {
  personal:       process.env.STRIPE_PRICE_PERSONAL,
  small_business: process.env.STRIPE_PRICE_SMALL_BUSINESS,
  enterprise:     process.env.STRIPE_PRICE_ENTERPRISE,
};

exports.handler = async (event) => {
  if (event.httpMethod === 'OPTIONS') return { statusCode: 200, headers: CORS, body: '' };
  if (event.httpMethod !== 'POST')    return { statusCode: 405, headers: CORS, body: JSON.stringify({ error: 'Method not allowed' }) };

  const idToken = (event.headers.authorization || '').replace('Bearer ', '');
  if (!idToken) return { statusCode: 401, headers: CORS, body: JSON.stringify({ error: 'Unauthorized' }) };

  try {
    const app = getAdminApp();
    const decoded = await getAuth(app).verifyIdToken(idToken);
    const { uid, email } = decoded;

    const { plan, successUrl, cancelUrl } = JSON.parse(event.body || '{}');
    const priceId = PLAN_PRICES[plan];
    if (!priceId) return { statusCode: 400, headers: CORS, body: JSON.stringify({ error: 'Invalid plan — check STRIPE_PRICE_* env vars.' }) };

    const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
    const db     = getFirestore(app);
    const docRef = db.collection('war_room_data').doc(uid);
    const doc    = await docRef.get();

    // Resolve existing Stripe customer ID from top-level field or inside state blob
    let stripeCustomerId = doc.exists ? doc.data()?.stripeCustomerId : null;
    if (!stripeCustomerId && doc.exists && doc.data()?.data) {
      try { stripeCustomerId = JSON.parse(doc.data().data)?.profile?.stripeCustomerId || null; } catch (_) {}
    }

    if (!stripeCustomerId) {
      const customer = await stripe.customers.create({ email, metadata: { firebaseUid: uid } });
      stripeCustomerId = customer.id;
    }

    // Write stripeCustomerId into the state blob AND as a top-level index (for webhook lookups)
    const state = (doc.exists && doc.data()?.data) ? JSON.parse(doc.data().data) : {};
    if (!state.profile) state.profile = {};
    state.profile.stripeCustomerId = stripeCustomerId;
    await docRef.set({ data: JSON.stringify(state), stripeCustomerId, updated_at: new Date().toISOString() }, { merge: true });

    const origin  = event.headers.origin || `https://${event.headers.host}`;
    const session = await stripe.checkout.sessions.create({
      customer:          stripeCustomerId,
      mode:              'subscription',
      line_items:        [{ price: priceId, quantity: 1 }],
      success_url:       successUrl || `${origin}/app.html?checkout=success`,
      cancel_url:        cancelUrl  || `${origin}/app.html`,
      metadata:          { firebaseUid: uid, plan },
      subscription_data: { metadata: { firebaseUid: uid, plan } },
      allow_promotion_codes: true,
    });

    return { statusCode: 200, headers: { ...CORS, 'Content-Type': 'application/json' }, body: JSON.stringify({ url: session.url }) };
  } catch (err) {
    console.error('[stripe-checkout]', err.message);
    return { statusCode: 500, headers: CORS, body: JSON.stringify({ error: err.message }) };
  }
};
