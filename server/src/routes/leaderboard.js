import { Router } from 'express';
import { currentMonth } from '../db.js';
import { computeLeaderboard } from '../lib/engine.js';

const router = Router();

// Two rankings for a month (reset monthly by construction): views and sales.
router.get('/', async (req, res) => {
  const month = req.query.month || currentMonth();
  const board = await computeLeaderboard(month);
  res.json({ month, ...board });
});

export default router;
