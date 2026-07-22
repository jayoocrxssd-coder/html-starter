import { Router } from 'express';
import { prisma, getSettings } from '../db.js';

const router = Router();

// ---- General settings (commission defaults, budget ceiling, prizes) -------

router.get('/', async (req, res) => {
  const settings = await getSettings();
  const tiers = await prisma.bonusTier.findMany({ orderBy: { threshold: 'asc' } });
  res.json({ ...settings, bonusTiers: tiers });
});

router.put('/', async (req, res) => {
  const data = {};
  if (req.body.commissionDefaults !== undefined)
    data.commissionDefaults = JSON.stringify(req.body.commissionDefaults);
  if (req.body.monthlyBudgetCeiling !== undefined)
    data.monthlyBudgetCeiling = Number(req.body.monthlyBudgetCeiling) || 0;
  if (req.body.leaderboardPrizes !== undefined)
    data.leaderboardPrizes = JSON.stringify(req.body.leaderboardPrizes);

  await prisma.settings.upsert({ where: { id: 1 }, create: { id: 1, ...data }, update: data });
  const settings = await getSettings();
  res.json(settings);
});

// ---- Bonus tiers CRUD (configurable, never hardcoded) ---------------------

function cleanTier(body) {
  return {
    label: body.label?.trim() || `${body.threshold || 0} views`,
    threshold: Number(body.threshold) || 0,
    rewardDescription: body.rewardDescription?.trim() || '',
    cashAmount: Number(body.cashAmount) || 0,
    productWholesaleCost: Number(body.productWholesaleCost) || 0,
    productRetailValue: Number(body.productRetailValue) || 0,
    commissionBumpPct: Number(body.commissionBumpPct) || 0,
    sortOrder: Number(body.sortOrder) || 0,
  };
}

router.post('/tiers', async (req, res) => {
  const created = await prisma.bonusTier.create({ data: cleanTier(req.body) });
  res.status(201).json(created);
});

router.put('/tiers/:id', async (req, res) => {
  const id = Number(req.params.id);
  try {
    const updated = await prisma.bonusTier.update({ where: { id }, data: cleanTier(req.body) });
    res.json(updated);
  } catch (e) {
    if (e.code === 'P2025') return res.status(404).json({ error: 'Bonus tier not found.' });
    throw e;
  }
});

router.delete('/tiers/:id', async (req, res) => {
  const id = Number(req.params.id);
  // Detach from any logged posts first (SetNull isn't declared on SQLite here).
  await prisma.viewLog.updateMany({ where: { bonusTierId: id }, data: { bonusTierId: null } });
  await prisma.bonusTier.delete({ where: { id } }).catch(() => {});
  res.json({ ok: true });
});

export default router;
