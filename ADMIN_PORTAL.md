# WAR ROOM — Command Portal

**File:** `admin.html`  
**Branch:** `claude/stoic-albattani-25nJI`  
**Status:** Base complete · Mock data cleared · 20 no-wiring improvements applied  
**Last updated:** May 31, 2026

---

## Overview

The WAR ROOM Command Portal is a single-file internal admin dashboard (`admin.html`) for managing the WAR ROOM platform. It requires no backend to open and run — all UI, logic, and routing is self-contained. Data arrays are empty and ready to be wired to Supabase and Stripe at launch.

Design matches the main WAR ROOM app exactly — Syne + DM Mono fonts, obsidian dark token system, same CSS variable names, same badge/chip patterns.

---

## Access

Three worker roles are pre-configured. Credentials should be replaced with real auth before launch.

| Role | Email | Password | Restrictions |
|---|---|---|---|
| Owner | `admin@warroom.app` | `warroom2026` | Full access |
| Ops | `ops@warroom.app` | `ops2026` | Full access |
| Support | `support@warroom.app` | `support2026` | Revenue tab locked |

> ⚠️ These credentials are stored in the HTML source. Move to Supabase Auth before any real deployment.

---

## Views

### ⬡ Overview
Platform health at a glance.

- **Stat cards:** Total Users, Active This Week, MRR, Churn Rate
- **Revenue 30-day chart** — MRR trend (SVG, connects to Stripe)
- **Plan Mix bars** — Free / Pro / Enterprise breakdown
- **Recent Signups feed** — last 5 users
- **Signups 7-day bar chart** — daily new users
- **Quick Stats panel** — ARR, ARPU, Trial Conversions, Failed Payments, Refunds, Support Tickets (live count)

All values show `—` until connected to a data source.

---

### ◈ Revenue
MRR, transactions, and payment health.

- **3 stat cards:** MRR, New MRR (30d), Churned MRR (30d)
- **MRR timeline chart** (30-day SVG line chart)
- **Recent Transactions table** — User, Plan, Amount, Date, Status, Retry/Refund actions
- **Failed Payments panel** — list with per-row Retry button

Connects to: **Stripe**

---

### ◉ Users
Manage accounts, plans, and access.

- **Search** by name or email
- **Filter chips:** All / Free / Pro / Enterprise / Suspended
- **Sortable columns:** Name, Email, Plan, Joined, Last Active, Status
- **Row actions:** View, Change Plan, Suspend/Reinstate
- **Add User button** — modal with Name, Email, Plan, Status fields
  - Validates email format
  - Checks for duplicate emails
  - Zeroed usage stats on creation
- **User detail side panel** — slides in on row click
  - Account details, usage stats (businesses, missions, P&L exports, AXIS sessions)
  - Actions: Change Plan, Impersonate, Password Reset, Suspend

Connects to: **Supabase** (user data), **Stripe** (plan changes)

---

### ◇ Support
User support tickets and requests.

- **3 stat cards:** Open Tickets (live count), Avg Response Time, Resolved (30d)
- **Search** by user, subject, or ticket ID
- **Filter chips:** All / Open / In Progress / Resolved
- **Table columns:** Ticket ID, User, Subject, Priority, Status, Created, Assigned To, Actions
- **Priority chips:** Low (blue) · Medium (amber) · High (red) · Urgent (pink)
- **Status badges:** open · in-progress · resolved (dedicated classes, not reused from revenue)
- **Row actions:** View (detail panel stub), Resolve (updates status in place)
- **Export CSV stub** in toolbar

Connects to: **Supabase** (ticket table or external support tool webhook)

---

### ◎ Activity
Live platform event feed.

- **Filter chips:** All / Signups / Upgrades / Cancels / Payments
- **Event types:** signup · upgrade · cancel · payment · login · export
- **Live indicator** in toolbar
- Auto-refreshes every 30 seconds

Connects to: **Supabase Realtime** (subscription to events table)

---

### ◈ Workers
Admin team access and audit trail.

- **Team Access table** — Name, Role, Last Login, Access toggle
  - Toggle fires a confirmation dialog before revoking access
- **Credentials panel** — shows current login credentials (replace before launch)
- **Audit Log table** — Worker, Action, Target, Time
  - Starts empty, populated as workers take actions

---

### ◫ Integrations
Connected services and API keys.

8 pre-built service cards — all disconnected by default:

| Service | Category | Connects to |
|---|---|---|
| Stripe | Payments | Subscriptions, charges, webhooks |
| Supabase | Database & Auth | User data, realtime, auth |
| Netlify | Hosting | Deploy hooks |
| Resend | Email | Transactional emails, password resets |
| AXIS AI | AI Layer | AXIS co-pilot inside WAR ROOM |
| Vercel | Hosting | Edge network, deployments |
| Twilio | SMS/Comms | 2FA, SMS notifications |
| PostHog | Analytics | Product analytics, user behavior |

**Connect flow:** Click Connect → enter API Key (+ optional Secret Key + Webhook URL) → Save. Card flips to connected state. Disconnect requires confirmation.

