# War Room — Beta

Static frontend for **War Room**, a personal business command center
(goals, tasks, invoices, and the AXIS AI assistant).
Backend: **Supabase** (auth + cloud sync). Hosting: **Vercel**.

## Layout

| Path | What it is |
|---|---|
| `index.html` | The War Room app, v6.1 — self-contained single-file build, served at `/` |
| `vercel.json` | Redirects the old `/app` path to `/` |
| `middleware.js` | Vercel Edge Middleware — security headers |
| `BACKEND.md` | Backend wiring checklist for the phased beta launch |
| `stratus_mobile (2) (1).html` | Unrelated Stratus mobile build (kept as-is) |

## Deploy

Push to the connected branch — Vercel serves the repo statically with the
app at `/`.

## Before inviting users

Work through `BACKEND.md`. The short version: create the `war_room_data`
table with RLS in Supabase (SQL included there), configure Supabase Auth
(site URL, email, Google provider), and add the production domain to the
Google OAuth client's JavaScript origins. AXIS proxy and team rooms are
Phase 2; Stripe is Phase 3.
