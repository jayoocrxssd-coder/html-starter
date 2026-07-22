import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import fs from 'node:fs';

import affiliates from './routes/affiliates.js';
import views from './routes/views.js';
import sales from './routes/sales.js';
import leaderboard from './routes/leaderboard.js';
import payouts from './routes/payouts.js';
import settings from './routes/settings.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
app.use(cors());
app.use(express.json());

app.get('/api/health', (req, res) => res.json({ ok: true, service: 'athlyst-affiliate-dashboard' }));
app.use('/api/affiliates', affiliates);
app.use('/api/views', views);
app.use('/api/sales', sales);
app.use('/api/leaderboard', leaderboard);
app.use('/api/payouts', payouts);
app.use('/api/settings', settings);

// Central error handler so route bugs return JSON, not an HTML stack page.
app.use((err, req, res, next) => {
  console.error(err);
  if (res.headersSent) return next(err);
  res.status(500).json({ error: err.message || 'Internal server error' });
});

// In production, serve the built React app (web/dist) from the same origin —
// this is also what gets embedded in the Shopify admin iframe in Phase 1.
const webDist = path.resolve(__dirname, '../../web/dist');
if (fs.existsSync(webDist)) {
  app.use(express.static(webDist));
  app.get('*', (req, res, next) => {
    if (req.path.startsWith('/api/')) return next();
    res.sendFile(path.join(webDist, 'index.html'));
  });
}

const port = process.env.PORT || 3001;
app.listen(port, () => console.log(`ATHLYST affiliate API listening on http://localhost:${port}`));
