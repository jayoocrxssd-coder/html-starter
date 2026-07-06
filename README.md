# War Room — Beta

Static frontend for **War Room**, a personal business command center
(goals, tasks, invoices, team rooms, and the AXIS AI assistant).
Deployed on Vercel.

## Layout

| Path | What it is |
|---|---|
| `index.html` | Landing page (beta) — links into the app |
| `app/index.html` | The War Room app (self-contained single-file build, v6) |
| `middleware.js` | Vercel Edge Middleware — security headers |
| `BACKEND.md` | Backend wiring checklist for the phased beta launch |
| `stratus_mobile (2) (1).html` | Unrelated Stratus mobile build (kept as-is) |

## Deploy

Push to the connected branch — Vercel serves the repo statically:
landing page at `/`, app at `/app/`.

## Before inviting users

Work through `BACKEND.md`. The short version: Firebase auth domains +
Firestore security rules, Google OAuth origins/consent, and an `/api/axis`
proxy for the Anthropic key. Billing (Stripe) is Phase 3.
