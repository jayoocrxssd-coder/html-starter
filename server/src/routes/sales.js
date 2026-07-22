import { Router } from 'express';
import { prisma, monthKey, currentMonth } from '../db.js';
import { isConfigured, syncSalesForMonth, shopifyConfig } from '../lib/shopify.js';

const router = Router();

// Connection status for the UI (drives the "Sync sales" button state).
router.get('/status', (req, res) => {
  const { shop, version } = shopifyConfig();
  res.json({ connected: isConfigured(), shop: shop || null, apiVersion: version });
});

// List matched sales for a month, grouped per affiliate for display.
router.get('/', async (req, res) => {
  const month = req.query.month || currentMonth();
  const sales = await prisma.sale.findMany({
    where: { month },
    orderBy: { orderedAt: 'desc' },
    include: { affiliate: { select: { name: true, commissionPct: true } } },
  });
  res.json(sales);
});

// Pull live sales from Shopify for a month and match to affiliates by code.
router.post('/sync', async (req, res) => {
  const month = req.body.month || currentMonth();
  try {
    const summary = await syncSalesForMonth(month);
    res.json(summary);
  } catch (e) {
    if (e.code === 'NOT_CONFIGURED') return res.status(400).json({ error: e.message, code: 'NOT_CONFIGURED' });
    res.status(502).json({ error: e.message });
  }
});

// Manual sale entry — handy for testing or one-off corrections without Shopify.
router.post('/', async (req, res) => {
  const affiliateId = Number(req.body.affiliateId);
  const amount = Number(req.body.amount) || 0;
  const orderedAt = req.body.orderedAt ? new Date(req.body.orderedAt) : new Date();
  if (!affiliateId) return res.status(400).json({ error: 'Affiliate is required.' });
  const affiliate = await prisma.affiliate.findUnique({ where: { id: affiliateId } });
  if (!affiliate) return res.status(404).json({ error: 'Affiliate not found.' });
  const created = await prisma.sale.create({
    data: {
      affiliateId,
      shopifyOrderId: `manual:${Date.now()}:${affiliateId}`,
      orderName: req.body.orderName || 'manual',
      discountCode: affiliate.discountCode,
      amount,
      orderedAt,
      month: monthKey(orderedAt),
    },
  });
  res.status(201).json(created);
});

export default router;
