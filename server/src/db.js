import { PrismaClient } from '@prisma/client';

// Single shared Prisma client for the whole server.
export const prisma = new PrismaClient();

// ---- shared helpers --------------------------------------------------------

// "YYYY-MM" bucket for a Date (used for all monthly rollups).
export function monthKey(date) {
  const d = date instanceof Date ? date : new Date(date);
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, '0')}`;
}

// The current month key (UTC).
export function currentMonth() {
  return monthKey(new Date());
}

// Load the singleton settings row, creating it with defaults on first run.
export async function getSettings() {
  let s = await prisma.settings.findUnique({ where: { id: 1 } });
  if (!s) s = await prisma.settings.create({ data: { id: 1 } });
  return {
    ...s,
    commissionDefaults: JSON.parse(s.commissionDefaults || '{}'),
    leaderboardPrizes: JSON.parse(s.leaderboardPrizes || '[]'),
  };
}
