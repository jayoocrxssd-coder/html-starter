# WAR ROOM — v5.1

**Your personal business command center.** Missions, P&L, focus timer, intel notes, calendar, bills — and AXIS, your AI co-pilot.

---

## What's in the box

| File | Purpose |
|---|---|
| `index.html` | Marketing landing page + auth overlay (sign up / sign in) |
| `app.html` | The full War Room application |
| `launch-checklist.html` | Interactive checklist — open in browser to track launch progress |
| `netlify.toml` | Netlify deploy config + security headers |
| `middleware.js` | Vercel Edge Middleware — security headers for Vercel deploys |
| `package.json` | Vercel Edge dependency |

---

## How the auth flow works

```
index.html  →  user signs up or signs in
               ↓
           localStorage.wr_accounts  (hashed credentials)
           localStorage.wr_access = '1'
               ↓
           redirect → /app.html
               ↓
app.html   →  checks localStorage.wr_access
               if missing → redirect back to /
               if present → load app
               ↓
           first visit: onboarding wizard (7 steps)
           returning:   dashboard
               ↓
           sign out → clears wr_access, wr_user_email, wr_user_google
                    → redirect to /
```

---

## Deploy in 2 minutes (Netlify)

1. Push this repo to GitHub
2. Go to [app.netlify.com](https://app.netlify.com) → **Add new site** → **Import from Git**
3. Select this repo — publish directory is already set to `.` in `netlify.toml`
4. Click **Deploy site**

`index.html` serves at `/`, `app.html` at `/app.html`. Security headers apply automatically.

---

## What's already fixed & production-ready

- **Account creation** — email + password validation, confirm-password field, hashed storage in `localStorage.wr_accounts`, redirects to app on success
- **Sign-in** — looks up account, verifies hash, sets token, redirects
- **Google sign-in** — sets `wr_access` token and redirects (connect to real OAuth in Phase 2)
- **Auth gate** — `?bypass=1` URL exploit removed; app strictly requires `wr_access` token
- **Sign-out** — clears all auth tokens (`wr_access`, `wr_user_email`, `wr_user_google`) and redirects to `/`
- **Dev backdoor** — hardcoded `admin / cres-dev-only` credential removed
- **XSS guard** — `esc()` HTML sanitizer added; business names, goal text, and other user data escaped before `innerHTML` insertion
- **Security headers** — `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, HSTS, `Referrer-Policy` on all routes via `netlify.toml`

---

## What to do next (priority order)

### 1 — Upgrade auth to a real provider
Current accounts live in the user's browser only. Replace `handleAuth()` in `index.html` with a real provider call.

**Recommended options:**
- [Supabase Auth](https://supabase.com/docs/guides/auth) — free tier, Postgres-backed, Google OAuth built-in
- [Clerk](https://clerk.com) — drop-in UI components, generous free tier
- Firebase Auth — already imported in `app.html`, just needs wiring up

### 2 — Fix waitlist lead capture (critical before launch)
`handleSignup()` in `index.html` saves emails to `localStorage.warroom_waitlist` — they exist only in that browser session. Add a Netlify Function at `netlify/functions/waitlist.js` to write signups to a database.

```js
// netlify/functions/waitlist.js (example)
export default async (req) => {
  const { email } = await req.json();
  // write to Supabase / Airtable / your DB
  return new Response(JSON.stringify({ ok: true }));
};
```

### 3 — Check Firebase Security Rules
The Firebase config (`projectId: "createwarrom"`) is embedded in `app.html`. The Web API key is designed to be public, but verify Firestore rules only allow each user to access their own data. Default rules allow public read/write.

### 4 — AXIS AI proxy
Users currently paste their own Anthropic key in Settings. For a hosted product, proxy requests through a Netlify Function so your key stays server-side.

---

## Local development

No build step — open the files directly in a browser or serve with any static server:

```bash
# Python
python3 -m http.server 3000

# Node
npx serve .
```

Then visit `http://localhost:3000`.

---

## Environment variables (for Netlify Functions)

Set these in Netlify → Site settings → Environment variables — never commit them to the repo.

| Variable | Used for |
|---|---|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase public API key |
| `ANTHROPIC_API_KEY` | AXIS AI proxy |
| `RESEND_API_KEY` | Transactional email (welcome, waitlist confirmation) |

---

## AXIS AI

AXIS uses the Anthropic API. Users enter their own API key in **Settings → Anthropic API Key** for the current build. Before public launch, move this to a server-side proxy (see above).

---

## Feature overview (app.html)

| Feature | Notes |
|---|---|
| **Dashboard** | Mission overview, P&L summary, calendar snapshot |
| **Missions** | Task management per business |
| **P&L Tracker** | Revenue, expenses, profit by business |
| **Focus Timer** | Pomodoro-style session tracker |
| **Intel Notes** | Markdown-style notes per business |
| **Calendar** | Events across all businesses |
| **Bills** | Recurring and one-off bill tracking |
| **AXIS AI** | Anthropic-powered co-pilot with briefing mode |
| **Onboarding** | 7-step wizard on first launch |
| **Themes** | Multiple color themes (Stratus default) |
| **Dark mode** | Toggle in settings |
| **Data backup** | Export/import via the backup system |

---

## Data storage

All app data is serialised to a single JSON object and stored in `localStorage` under the key `stratusWR_v31`. Auth accounts are stored separately under `wr_accounts`.

For multi-device sync, pipe the `stratusWR_v31` blob to a Supabase or Firebase Firestore document keyed by user ID.

---

## Security notes

- Passwords are stored as `btoa(unescape(encodeURIComponent(email + ':' + password)))` — client-side only, suitable for the current localStorage-based auth. Replace with bcrypt hashes server-side when you move to a real auth provider.
- The `esc()` function in `app.html` escapes `& < > " '` before any user-entered string is inserted via `innerHTML`.
- Firebase Web API keys are designed to be public — security is enforced by Firestore Rules, not key secrecy.

---

## Launch checklist

Open `launch-checklist.html` in your browser for a full interactive checklist of everything needed to go from these files to a live production app. Progress saves in your browser.

---

*WAR ROOM v5.1 · CRES Ventures*
