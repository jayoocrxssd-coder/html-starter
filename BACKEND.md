# War Room — Beta Launch Backend Checklist (Supabase + Vercel)

Current build: **Warroom v6.1** served at `/` (the old `/app` path redirects
home via `vercel.json`). The app is Supabase-native: auth (email/password +
Google) and cloud sync both go through Supabase project
`xtvvbylcejvkgvyrcist`. Everything below is what has to exist server-side
before real users touch it.

---

## Phase 1 — Go live (required before sharing any link)

### 1. Supabase database — create the sync table + RLS

The app upserts one row per user into `war_room_data`
(`user_id`, `data` = the serialized app state, `updated_at`).
Run this in the Supabase SQL editor:

```sql
create table if not exists public.war_room_data (
  user_id    uuid primary key references auth.users (id) on delete cascade,
  data       text,
  updated_at timestamptz not null default now()
);

alter table public.war_room_data enable row level security;

create policy "select own data" on public.war_room_data
  for select using (auth.uid() = user_id);
create policy "insert own data" on public.war_room_data
  for insert with check (auth.uid() = user_id);
create policy "update own data" on public.war_room_data
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "delete own data" on public.war_room_data
  for delete using (auth.uid() = user_id);
```

RLS is what makes the embedded anon key safe to ship — do not skip it.

### 2. Supabase Auth configuration

- **Site URL / Redirect URLs** (Auth → URL Configuration): set to the
  production domain so password-reset emails link to the right place.
- **Email provider**: enabled by default. Decide whether "Confirm email"
  is on (safer) or off (less signup friction for beta).
- **Google provider**: the app signs in with `signInWithIdToken` using
  Google Identity Services client
  `190616282170-hkcq273fdvm3740p6h222u6pohlbjdih.apps.googleusercontent.com`.
  - In Supabase: Auth → Providers → Google → enable, and add that client ID
    to **Authorized Client IDs**.
  - In Google Cloud Console → Credentials → that OAuth client: add the
    production domain (and `*.vercel.app` preview domain) to
    **Authorized JavaScript origins**.

### 3. Vercel

- Import this repo, production branch = your default branch.
- Attach the custom domain. The app is served at `/`; `vercel.json`
  already redirects `/app` → `/`; `middleware.js` already sets security
  headers.

### 4. Legal pages

The auth gate links to **Terms of Service** and **Privacy Policy** — those
pages need to exist (or the links need a target) before public signups.

---

## Phase 2 — Beta hardening

### 5. AXIS AI proxy (Anthropic)

The app currently calls `api.anthropic.com` **directly from the browser**
with a user-pasted `sk-ant` key (session-only). Works day one for users who
bring their own key; for everyone else:

- Vercel function `api/axis.js` holding `ANTHROPIC_API_KEY` as an env var,
  verifying the caller's Supabase JWT (`supabase.auth.getUser(token)`),
  enforcing per-user daily quotas, forwarding to Anthropic.
- Point the app's AI fetch at `/api/axis` (one constant +
  `getAIFetchHeaders()` change), keep paste-your-own-key as fallback.
- Model is pinned to `claude-sonnet-4-20250514`; pick the beta model and
  `max_tokens` budget deliberately (cost control).

### 6. Team rooms / invite links — currently disabled

`handlePendingJoin` is stubbed (`var db = null; // TODO: migrate warrooms
to Supabase Realtime`), so `?join=<roomId>` links silently do nothing.
Solo use is unaffected. To enable multiplayer:

- Tables: `warrooms` (id, owner, name) + `warroom_members`
  (room_id, user_id, role, joined_at) with membership-scoped RLS.
- Live sync via Supabase Realtime (`postgres_changes` on the room's data).

Either ship Phase 1 as solo-only (recommended) or build this first.

### 7. Google Drive backup (optional feature in Settings)

Uses the same Google client + `drive.file` scope. If keeping it:
OAuth consent screen must be published (testing mode = 100 users max +
"unverified app" warning) and the Drive API enabled. Alternative: replace
with Supabase Storage snapshots and delete the Google dependency.

### 8. Ops

- Scheduled Supabase backups (dashboard → Database → Backups).
- Error monitoring (e.g. Sentry snippet) once real users are in.

---

## Phase 3 — Paid launch

The in-app plan gate (Personal / Small Business / Enterprise, founder
pricing) is **UI only** — no payment rails exist.

- Stripe Products/Prices for the tiers (+ annual), Checkout session via a
  Vercel function, Customer Portal, webhook writing `plan` to a `profiles`
  table in Supabase.
- Entitlement enforcement in RLS + the AXIS proxy quotas.

---

## Quick reference — what the frontend already talks to

| Service | Used for | Status |
|---|---|---|
| Supabase Auth (`xtvvbylcejvkgvyrcist`) | Email + Google sign-in | Needs providers + URL config |
| Supabase Postgres | Cloud sync (`war_room_data`) | Needs table + RLS (SQL above) |
| Google Identity Services | Google login + Drive backup | Needs JS origins (+ consent screen if Drive kept) |
| Anthropic API | AXIS assistant | Direct-from-browser today; proxy in Phase 2 |
| Stripe | Billing (Phase 3) | Not wired at all |
| Vercel | Hosting, redirects, headers | Repo-ready |
