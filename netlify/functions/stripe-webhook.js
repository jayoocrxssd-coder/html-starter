const Stripe = require('stripe');
const { getApps, initializeApp, getApp, cert } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');

function getAdminApp() {
  if (getApps().length > 0) return getApp();
  return initializeApp({ credential: cert(JSON.parse(process.env.FIREBASE_ADMIN_SDK)) });
}

function planFromPriceId(priceId) {
  const map = {
    [process.env.STRIPE_PRICE_SMALL_BUSINESS]: 'small_business',
    [process.env.STRIPE_PRICE_ENTERPRISE]:     'enterprise',
  };
  return map[priceId] || 'personal';
}

// Find the Firestore doc by the top-level stripeCustomerId index field,
// then merge updates into the S state blob so the app picks them up on next sync.
async function updateUserByCustomer(db, customerId, profileUpdates) {
  const snap = await db.collection('war_room_data')
    .where('stripeCustomerId', '==', customerId)
    .limit(1)
    .get();

  if (snap.empty) { console.warn('[stripe-webhook] No doc for customer:', customerId); return; }

  const docRef  = snap.docs[0].ref;
  const docData = snap.docs[0].data();
  let state = {};
  if (docData.data) { try { state = JSON.parse(docData.data); } catch (_) {} }
  if (!state.profile) state.profile = {};
  Object.assign(state.profile, profileUpdates);

  await docRef.set(
    { data: JSON.stringify(state), stripeCustomerId: customerId, updated_at: new Date().toISOString() },
    { merge: true }
  );
}

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') return { statusCode: 405, body: 'Method not allowed' };

  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
  const sig    = event.headers['stripe-signature'];

  let stripeEvent;
  try {
    // Netlify provides the raw body as a string — Stripe accepts string or Buffer
    stripeEvent = stripe.webhooks.constructEvent(event.body, sig, process.env.STRIPE_WEBHOOK_SECRET);
  } catch (err) {
    console.error('[stripe-webhook] Signature failed:', err.message);
    return { statusCode: 400, body: `Webhook Error: ${err.message}` };
  }

  const db = getFirestore(getAdminApp());

  try {
    switch (stripeEvent.type) {
      case 'checkout.session.completed': {
        const session = stripeEvent.data.object;
        if (session.mode !== 'subscription') break;
        await updateUserByCustomer(db, session.customer, {
          stripeSubscriptionId: session.subscription,
          stripeStatus:  'active',
          currentPlan:   session.metadata?.plan || 'personal',
        });
        break;
      }
      case 'customer.subscription.updated': {
        const sub     = stripeEvent.data.object;
        const priceId = sub.items?.data?.[0]?.price?.id;
        const plan    = planFromPriceId(priceId);
        await updateUserByCustomer(db, sub.customer, {
          stripeSubscriptionId: sub.id,
          stripeStatus:  sub.status,
          currentPlan:   (sub.status === 'active' || sub.status === 'trialing') ? plan : 'personal',
        });
        break;
      }
      case 'customer.subscription.deleted': {
        const sub = stripeEvent.data.object;
        await updateUserByCustomer(db, sub.customer, {
          stripeSubscriptionId: null,
          stripeStatus:  'canceled',
          currentPlan:   'personal',
        });
        break;
      }
      case 'invoice.payment_failed': {
        const inv = stripeEvent.data.object;
        await updateUserByCustomer(db, inv.customer, { stripeStatus: 'past_due' });
        break;
      }
      case 'invoice.payment_succeeded': {
        const inv = stripeEvent.data.object;
        if (inv.billing_reason === 'subscription_create') break; // already handled by checkout.session.completed
        await updateUserByCustomer(db, inv.customer, { stripeStatus: 'active' });
        break;
      }
    }
  } catch (err) {
    // Return 200 so Stripe doesn't retry — the error is logged for manual review
    console.error('[stripe-webhook] Handler error:', err.message);
  }

  return { statusCode: 200, body: JSON.stringify({ received: true }) };
};
