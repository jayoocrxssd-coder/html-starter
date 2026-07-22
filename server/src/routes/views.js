import { Router } from 'express';
import { prisma, monthKey } from '../db.js';
import { tierForViews } from '../lib/engine.js';

const router = Router();

// Auto-tag which bonus tier a post hit, given current tier config.
async function tagTier(viewCount) {
  const tiers = await prisma.bonusTier.findMany({ orderBy: { threshold: 'asc' } });
  const tier = tierForViews(tiers, viewCount);
  return tier ? tier.id : null;
}

// List logged posts, newest first. Optional ?month= & ?affiliateId= filters.
router.get('/', async (req, res) => {
  const where = {};
  if (req.query.month) where.month = req.query.month;
  if (req.query.affiliateId) where.affiliateId = Number(req.query.affiliateId);
  const views = await prisma.viewLog.findMany({
    where,
    orderBy: { postedAt: 'desc' },
    include: { affiliate: { select: { name: true, discountCode: true } }, bonusTier: true },
  });
  res.json(views);
});

router.post('/', async (req, res) => {
  const affiliateId = Number(req.body.affiliateId);
  const viewCount = Number(req.body.viewCount) || 0;
  const postedAt = req.body.postedAt ? new Date(req.body.postedAt) : new Date();
  if (!affiliateId) return res.status(400).json({ error: 'Affiliate is required.' });
  if (!req.body.postLink?.trim()) return res.status(400).json({ error: 'Post link is required.' });

  const created = await prisma.viewLog.create({
    data: {
      affiliateId,
      postLink: req.body.postLink.trim(),
      platform: req.body.platform?.trim() || '',
      viewCount,
      postedAt,
      month: monthKey(postedAt),
      verified: Boolean(req.body.verified),
      bonusTierId: await tagTier(viewCount),
    },
    include: { affiliate: { select: { name: true } }, bonusTier: true },
  });
  res.status(201).json(created);
});

router.put('/:id', async (req, res) => {
  const id = Number(req.params.id);
  const viewCount = Number(req.body.viewCount) || 0;
  const postedAt = req.body.postedAt ? new Date(req.body.postedAt) : new Date();
  try {
    const updated = await prisma.viewLog.update({
      where: { id },
      data: {
        postLink: req.body.postLink?.trim(),
        platform: req.body.platform?.trim() || '',
        viewCount,
        postedAt,
        month: monthKey(postedAt),
        verified: Boolean(req.body.verified),
        bonusTierId: await tagTier(viewCount),
      },
      include: { affiliate: { select: { name: true } }, bonusTier: true },
    });
    res.json(updated);
  } catch (e) {
    if (e.code === 'P2025') return res.status(404).json({ error: 'Logged post not found.' });
    throw e;
  }
});

// Quick verify toggle (the key business-rule checkbox).
router.post('/:id/verify', async (req, res) => {
  const id = Number(req.params.id);
  const updated = await prisma.viewLog.update({ where: { id }, data: { verified: req.body.verified !== false } });
  res.json(updated);
});

router.delete('/:id', async (req, res) => {
  const id = Number(req.params.id);
  await prisma.viewLog.delete({ where: { id } }).catch(() => {});
  res.json({ ok: true });
});

export default router;
