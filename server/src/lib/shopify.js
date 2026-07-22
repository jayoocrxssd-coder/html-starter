// Shopify Admin API service (feature 2: live sales pull).
// GraphQL preferred. Pulls orders for a month, matches each to an affiliate by
// its discount code, and upserts a Sale row. Fully env-gated: if credentials
// aren't set the rest of the app still works on manual/seeded data.

import { prisma, monthKey } from '../db.js';

export function shopifyConfig() {
  return {
    shop: process.env.SHOPIFY_SHOP || '',
    token: process.env.SHOPIFY_ADMIN_TOKEN || '',
    version: process.env.SHOPIFY_API_VERSION || '2025-01',
  };
}

export function isConfigured() {
  const { shop, token } = shopifyConfig();
  return Boolean(shop && token);
}

async function adminGraphQL(query, variables) {
  const { shop, token, version } = shopifyConfig();
  const res = await fetch(`https://${shop}/admin/api/${version}/graphql.json`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Shopify-Access-Token': token },
    body: JSON.stringify({ query, variables }),
  });
  if (!res.ok) throw new Error(`Shopify API ${res.status}: ${await res.text()}`);
  const json = await res.json();
  if (json.errors) throw new Error(`Shopify GraphQL error: ${JSON.stringify(json.errors)}`);
  return json.data;
}

const ORDERS_QUERY = `
  query Orders($query: String!, $cursor: String) {
    orders(first: 100, after: $cursor, query: $query) {
      pageInfo { hasNextPage endCursor }
      nodes {
        id
        name
        createdAt
        discountCodes
        currentSubtotalPriceSet { shopMoney { amount } }
      }
    }
  }
`;

// Sync all orders in a "YYYY-MM" month, matching to affiliates by code.
// Idempotent: re-running upserts on shopifyOrderId so totals don't double up.
export async function syncSalesForMonth(month) {
  if (!isConfigured()) {
    const err = new Error('Shopify is not connected. Add SHOPIFY_SHOP and SHOPIFY_ADMIN_TOKEN to your .env.');
    err.code = 'NOT_CONFIGURED';
    throw err;
  }

  // Build a lookup of discount code (lowercased) -> affiliate.
  const affiliates = await prisma.affiliate.findMany({ where: { archived: false } });
  const byCode = new Map(affiliates.map((a) => [a.discountCode.toLowerCase(), a]));

  // Month window in ISO for the Shopify search query.
  const [y, m] = month.split('-').map(Number);
  const start = new Date(Date.UTC(y, m - 1, 1)).toISOString();
  const end = new Date(Date.UTC(y, m, 1)).toISOString();
  const search = `created_at:>='${start}' AND created_at:<'${end}'`;

  let cursor = null;
  let scanned = 0;
  let matched = 0;
  const perAffiliate = new Map();

  do {
    const data = await adminGraphQL(ORDERS_QUERY, { query: search, cursor });
    const { nodes, pageInfo } = data.orders;
    for (const o of nodes) {
      scanned += 1;
      const codes = (o.discountCodes || []).map((c) => String(c).toLowerCase());
      const affiliate = codes.map((c) => byCode.get(c)).find(Boolean);
      if (!affiliate) continue;
      const amount = Number(o.currentSubtotalPriceSet?.shopMoney?.amount || 0);
      const orderedAt = new Date(o.createdAt);
      await prisma.sale.upsert({
        where: { shopifyOrderId: o.id },
        create: {
          affiliateId: affiliate.id,
          shopifyOrderId: o.id,
          orderName: o.name,
          discountCode: affiliate.discountCode,
          amount,
          orderedAt,
          month: monthKey(orderedAt),
        },
        update: { amount, affiliateId: affiliate.id, discountCode: affiliate.discountCode, month: monthKey(orderedAt) },
      });
      matched += 1;
      perAffiliate.set(affiliate.name, (perAffiliate.get(affiliate.name) || 0) + amount);
    }
    cursor = pageInfo.hasNextPage ? pageInfo.endCursor : null;
  } while (cursor);

  return {
    month,
    scanned,
    matched,
    byAffiliate: Object.fromEntries([...perAffiliate].map(([k, v]) => [k, Math.round(v * 100) / 100])),
  };
}
