import { Router } from 'express';
import { prisma, currentMonth } from '../db.js';
import { computeMonthlyBatch } from '../lib/engine.js';

const router = Router();

// The payout calculator screen: every active affiliate + what they're owed.
router.get('/', async (req, res) => {
  const month = req.query.month || currentMonth();
  const batch = await computeMonthlyBatch(month);
  res.json(batch);
});

// Mark paid (y/n) per affiliate per month. Snapshots the breakdown on pay.
router.post('/:affiliateId/paid', async (req, res) => {
  const affiliateId = Number(req.params.affiliateId);
  const month = req.body.month || currentMonth();
  const paid = req.body.paid !== false;

  let snapshotJson = null;
  if (paid) {
    const batch = await computeMonthlyBatch(month);
    const row = batch.rows.find((r) => r.affiliateId === affiliateId);
    if (row) snapshotJson = JSON.stringify(row);
  }

  const updated = await prisma.payout.upsert({
    where: { affiliateId_month: { affiliateId, month } },
    create: { affiliateId, month, paid, paidAt: paid ? new Date() : null, snapshotJson },
    update: { paid, paidAt: paid ? new Date() : null, ...(snapshotJson ? { snapshotJson } : {}) },
  });
  res.json(updated);
});

// Set payout type (cash | product | split) and/or notes per affiliate/month.
router.post('/:affiliateId/settings', async (req, res) => {
  const affiliateId = Number(req.params.affiliateId);
  const month = req.body.month || currentMonth();
  const payoutType = ['cash', 'product', 'split'].includes(req.body.payoutType) ? req.body.payoutType : undefined;
  const notes = typeof req.body.notes === 'string' ? req.body.notes : undefined;
  const updated = await prisma.payout.upsert({
    where: { affiliateId_month: { affiliateId, month } },
    create: { affiliateId, month, payoutType: payoutType || 'cash', notes: notes || null },
    update: { ...(payoutType ? { payoutType } : {}), ...(notes !== undefined ? { notes } : {}) },
  });
  res.json(updated);
});

// Export the monthly batch as CSV so the owner can pay out in one go.
router.get('/export', async (req, res) => {
  const month = req.query.month || currentMonth();
  const { rows } = await computeMonthlyBatch(month);

  const headers = [
    'Affiliate', 'Tier', 'Discount Code', 'Payout Email', 'Orders', 'Sales',
    'Commission %', 'Commission Bump %', 'Commission', 'Ambassador Base',
    'View Bonus Cash', 'Leaderboard Cash', 'Cash Owed',
    'Product Value (Wholesale)', 'Product Value (Retail)', 'Payout Type', 'Paid', 'Notes',
  ];
  const esc = (v) => {
    const s = String(v ?? '');
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const lines = [headers.join(',')];
  for (const r of rows) {
    lines.push([
      r.name, r.tier, r.discountCode, r.payoutEmail, r.orderCount, r.sales,
      r.commissionPct, r.commissionBump, r.commission, r.ambassadorBase,
      r.viewBonusCash, r.leaderboardCash, r.cashOwed,
      r.productWholesale, r.productRetail, r.payoutType, r.paid ? 'yes' : 'no', r.notes,
    ].map(esc).join(','));
  }

  res.setHeader('Content-Type', 'text/csv; charset=utf-8');
  res.setHeader('Content-Disposition', `attachment; filename="athlyst-payouts-${month}.csv"`);
  res.send(lines.join('\n'));
});

export default router;
