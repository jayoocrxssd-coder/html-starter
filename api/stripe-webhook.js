const Stripe = require('stripe');
const { getApps, initializeApp, getApp, cert } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');

// Disable body parsing — Stripe requires raw body for signature verification
module.exports.config = { api: { bodyParser: false } };

function getAdminApp() {
  if (getApps().length > 0) return getApp();
  const serviceAccount = JSON.parse(process.env.FIREBASE_ADMIN_SDK);
  return initializeApp({ credential: cert(serviceAccount) });
}

function getRawBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on('data', (chunk) => chunks.push(chunk));
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

// Map Stripe price IDs to War Room plan names
function planFromPriceId(priceId) {
  const map = {
    [process.env.STRIPE_PRICE_PERSONAL]: 'personal',
    [process.env.STRIPE_PRICE_SMALL_BUSINESS]: 'small_business',
    [process.env.STRIPE_PRICE_ENTERPRISE]: 'enterprise',
  };
  return map[priceId] || 'personal';
}

// Update Firestore: find user by stripeCustomerId index field, merge updates into data blob + top-level
async function updateUserByCustomer(db, customerId, profileUpdates) {
  const snap = await db.collection('war_room_data')
    .where('stripeCustomerId', '==', customerId)
    .limit(1)
    .get();

  if (snap.empty) {
    console.warn('[stripe-webhook] No Firestore doc for customer:', customerId);
    return;
  }

  const docRef = snap.docs[0].ref;
  const docData = snap.docs[0].data();

  let state = {};
  if (docData.data) {
    try { state = JSON.parse(docData.data); } catch (_) {}
  }
  if (!state.profile) state.profile = {};

  Object.assign(state.profile, profileUpdates);

  await docRef.set(
    {
      data: JSON.stringify(state),
      stripeCustomerId: customerId,        // Keep top-level index fresh
      updated_at: new Date().toISOString(),
    },
    { merge: true }
  );
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
  const sig = req.headers['stripe-signature'];

  let rawBody;
  try {
    rawBody = await getRawBody(req);
  } catch (err) {
    return res.status(400).json({ error: 'Could not read body' });
  }

  let event;
  try {
    event = stripe.webhooks.constructEvent(rawBody, sig, process.env.STRIPE_WEBHOOK_SECRET);
  } catch (err) {
    console.error('[stripe-webhook] Signature verification failed:', err.message);
    return res.status(400).json({ error: `Webhook signature invalid: ${err.message}` });
  }

  const db = getFirestore(getAdminApp());

  try {
    switch (event.type) {
      case 'checkout.session.completed': {
        const session = event.data.object;
        if (session.mode !== 'subscription') break;
        const plan = session.metadata?.plan || 'personal';
        await updateUserByCustomer(db, session.customer, {
          stripeSubscriptionId: session.subscription,
          stripeStatus: 'active',
          currentPlan: plan,
        });
        break;
      }

      case 'customer.subscription.updated': {
        const sub = event.data.object;
        const priceId = sub.items?.data?.[0]?.price?.id;
        const plan = planFromPriceId(priceId);
        await updateUserByCustomer(db, sub.customer, {
          stripeSubscriptionId: sub.id,
          stripeStatus: sub.status,   // active | past_due | trialing | canceled | ...
          currentPlan: sub.status === 'active' || sub.status === 'trialing' ? plan : 'personal',
        });
        break;
      }

      case 'customer.subscription.deleted': {
        const sub = event.data.object;
        await updateUserByCustomer(db, sub.customer, {
          stripeSubscriptionId: null,
          stripeStatus: 'canceled',
          currentPlan: 'personal',
        });
        break;
      }

      case 'invoice.payment_failed': {
        const invoice = event.data.object;
        await updateUserByCustomer(db, invoice.customer, {
          stripeStatus: 'past_due',
        });
        break;
      }

      case 'invoice.payment_succeeded': {
        const invoice = event.data.object;
        if (invoice.billing_reason === 'subscription_create') break; // handled by checkout.session.completed
        await updateUserByCustomer(db, invoice.customer, {
          stripeStatus: 'active',
        });
        break;
      }
    }
  } catch (err) {
    console.error('[stripe-webhook] Handler error:', err.message);
    // Return 200 so Stripe doesn't retry — log the error for manual review
  }

  return res.status(200).json({ received: true });
};
