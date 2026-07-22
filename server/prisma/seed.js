// Seeds realistic demo data so the dashboard is populated on first run.
// Safe to re-run: it clears app tables first. Remove/adjust before going live.
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

function monthKey(date) {
  const d = new Date(date);
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, '0')}`;
}
const now = new Date();
const thisMonth = monthKey(now);
const day = (n) => new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), n)).toISOString();

async function main() {
  // Clear in FK-safe order.
  await prisma.viewLog.deleteMany();
  await prisma.sale.deleteMany();
  await prisma.payout.deleteMany();
  await prisma.bonusTier.deleteMany();
  await prisma.affiliate.deleteMany();

  // Settings + leaderboard prizes.
  await prisma.settings.upsert({
    where: { id: 1 },
    update: {},
    create: {
      id: 1,
      commissionDefaults: JSON.stringify({ Athlete: 15, Influencer: 11, Ambassador: 10 }),
      monthlyBudgetCeiling: 2500,
      leaderboardPrizes: JSON.stringify([
        { rank: 1, board: 'both', cashAmount: 150, productDescription: 'Full kit', productWholesaleCost: 60, productRetailValue: 180 },
        { rank: 2, board: 'both', cashAmount: 75, productDescription: 'Hoodie + shaker', productWholesaleCost: 30, productRetailValue: 95 },
        { rank: 3, board: 'both', cashAmount: 0, productDescription: 'Store credit $50', productWholesaleCost: 20, productRetailValue: 50 },
      ]),
    },
  });

  // Configurable view-bonus tiers.
  const tiers = await Promise.all([
    prisma.bonusTier.create({ data: { label: '10K', threshold: 10000, rewardDescription: 'Free product / store credit', cashAmount: 0, productWholesaleCost: 18, productRetailValue: 55, commissionBumpPct: 0, sortOrder: 1 } }),
    prisma.bonusTier.create({ data: { label: '25K', threshold: 25000, rewardDescription: 'Bigger product or small cash', cashAmount: 50, productWholesaleCost: 30, productRetailValue: 95, commissionBumpPct: 0, sortOrder: 2 } }),
    prisma.bonusTier.create({ data: { label: '50K+', threshold: 50000, rewardDescription: 'Cash + commission bump', cashAmount: 125, productWholesaleCost: 0, productRetailValue: 0, commissionBumpPct: 3, sortOrder: 3 } }),
  ]);

  // Affiliates across all three tiers.
  const affiliates = await Promise.all([
    prisma.affiliate.create({ data: { name: 'Maya Torres', email: 'maya@example.com', payoutEmail: 'maya.pp@example.com', country: 'US', platform: 'Instagram', handle: '@mayalifts', tier: 'Athlete', discountCode: 'MAYA15', commissionPct: 15 } }),
    prisma.affiliate.create({ data: { name: 'Devon Clarke', email: 'devon@example.com', payoutEmail: 'devon.pp@example.com', country: 'UK', platform: 'TikTok', handle: '@devonc', tier: 'Influencer', discountCode: 'DEVON12', commissionPct: 12 } }),
    prisma.affiliate.create({ data: { name: 'Priya Nair', email: 'priya@example.com', payoutEmail: 'priya.pp@example.com', country: 'CA', platform: 'YouTube', handle: '@priyafit', tier: 'Ambassador', discountCode: 'PRIYA', commissionPct: 10, monthlyBase: 250 } }),
    prisma.affiliate.create({ data: { name: 'Sam Okafor', email: 'sam@example.com', payoutEmail: 'sam.pp@example.com', country: 'US', platform: 'Instagram', handle: '@samstrength', tier: 'Athlete', discountCode: 'SAM15', commissionPct: 15 } }),
  ]);
  const [maya, devon, priya, sam] = affiliates;

  // Matched sales (as if pulled from Shopify) for this month.
  const sale = (aff, amount, d, name) => prisma.sale.create({ data: { affiliateId: aff.id, shopifyOrderId: `seed:${aff.id}:${name}`, orderName: name, discountCode: aff.discountCode, amount, orderedAt: day(d), month: thisMonth } });
  await Promise.all([
    sale(maya, 320.0, 3, '#1001'), sale(maya, 145.5, 9, '#1014'), sale(maya, 210.0, 15, '#1039'),
    sale(devon, 180.0, 4, '#1005'), sale(devon, 260.0, 12, '#1022'),
    sale(priya, 540.0, 2, '#1002'), sale(priya, 300.0, 18, '#1051'),
    sale(sam, 95.0, 7, '#1011'),
  ]);

  // Logged posts (feature 3), some verified, some not.
  const view = (aff, link, platform, count, d, verified) => {
    const tier = [...tiers].reverse().find((t) => count >= t.threshold);
    return prisma.viewLog.create({ data: { affiliateId: aff.id, postLink: link, platform, viewCount: count, postedAt: day(d), month: thisMonth, verified, bonusTierId: tier?.id || null } });
  };
  await Promise.all([
    view(maya, 'https://instagram.com/p/aaa', 'Instagram', 62000, 5, true),   // 50K+ tier, verified
    view(devon, 'https://tiktok.com/@devonc/video/1', 'TikTok', 28000, 6, true), // 25K tier, verified
    view(priya, 'https://youtube.com/watch?v=xyz', 'YouTube', 14000, 8, true),   // 10K tier, verified
    view(sam, 'https://instagram.com/p/bbb', 'Instagram', 31000, 10, false),     // 25K tier but UNVERIFIED -> no bonus
    view(maya, 'https://instagram.com/p/ccc', 'Instagram', 9000, 20, true),      // below lowest tier -> no bonus
  ]);

  console.log('Seeded ATHLYST demo data for', thisMonth);
}

main().then(() => prisma.$disconnect()).catch(async (e) => { console.error(e); await prisma.$disconnect(); process.exit(1); });
