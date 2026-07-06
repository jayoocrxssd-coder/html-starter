# War Room — Beta

**Warroom by aionvsn** — a real-time business command center (goals, tasks,
invoices, budget, and the AXIS AI assistant).
Marketing site + app + serverless API in one repo.
Backend: **Supabase**. Hosting: **Vercel**.

## Layout

| Path | What it is |
|---|---|
| `index.html` | Landing page — hero, features, pricing, FAQ, beta-request + sign-in modals |
| `features.html`, `contact.html`, `donate.html`, `partners.html` | Marketing pages |
| `access.html` | Post-login "access granted" transition → `/app/` |
| `forgot-password.html`, `reset-password.html` | Password recovery flow |
| `app/index.html` | The Warroom app (v6.1, self-contained single-file build) |
| `api/axis.js` | AXIS AI proxy → Anthropic (uses `ANTHROPIC_API_KEY` env var) |
| `api/forgot-password.js` | Sends Supabase password-recovery emails |
| `middleware.js` | Edge middleware — security headers |
| `BACKEND.md` | **The launch runbook — start here** |

## Deploy

Push to the connected branch; Vercel serves the static pages and deploys
`/api/*` as functions. Set `ANTHROPIC_API_KEY` in Vercel project settings
to enable AXIS for all users.

## Launch

Follow `BACKEND.md` top to bottom — Supabase SQL, auth config, Google
OAuth origins, Vercel env var, then the end-to-end test loop.