> ⚠️ API keys are held in memory only and lost on page reload. Persist to Supabase Vault or environment variables before launch.

---

## Features Implemented (No Wiring Required)

| Feature | Detail |
|---|---|
| Auth gate | Login with role-based access control |
| Light/dark mode toggle | `◑` in topbar, full token system swap |
| Escape key | Closes any open modal or detail panel |
| Focus trap | Tab stays inside open modals (WCAG 2.1 AA) |
| `aria-label` | All icon buttons labeled for screen readers |
| `aria-disabled` | Set on role-blocked nav items |
| XSS escape | `he()` helper sanitizes all user strings before innerHTML |
| Email validation | Add User rejects malformed emails |
| Duplicate email check | Prevents same email being added twice |
| Webhook URL validation | Format-checked before saving integration config |
| Confirmation dialog | Fires before worker revoke and integration disconnect |
| Toast queue | Animates out before showing next — no abrupt cuts |
| Filter/sort state reset | Clean slate on every logout |
| Sort indicators clear | Cleared when filter changes — no stale headers |
| Revenue tab restriction | Uses `data-section` attribute — not fragile text matching |
| Support view search | Filters by user, subject, or ticket ID |
| Support CSV stub | Export button in toolbar |
| Quick Stats ticket count | Live count from `SUPPORT_TICKETS` array |
| `renderIntegrations()` on login | Grid renders immediately after auth |
| `renderSupport()` on login | View ready without needing to navigate there first |

---

## Post-Wiring TODO

Everything below requires a live backend integration before it becomes functional.

### Supabase (Auth + Database)

- [ ] Replace hardcoded worker credentials with Supabase Auth session
- [ ] Load `USERS[]` from Supabase `profiles` table
- [ ] Persist integration API keys in Supabase Vault (never in client-side JS)
- [ ] Impersonate User — Supabase admin token exchange
- [ ] Send Password Reset — `supabase.auth.resetPasswordForEmail()`
- [ ] Real activity stream — Supabase Realtime subscription to `events` table
- [ ] Real support tickets — Supabase `tickets` table or webhook from Linear/Intercom
- [ ] Audit log — write worker actions to a Supabase `audit_log` table

### Stripe

- [ ] Change Plan — `stripe.subscriptions.update()`
- [ ] MRR / ARR / Churn stat cards — Stripe Billing metrics API
- [ ] Revenue timeline chart — `stripe.balanceTransactions.list()`
- [ ] Transaction table — `stripe.paymentIntents.list()` or `charges.list()`
- [ ] Failed payments + Retry — `stripe.invoices.list({ status: 'open' })` + `invoices.pay()`
- [ ] New MRR / Churned MRR — Stripe `customer.subscription.updated` / `deleted` webhooks

### Resend (Email)

- [ ] Password Reset button — `resend.emails.send()` with a reset link
- [ ] Welcome email on manual user creation via Add User modal

### PostHog (Analytics)

- [ ] Active This Week stat — PostHog events query or Supabase `last_seen` timestamp
- [ ] Trial conversion rate — PostHog funnel or computed from Supabase subscription data

### CSV Exports

- [ ] Users CSV — `USERS[]` array is the data source; download works once it's populated
- [ ] Support Tickets CSV — same pattern as Users

---

## File Structure

```
html-starter/
├── index.html          ← WAR ROOM landing page
├── app.html            ← WAR ROOM main app
├── admin.html          ← Command Portal (this file)
├── middleware.js       ← Vercel Edge Middleware (security headers)
├── package.json
└── ADMIN_PORTAL.md     ← This document
```

---

## Design Tokens (Obsidian Dark — Admin Default)

| Token | Value | Use |
|---|---|---|
| `--bg` | `#000000` | Page background |
| `--surface` | `#111111` | Cards, panels, sidebar |
| `--ink` | `#f0f0ee` | Primary text |
| `--ink2` | `#9a9a98` | Secondary text |
| `--ink3` | `#5a5a58` | Muted text, labels |
| `--green` | `#3de090` | Success, active states |
| `--red` | `#f06860` | Errors, danger actions |
| `--amber` | `#f0b030` | Warnings, owner role |
| `--blue` | `#5ab0f8` | Info, free plan |
| `--violet` | `#9c6ee8` | Pro plan |
| `--pink` | `#f068a8` | Urgent priority |

Light mode (toggle via `◑` in topbar) uses the Stratus warm cream palette — same token names, swapped values.

---

## Build Notes

- Single HTML file — no build step, no dependencies, no bundler
- All charts are pure SVG — no chart library needed
- Fonts loaded from Google Fonts CDN (Syne + DM Mono)
- Data arrays (`USERS`, `SUPPORT_TICKETS`, `ACTIVITY_EVENTS`, `TRANSACTIONS`) are empty — populate via API calls at integration points marked with `// TODO: replace with API call`
- `he()` helper must wrap all user-supplied strings before any `innerHTML` assignment
- `showConfirm(title, body, callback)` is a reusable confirmation dialog — use it for any destructive action
- `trapFocus(modalCardEl)` is a reusable focus trap — call it on every new modal added

---

*WAR ROOM Command Portal — internal use only*
