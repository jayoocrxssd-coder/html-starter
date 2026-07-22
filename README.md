# ATHLYST Affiliate Dashboard — Phase 1 (Owner dashboard)

An embedded Shopify admin app that houses your affiliates and handles everything
Shopify Collabs does **not**: view-based bonuses, a monthly leaderboard, and
payout calculation. It pulls live sales from your store and matches each order
to an affiliate by their discount code.

**Phase 1 = the owner-facing dashboard only** (features 1–5 + settings). The
affiliate-facing login portal is Phase 2 and is intentionally not built yet.

---

## What's in the box

| # | Feature | Where |
|---|---------|-------|
| 1 | **Affiliate roster** — add / edit / archive, all fields, tiers, unique code | `Affiliates` |
| 2 | **Live sales pull** — Shopify Admin API (GraphQL), matched by discount code, auto commission math | `Sales` |
| 3 | **View logging** — manual post entry, auto-tagged bonus tier, **verified** checkbox | `View logging` |
| 4 | **Monthly leaderboard** — two rankings (views + sales), reset monthly | `Leaderboard` |
| 5 | **Payout calculator** — commission + view bonuses + ambassador base + leaderboard prizes, cash vs product split, mark paid, CSV export, budget ceiling warning | `Payouts` |
| ⚙ | **Configurable settings** — commission defaults, editable bonus tiers, leaderboard prizes, budget ceiling | `Settings` |

### Business rules baked in
- A view counts toward a bonus **only if `verified`** is ticked (you confirm the
  post features the product *and* the code). Unverified posts still appear on the
  leaderboard but earn no bonus.
- Product-based rewards are tracked at **wholesale cost** (your budget math),
  kept separate from their **retail value** (what the affiliate perceives).
- Payouts run **once monthly as one batch** — export the CSV, pay everyone, then
  mark each as paid. Nothing is paid automatically.
- The `50K+` view tier applies a **commission bump** on top of the base rate.

---

## The stack (and what it costs)

| Layer | Choice | Monthly cost |
|-------|--------|--------------|
| Backend | **Node + Express** | — |
| Database | **SQLite via Prisma** (one file; swap to Postgres later with zero code changes) | **$0** |
| Frontend | **React + Vite + Shopify Polaris** (native admin look) | — |
| Shopify | **Partner account + custom app** | **$0** (both free) |
| Hosting | Render / Fly.io / Railway **hobby tier** | **~$0–7/mo** |

**Total to run this:** effectively **$0**, up to ~$7/mo once you host it on an
always-on box. The only thing that ever costs money is hosting — the Shopify
Partner account, the custom app, and SQLite are all free.

> Moving to Postgres later: change `provider` in `server/prisma/schema.prisma`
> to `postgresql`, point `DATABASE_URL` at your database, run `prisma migrate`.
> No application code changes.

---

## Run it locally

```bash
# from the repo root — installs both apps, sets up the DB, seeds demo data
npm run setup

# two terminals:
npm run dev:server   # API on http://localhost:3001
npm run dev:web      # dashboard on http://localhost:5173  (proxies /api)
```

Open **http://localhost:5173**. It's pre-loaded with demo affiliates, sales, and
posts so every screen is populated. To wipe the demo data and start clean, edit
or empty `server/prisma/seed.js` and re-run `npm run seed` (it clears first).

### Production-style (single origin, same as embedded)

```bash
npm run build     # builds the React app into web/dist
npm start         # Express serves the API *and* the built dashboard on :3001
```

---

## Connecting your live Shopify store (feature 2)

The app runs fully without this — but here's how to turn on the live sales pull.
**These are the steps only you can do** (they need your store login):

1. In your Shopify admin: **Settings → Apps and sales channels → Develop apps →
   Create an app**. Name it `ATHLYST Affiliates`.
2. **Configuration → Admin API integration → Configure** and enable these scopes:
   `read_orders`, `read_discounts` (add `read_customers` if you later want more).
3. **Install app**, then **API credentials → Admin API access token → Reveal**.
4. Copy `server/.env.example` to `server/.env` and fill in:
   ```env
   SHOPIFY_SHOP="athlyst.myshopify.com"
   SHOPIFY_ADMIN_TOKEN="shpat_xxxxxxxxxxxxxxxxxxxxxxxx"
   SHOPIFY_API_VERSION="2025-01"
   ```
5. Restart the server. The **Sales** page will show *Connected*, and
   **Sync sales from Shopify** will pull that month's orders and match them to
   affiliates by discount code.

> Matching uses the order's **subtotal after discounts** as the commissionable
> amount. Sync is idempotent — re-running never double-counts an order.

### Turning it into a true *embedded* app (final Phase 1 step)

The dashboard is already built to be embedded (single-origin, Polaris UI). To
put it inside the Shopify admin iframe:

1. Register the app in your **Shopify Partner** account (Partners dashboard →
   Apps → Create app → *custom/private*), pointing the App URL at your hosted
   server.
2. Add App Bridge at the top of `web/src/main.jsx` (wrap `<AppProvider>` with
   `@shopify/app-bridge-react`'s provider using your API key + host param) and
   Shopify's OAuth on the server. This handshake needs your Partner credentials
   and a public HTTPS URL, so it's the one piece to finish on your own machine
   with `shopify app dev`.

Everything the embed needs (same-origin API, Polaris look, no external calls in
the UI) is already in place — this is a wrapper, not a rewrite.

---

## Project layout

```
server/                 Express API + Prisma + Shopify service
  prisma/schema.prisma  data model (affiliates, views, sales, tiers, payouts, settings)
  prisma/seed.js        demo data
  src/lib/engine.js     payout + leaderboard calculation (business rules)
  src/lib/shopify.js    Admin API GraphQL sales pull (env-gated)
  src/routes/*.js       REST API per feature
web/                    React + Vite + Polaris dashboard
  src/pages/*.jsx       Overview, Affiliates, Views, Sales, Leaderboard, Payouts, Settings
```

## API quick reference

```
GET/POST/PUT   /api/affiliates            roster CRUD  (+ /:id/archive)
GET/POST/PUT   /api/views                 logged posts (+ /:id/verify, DELETE)
GET            /api/sales                  matched sales for a month
GET            /api/sales/status           Shopify connection status
POST           /api/sales/sync             pull + match orders for a month
GET            /api/leaderboard            two rankings for a month
GET            /api/payouts                payout batch + budget for a month
POST           /api/payouts/:id/paid       mark paid / unpaid (snapshots breakdown)
POST           /api/payouts/:id/settings   payout type (cash|product|split) + notes
GET            /api/payouts/export         monthly batch as CSV
GET/PUT        /api/settings               commission defaults, ceiling, prizes
POST/PUT/DELETE /api/settings/tiers        bonus-tier CRUD
```

---

## Out of scope for Phase 1 (as briefed)
- Affiliate-facing login portal → **Phase 2**
- Automated payouts (you pay manually from the exported CSV)
- Public App Store listing (this is a private/custom app for your store only)
