// ATHLYST payout & leaderboard engine.
// Pure-ish calculation layer: given rows for a month, produce the numbers the
// dashboard and CSV export display. Business rules from the brief live here.

import { prisma } from '../db.js';

// Which bonus tier does a post hit? The highest tier whose threshold the view
// count meets or exceeds. Returns null if it's below every threshold.
export function tierForViews(tiers, viewCount) {
  let hit = null;
  for (const t of tiers) {
    if (viewCount >= t.threshold && (!hit || t.threshold > hit.threshold)) hit = t;
  }
  return hit;
}

// Compute one affiliate's full payout breakdown for a month.
// `ctx` carries the month's shared data so we don't re-query per affiliate.
function computeAffiliate(affiliate, ctx) {
  const { month, salesByAffiliate, viewsByAffiliate, tiers, leaderboard, prizes } = ctx;

  const sales = salesByAffiliate.get(affiliate.id) || { amount: 0, orders: 0 };
  const views = viewsByAffiliate.get(affiliate.id) || [];

  // --- View-tier bonuses (verified posts only) ---------------------------
  let viewBonusCash = 0;
  let viewBonusWholesale = 0;
  let viewBonusRetail = 0;
  let commissionBump = 0;
  const bonusHits = [];
  for (const v of views) {
    if (!v.verified) continue; // unverified posts never count toward bonuses
    // Recompute against current tier config so edits to thresholds/rewards
    // are reflected immediately, even if the stored tag is now stale.
    const tier = tierForViews(tiers, v.viewCount);
    if (!tier) continue;
    viewBonusCash += tier.cashAmount;
    viewBonusWholesale += tier.productWholesaleCost;
    viewBonusRetail += tier.productRetailValue;
    commissionBump = Math.max(commissionBump, tier.commissionBumpPct);
    bonusHits.push({ postLink: v.postLink, tier: tier.label, cash: tier.cashAmount, wholesale: tier.productWholesaleCost });
  }

  // --- Commission (sales × their %, plus any earned bump) ----------------
  const effectiveRate = affiliate.commissionPct + commissionBump;
  const commission = round2((sales.amount * effectiveRate) / 100);

  // --- Ambassador monthly base ------------------------------------------
  const ambassadorBase = affiliate.tier === 'Ambassador' ? affiliate.monthlyBase : 0;

  // --- Leaderboard prizes (can place on both boards) --------------------
  let leaderboardCash = 0;
  let leaderboardWholesale = 0;
  let leaderboardRetail = 0;
  const leaderboardWins = [];
  for (const board of ['views', 'sales']) {
    const rank = leaderboard[board].findIndex((r) => r.affiliateId === affiliate.id) + 1;
    if (rank >= 1 && rank <= 3) {
      const prize = prizes.find((p) => p.rank === rank && (p.board === board || p.board === 'both' || !p.board));
      if (prize) {
        leaderboardCash += prize.cashAmount || 0;
        leaderboardWholesale += prize.productWholesaleCost || 0;
        leaderboardRetail += prize.productRetailValue || 0;
        leaderboardWins.push({ board, rank, cash: prize.cashAmount || 0, product: prize.productDescription || '' });
      }
    }
  }

  const cashOwed = round2(commission + viewBonusCash + ambassadorBase + leaderboardCash);
  const productWholesale = round2(viewBonusWholesale + leaderboardWholesale);
  const productRetail = round2(viewBonusRetail + leaderboardRetail);

  return {
    affiliateId: affiliate.id,
    name: affiliate.name,
    tier: affiliate.tier,
    discountCode: affiliate.discountCode,
    payoutEmail: affiliate.payoutEmail,
    month,
    sales: round2(sales.amount),
    orderCount: sales.orders,
    commissionPct: affiliate.commissionPct,
    commissionBump,
    commission,
    ambassadorBase,
    viewBonusCash: round2(viewBonusCash),
    bonusHits,
    leaderboardCash: round2(leaderboardCash),
    leaderboardWins,
    // Cash the affiliate is owed vs. product/store-credit value.
    cashOwed,
    productWholesale, // real cost to you — used for budget math
    productRetail, // perceived value handed to the affiliate
  };
}

export const round2 = (n) => Math.round((n + Number.EPSILON) * 100) / 100;

