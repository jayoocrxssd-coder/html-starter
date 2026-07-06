# War Room — Beta Launch Backend Checklist

The app ships at `/app/` and the landing page at `/`. The frontend is fully
static; everything below is the wiring it expects to exist before real users
touch it. Ordered by launch phase.

---

## Phase 1 — Private beta (invite-only, free)

### 1. Firebase (auth + cloud sync) — project `createwarrom`
The app already embeds the Firebase config (`projectId: createwarrom`) and
uses Auth + Firestore for accounts, team rooms and cloud sync.

- [ ] **Authorized domains**: add the production domain (and the Vercel
      `*.vercel.app` preview domain) under Firebase Console → Authentication →
      Settings → Authorized domains. Google sign-in fails without this.
- [ ] **Sign-in providers**: enable **Google** and **Email/Password** in
      Firebase Auth (the in-app gate has both tabs).
- [ ] **Firestore security rules** — critical, do this before sharing any
      link. The app reads/writes these collections:
      `users`, `warrooms`, `warrooms/{id}/members`, `war_room_data`.
      Rules must enforce: users can only read/write their own `users` doc and
      `war_room_data` doc; room reads/writes require membership; invite-join
      (`?join=<roomId>`) needs a narrowly-scoped create on `members`.
- [ ] **Email templates**: configure password-reset / verification email
      sender + templates in Firebase Auth.
- [ ] **Quotas/billing**: confirm the Firebase plan (Spark vs Blaze) covers
      expected beta traffic.

### 2. Google OAuth + Drive backup
The app uses Google Identity Services + the Drive API (`drive.file` scope)
with OAuth client `190616282170-hkcq...apps.googleusercontent.com`.

- [ ] **Authorized JavaScript origins**: add the production domain to that
      OAuth client in Google Cloud Console → Credentials.
- [ ] **OAuth consent screen**: move from "Testing" to "In production"
      (testing mode caps you at 100 test users and shows the unverified-app
      warning). Scopes used: `drive.file`, `userinfo.email`,
      `userinfo.profile`.
- [ ] **Enable the Drive API** on the same GCP project.

### 3. AXIS AI proxy (Anthropic) — biggest item
Right now the app calls `api.anthropic.com/v1/messages` **directly from the
browser** with a user-pasted `sk-ant` key (held in session memory only).
Fine for you; not viable for beta users.

- [ ] Build a serverless proxy (Vercel function, e.g. `api/axis.js`) that:
      - holds **your** Anthropic API key in a Vercel env var,
      - verifies the caller's Firebase ID token,
      - enforces per-user rate limits / daily token quotas,
      - forwards `{model, system, messages, max_tokens}` to Anthropic and
        streams the response back.
- [ ] Point the app's AI fetch at `/api/axis` instead of
      `api.anthropic.com` (single constant + `getAIFetchHeaders()` change),
      keeping the paste-your-own-key path as a fallback.
- [ ] Model is pinned to `claude-sonnet-4-20250514` — works, but decide the
      beta model + `max_tokens` budget deliberately (cost control).

### 4. Phased access gating
Invite links (`?join=<roomId>`) already work client-side, but nothing limits
who can sign up.

- [ ] Beta allowlist: a Firestore collection (e.g. `beta_invites`) of invite
      codes/emails, checked in security rules or a small signup Cloud
      Function, so you control each phase's cohort.
- [ ] Waitlist capture on the landing page (form → Firestore or a simple
      Vercel function + email service) for people outside the current phase.

### 5. Hosting
- [ ] Vercel project connected to this repo; custom domain on `/`.
- [ ] Landing page is live at `/`, app at `/app/` (already wired).
- [ ] Vercel Analytics is already included on the landing page.

---

## Phase 2 — Open beta

- [ ] **Error monitoring**: Sentry (or similar) snippet in the app.
- [ ] **Backups/export**: Drive backup exists per-user; add scheduled
      Firestore backups (GCP export) for your side.
- [ ] **Legal**: Privacy Policy + Terms pages (`/privacy`, `/terms`) — the
      app collects auth data, business data and proxies AI content; you need
      these before opening signups.
- [ ] **Abuse controls** on the AXIS proxy: per-IP throttle, prompt-size cap.

## Phase 3 — Paid launch

The in-app plan gate (Personal / Small Business / Enterprise, founder
pricing) is **UI only** — no payment rails exist.

- [ ] **Stripe**: Products/Prices for the three tiers (+ annual), Checkout
      session endpoint, Customer Portal, and a webhook that writes the plan
      to the user's Firestore doc.
- [ ] **Entitlement enforcement**: security rules / proxy quotas keyed off
      the plan field (room member limits, AXIS usage, invoice caps).
- [ ] **Dunning + receipts** via Stripe emails.

---

## Quick reference — external services the frontend already talks to

| Service | Used for | Status |
|---|---|---|
| Firebase Auth (`createwarrom`) | Sign-in (Google + email) | Config embedded; needs domains, providers, rules |
| Firestore | Cloud sync, team rooms, invites | Needs security rules before beta |
| Google Drive API | Per-user backup | Needs OAuth origins + consent screen |
| Anthropic API | AXIS assistant | Needs `/api/axis` proxy + server-side key |
| Stripe | Billing (Phase 3) | Not wired at all |
| Vercel | Hosting + analytics | Repo-ready |
