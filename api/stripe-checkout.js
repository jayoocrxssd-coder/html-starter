const Stripe = require('stripe');
const { getApps, initializeApp, getApp, cert } = require('firebase-admin/app');
const { getAuth } = require('firebase-admin/auth');
const { getFirestore } = require('firebase-admin/firestore');

function getAdminApp() {
  if (getApps().length > 0) return getApp();
  const serviceAccount = JSON.parse(process.env.FIREBASE_ADMIN_SDK);
  return initializeApp({ credential: cert(serviceAccount) });
}

const PLAN_PRICES = {
  small_business: process.env.STRIPE_PRICE_SMALL_BUSINESS,
  enterprise: process.env.STRIPE_PRICE_ENTERPRISE,
};

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const idToken = (req.headers.authorization || '').replace('Bearer ', '');
  if (!idToken) return res.status(401).json({ error: 'Unauthorized' });

  try {
    const app = getAdminApp();
    const decoded = await getAuth(app).verifyIdToken(idToken);
    const { uid, email } = decoded;

    const { plan, successUrl, cancelUrl } = req.body;
    const priceId = PLAN_PRICES[plan];
    if (!priceId) return res.status(400).json({ error: 'Invalid plan — check STRIPE_PRICE_* env vars.' });

    const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
    const db = getFirestore(app);
    const docRef = db.collection('war_room_data').doc(uid);
    const doc = await docRef.get();

    // Look for existing stripeCustomerId in top-level field or inside data blob
    let stripeCustomerId = doc.exists ? doc.data()?.stripeCustomerId : null;
    if (!stripeCustomerId && doc.exists && doc.data()?.data) {
      try {
        const state = JSON.parse(doc.data().data);
        stripeCustomerId = state?.profile?.stripeCustomerId || null;
      } catch (_) {}
    }

    if (!stripeCustomerId) {
      const customer = await stripe.customers.create({
        email,
        metadata: { firebaseUid: uid },
      });
      stripeCustomerId = customer.id;
    }

    // Write stripeCustomerId into both the state blob and as a top-level index field
    const currentData = (doc.exists && doc.data()?.data) ? JSON.parse(doc.data().data) : {};
    if (!currentData.profile) currentData.profile = {};
    currentData.profile.stripeCustomerId = stripeCustomerId;
    await docRef.set(
      { data: JSON.stringify(currentData), stripeCustomerId, updated_at: new Date().toISOString() },
      { merge: true }
    );

    const session = await stripe.checkout.sessions.create({
      customer: stripeCustomerId,
      mode: 'subscription',
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: successUrl || `${req.headers.origin}/app.html?checkout=success`,
      cancel_url: cancelUrl || `${req.headers.origin}/app.html`,
      metadata: { firebaseUid: uid, plan },
      subscription_data: { metadata: { firebaseUid: uid, plan } },
      allow_promotion_codes: true,
    });

    return res.status(200).json({ url: session.url });
  } catch (err) {
    console.error('[stripe-checkout]', err.message);
    return res.status(500).json({ error: err.message });
  }
};