// Build the two monthly leaderboards (reset monthly by construction — we only
// look at rows in `month`). Ranked descending; ties broken by affiliate id.
export async function computeLeaderboard(month) {
  const [viewRows, saleRows, affiliates] = await Promise.all([
    prisma.viewLog.groupBy({ by: ['affiliateId'], where: { month }, _sum: { viewCount: true } }),
    prisma.sale.groupBy({ by: ['affiliateId'], where: { month }, _sum: { amount: true } }),
    prisma.affiliate.findMany({ where: { archived: false }, select: { id: true, name: true, tier: true, discountCode: true } }),
  ]);
  const byId = new Map(affiliates.map((a) => [a.id, a]));
  const decorate = (rows, valueKey) =>
    rows
      .map((r) => ({
        affiliateId: r.affiliateId,
        name: byId.get(r.affiliateId)?.name || `#${r.affiliateId}`,
        tier: byId.get(r.affiliateId)?.tier || '',
        value: valueKey === 'views' ? r._sum.viewCount || 0 : round2(r._sum.amount || 0),
      }))
      .filter((r) => byId.has(r.affiliateId) && r.value > 0)
      .sort((a, b) => b.value - a.value || a.affiliateId - b.affiliateId);

  return {
    views: decorate(viewRows, 'views'),
    sales: decorate(saleRows, 'sales'),
  };
}

// Compute the full payout batch for a month across all active affiliates,
// merged with stored paid-status, plus budget totals and a ceiling warning.
export async function computeMonthlyBatch(month) {
  const [affiliates, saleRows, viewRows, tiers, payoutRows, settings, leaderboard] = await Promise.all([
    prisma.affiliate.findMany({ where: { archived: false, status: 'active' } }),
    prisma.sale.findMany({ where: { month } }),
    prisma.viewLog.findMany({ where: { month } }),
    prisma.bonusTier.findMany({ orderBy: { threshold: 'asc' } }),
    prisma.payout.findMany({ where: { month } }),
    getSettingsRaw(),
    computeLeaderboard(month),
  ]);

  const salesByAffiliate = new Map();
  for (const s of saleRows) {
    const cur = salesByAffiliate.get(s.affiliateId) || { amount: 0, orders: 0 };
    cur.amount += s.amount;
    cur.orders += 1;
    salesByAffiliate.set(s.affiliateId, cur);
  }
  const viewsByAffiliate = new Map();
  for (const v of viewRows) {
    const arr = viewsByAffiliate.get(v.affiliateId) || [];
    arr.push(v);
    viewsByAffiliate.set(v.affiliateId, arr);
  }
  const payoutByAffiliate = new Map(payoutRows.map((p) => [p.affiliateId, p]));
  const prizes = JSON.parse(settings.leaderboardPrizes || '[]');

  const ctx = { month, salesByAffiliate, viewsByAffiliate, tiers, leaderboard, prizes };

  const rows = affiliates.map((a) => {
    const calc = computeAffiliate(a, ctx);
    const stored = payoutByAffiliate.get(a.id);
    return {
      ...calc,
      paid: stored?.paid || false,
      paidAt: stored?.paidAt || null,
      payoutType: stored?.payoutType || 'cash',
      notes: stored?.notes || '',
    };
  });

  // Budget math: projected cash out + real product cost vs. the ceiling.
  const totalCash = round2(rows.reduce((s, r) => s + r.cashOwed, 0));
  const totalProductWholesale = round2(rows.reduce((s, r) => s + r.productWholesale, 0));
  const totalProductRetail = round2(rows.reduce((s, r) => s + r.productRetail, 0));
  const projectedSpend = round2(totalCash + totalProductWholesale);
  const ceiling = settings.monthlyBudgetCeiling || 0;
  const budget = {
    ceiling,
    totalCash,
    totalProductWholesale,
    totalProductRetail,
    projectedSpend,
    // Warn when projected spend reaches 90% of the ceiling.
    warning: ceiling > 0 && projectedSpend >= ceiling * 0.9,
    overBudget: ceiling > 0 && projectedSpend > ceiling,
    pctOfCeiling: ceiling > 0 ? round2((projectedSpend / ceiling) * 100) : 0,
  };

  return { month, rows, budget, leaderboard };
}

// Small internal: raw settings row (strings intact) for the engine.
async function getSettingsRaw() {
  let s = await prisma.settings.findUnique({ where: { id: 1 } });
  if (!s) s = await prisma.settings.create({ data: { id: 1 } });
  return s;
}
