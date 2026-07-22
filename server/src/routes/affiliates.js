import { Router } from 'express';
import { prisma } from '../db.js';

const router = Router();

const TIERS = ['Athlete', 'Influencer', 'Ambassador'];

function clean(body) {
  return {
    name: body.name?.trim(),
    email: body.email?.trim() || '',
    payoutEmail: body.payoutEmail?.trim() || '',
    country: body.country?.trim() || null,
    platform: body.platform?.trim() || null,
    handle: body.handle?.trim() || null,
    tier: TIERS.includes(body.tier) ? body.tier : 'Athlete',
    discountCode: body.discountCode?.trim(),
    commissionPct: Number(body.commissionPct) || 0,
    monthlyBase: Number(body.monthlyBase) || 0,
    status: body.status === 'inactive' ? 'inactive' : 'active',
  };
}

// List (roster). ?includeArchived=1 to show archived too.
router.get('/', async (req, res) => {
  const where = req.query.includeArchived === '1' ? {} : { archived: false };
  const affiliates = await prisma.affiliate.findMany({ where, orderBy: { name: 'asc' } });
  res.json(affiliates);
});

router.post('/', async (req, res) => {
  const data = clean(req.body);
  if (!data.name) return res.status(400).json({ error: 'Name is required.' });
  if (!data.discountCode) return res.status(400).json({ error: 'Discount code is required.' });
  try {
    const created = await prisma.affiliate.create({ data });
    res.status(201).json(created);
  } catch (e) {
    if (e.code === 'P2002') return res.status(409).json({ error: `Discount code "${data.discountCode}" is already in use.` });
    throw e;
  }
});

router.put('/:id', async (req, res) => {
  const id = Number(req.params.id);
  const data = clean(req.body);
  if (!data.name) return res.status(400).json({ error: 'Name is required.' });
  if (!data.discountCode) return res.status(400).json({ error: 'Discount code is required.' });
  try {
    const updated = await prisma.affiliate.update({ where: { id }, data });
    res.json(updated);
  } catch (e) {
    if (e.code === 'P2002') return res.status(409).json({ error: `Discount code "${data.discountCode}" is already in use.` });
    if (e.code === 'P2025') return res.status(404).json({ error: 'Affiliate not found.' });
    throw e;
  }
});

// Archive / unarchive (soft delete — keeps history for past payouts).
router.post('/:id/archive', async (req, res) => {
  const id = Number(req.params.id);
  const archived = req.body.archived !== false;
  const updated = await prisma.affiliate.update({ where: { id }, data: { archived } });
  res.json(updated);
});

export default router;
