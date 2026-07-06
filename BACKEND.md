# War Room — Beta Launch Runbook (Supabase + Vercel)

**Layout:** marketing site at `/` (8 pages), the Warroom v6.1 app at `/app/`,
serverless functions in `/api/`. Everything below is ordered — do the steps
top to bottom and the beta is live.

## What is already wired in code (no action needed)

- Landing **Sign in** → Supabase password auth → `access.html` animation → `/app/`
  (the session persists in localStorage, so the app picks it up automatically).
- Landing + contact **Request beta access** forms → insert into `beta_requests`.
- **Contact** form → `contact_messages`. **Partners** form → `partner_inquiries`.
- **Forgot password** page → `/api/forgot-password` → Supabase recovery email
  → `/reset-password.html` (fully wired, including token handling).
- **AXIS AI** in the app now calls `/api/axis` (proxy). Users can paste their
  own Anthropic key day one; set `ANTHROPIC_API_KEY` in Vercel and it works
  for everyone, with per-IP rate limiting and a max-token cap on your key.
- Old `/app` redirect config removed; app genuinely lives at `/app/`.

---

## STEP 1 — Supabase SQL (5 min, blocking)

SQL Editor → run all of this:

```sql
-- App cloud sync: one row per user
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

-- Beta access requests (landing + contact page forms)
create table if not exists public.beta_requests (
  id bigint generated always as identity primary key,
  first_name text, last_name text,
  email text not null,
  company text, use_case text,
  marketing_opt_in boolean not null default false,
  source text,
  created_at timestamptz not null default now()
);
alter table public.beta_requests enable row level security;
create policy "anyone can request access" on public.beta_requests
  for insert to anon, authenticated with check (true);

-- Contact form
create table if not exists public.contact_messages (
  id bigint generated always as identity primary key,
  first_name text, last_name text,
  email text not null,
  subject text, message text,
  created_at timestamptz not null default now()
);
alter table public.contact_messages enable row level security;
create policy "anyone can send a message" on public.contact_messages
  for insert to anon, authenticated with check (true);

-- Partner / creator applications
create table if not exists public.partner_inquiries (
  id bigint generated always as identity primary key,
  first_name text, last_name text,
  email text not null,
  platform text, handle text, audience_size text, details text,
  created_at timestamptz not null default now()
);
alter table public.partner_inquiries enable row level security;
create policy "anyone can apply" on public.partner_inquiries
  for insert to anon, authenticated with check (true);
```

No select policies on the three form tables = the public can submit but
never read them. You read them in the Supabase dashboard (Table Editor).

## STEP 2 — Supabase Auth config (5 min, blocking)

Authentication → URL Configuration:
- **Site URL** = your production domain (e.g. `https://warroom.aionvsn.com`)
- **Redirect URLs**: add `https://<your-domain>/reset-password.html`
  (password-reset emails will not land on the page without this).

Authentication → Providers:
- **Email**: on by default. Decide if "Confirm email" is on (safer) or off
  (fewer signup steps during beta).

## STEP 3 — Google sign-in for the app (10 min, only blocks the Google button)

- Supabase → Auth → Providers → **Google**: enable; add client ID
  `190616282170-hkcq273fdvm3740p6h222u6pohlbjdih.apps.googleusercontent.com`
  to Authorized Client IDs.
- Google Cloud Console → Credentials → that client → **Authorized JavaScript
  origins**: add your production domain and your `*.vercel.app` domain.

Email sign-in works even if you skip this step.

## STEP 4 — Vercel (10 min, blocking)

1. Merge the working branch into your default branch.
2. Import the repo at vercel.com (if not already) — it deploys statically
   with `/api/*` as serverless functions automatically.
3. Attach your custom domain.
4. Project → Settings → Environment Variables:
   - `ANTHROPIC_API_KEY` = your key from console.anthropic.com
     (optional — without it AXIS is bring-your-own-key only).

## STEP 5 — Legal pages (blocking for public traffic)

The app's signup gate links to Terms of Service and Privacy Policy.
Generate both, host them anywhere (two more static pages in this repo is
fine), and make sure the links resolve.

## STEP 6 — Test the loop end to end (15 min)

1. Open the landing page → submit **Request beta access** → confirm the row
   appears in `beta_requests` in the Supabase dashboard.
2. Supabase → Authentication → **Add user / Invite** yourself.
3. Landing → **Sign in** → confirm you pass through `access.html` into the
   app and land signed-in.
4. In the app: add data, sign out, sign back in on another device/browser —
   confirm it synced.
5. **Forgot password** → confirm the email arrives and the reset page works.
6. If you set `ANTHROPIC_API_KEY`: open AXIS in the app and send a message.

## STEP 7 — Run the beta in phases

The invite-only mechanics are already the phasing tool:

- **Phase 1 (friends & family):** share the URL; approve requests by
  creating users manually in Supabase Auth (Invite user → they get an email).
- **Phase 2 (waves):** work through `beta_requests` in batches; invite each
  cohort from the dashboard. The landing FAQ already tells users
  "reviewed within 48h, credentials sent by email" — match that promise.
- **Phase 3 (open):** turn on self-serve signup by pointing the landing CTA
  at the app's own create-account gate (one-line change — ask Claude).

---

## Hardening backlog (post-launch, in rough priority order)

1. **Team rooms**: invite links in the app are stubbed
   (`TODO: migrate warrooms to Supabase Realtime`) — needs `warrooms` +
   `warroom_members` tables with membership RLS and Realtime sync.
2. **Vendor React locally**: the landing pages load React from unpkg.com at
   runtime; serving those two files from this repo removes a third-party
   point of failure.
3. **AXIS metering**: per-user quotas in Postgres (current limiter is
   per-IP, per warm instance — good enough for a small beta only).
4. **Google Drive backup** (app Settings): needs the OAuth consent screen
   published, or replace it with Supabase Storage snapshots.
5. **Email notifications**: a Supabase webhook/cron that emails you when a
   new `beta_requests` row lands, so approvals stay inside 48h.
6. **Error monitoring** (Sentry) + scheduled Supabase backups.

## Phase: paid launch (later)

Plan gates in the app are UI-only. Stripe Checkout + webhook →
`profiles.plan` column → entitlement checks in RLS and `/api/axis` quotas.
