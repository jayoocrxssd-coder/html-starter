const Stripe = require('stripe');
const { getApps, initializeApp, getApp, cert } = require('firebase-admin/app');
const { getAuth } = require('firebase-admin/auth');
const { getFirestore } = require('firebase-admin/firestore');

function getAdminApp() {
  if (getApps().length > 0) return getApp();
  const serviceAccount = JSON.parse(process.env.FIREBASE_ADMIN_SDK);
  return initializeApp({ credential: cert(serviceAccount) });
}

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
    const { uid } = decoded;

    const db = getFirestore(app);
    const docRef = db.collection('war_room_data').doc(uid);
    const doc = await docRef.get();

    // Read stripeCustomerId from top-level field or inside data blob
    let stripeCustomerId = doc.exists ? doc.data()?.stripeCustomerId : null;
    if (!stripeCustomerId && doc.exists && doc.data()?.data) {
      try {
        const state = JSON.parse(doc.data().data);
        stripeCustomerId = state?.profile?.stripeCustomerId || null;
      } catch (_) {}
    }

    if (!stripeCustomerId) {
      return res.status(400).json({ error: 'No subscription found. Please upgrade first.' });
    }

    const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
    const { returnUrl } = req.body;

    const portalSession = await stripe.billingPortal.sessions.create({
      customer: stripeCustomerId,
      return_url: returnUrl || `${req.headers.origin}/app.html`,
    });

    return res.status(200).json({ url: portalSession.url });
  } catch (err) {
    console.error('[stripe-portal]', err.message);
    return res.status(500).json({ error: err.message });
  }
};
