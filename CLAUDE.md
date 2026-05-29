# CLAUDE.md

Guidance for working in this repository.

## What this is

**WAR ROOM** — a personal business command center. It is a single-page app
shipped as one large self-contained HTML file with inline CSS and JavaScript.
There is no build step, no framework, and no bundler. Deployment is via Vercel
(static hosting + Edge Middleware for security headers).

## Files

| File | Purpose |
|---|---|
| `app.html` | The full WAR ROOM application (~13.8k lines, everything inline) |
| `index.html` | Marketing landing page (includes a live AXIS demo chat) |
| `stratus_mobile (2) (1).html` | Legacy iOS-style mobile prototype — separate, older color system, not wired to the main app |
| `middleware.js` | Vercel Edge Middleware setting security headers (CSP-adjacent, X-Frame-Options, HSTS, etc.) |
| `package.json` | Only dependency is `@vercel/edge` for the middleware |
| `README.md` | Vercel starter boilerplate (largely unmodified) |

## Editing model

- All app logic lives inline in `app.html`. Edit it directly — there is no
  source-to-build pipeline.
- The file is large; locate code with `grep -n` before reading, and edit with
  targeted string replacements rather than rewriting blocks.
- After making changes, the working copy is also commonly re-packaged into a
  deploy zip alongside `index.html`, the mobile prototype, and
  `warroom_build_notes.md` when delivering to the user.

## Architecture (app.html)

### State

- A single global object `S` holds all app data. Its shape is defined by
  `DEFAULT` (~line 3753): `businesses`, `tasks`, `entries`, `notes`, `goals`,
  `goalLog`, `recent`, `wins`, `streams`, `alarms`, `sessions`, `events`,
  `bills`, `employees`, `clients`, `backups`, `monthlyBudgets`, `whiteboards`,
  `profile`, plus flags (`dark`, `onboarded`, `nextId`, `xp`, `achievements`).
- `load()` reads `S` from `localStorage` key `warRoomWR_v31`. A one-time
  migration shim copies legacy `stratusWR_v31` → `warRoomWR_v31` on first run.
- `save()` (debounced) / `saveImmediate()` persist `S` to localStorage and
  trigger cloud sync.
- `nextId` is a monotonic id counter; `recalculateNextId()` repairs it on load.

### Pages

Pages are `<div id="page-*">` sections toggled by `showPage(name)`:
`dashboard`, `axis`, `strategy` (Mission Board), `tracker` (P&L), `goals`,
`calendar`, `timer`, `intel`, `bills`, `invoices`, `bizprofile`, `profile`,
`update`. Each page has a render function (e.g. `renderAxisPage()`,
`renderTracker()`, `renderKanban()`).

### Cloud sync (Firebase)

- Firebase is **optional background sync** — the app works fully offline on
  localStorage alone. Firebase loads non-blocking after `bootApp()`.
- `bootApp()` boots the app from local data immediately.
- `loadFromCloud()` fetches the user's doc and **fully overwrites `S`** with the
  cloud copy merged over `DEFAULT`.
- `syncFromCloud(user)` runs on auth state change. It has branches for:
  cloud-authoritative (existing onboarded account), local-authoritative (stale
  cloud), no-cloud-doc (push local up), and fresh-onboarding.
- **Gotcha:** because `loadFromCloud()` replaces `S` wholesale, anything derived
  from `S` (theme, AI name, rendered panels) must be re-applied *after* it runs.
  See the theming section below.

### Theming

- Theme = CSS custom properties on `document.documentElement` (the `:root`/html
  element). `applyTheme()` reads `S.dark` and `S.profile.theme` and sets every
  `--*` variable via `root.style.setProperty`.
- Dark mode also toggles a `.dark` class on **both** `#app` and `document.body`.
- `THEMES` JS object holds per-theme light/dark palettes. The default key is
  `stratus` (user-visible name "Sand"). Light = warm cream `#f4f4f2`,
  dark = true obsidian `#000000`.
- **Critical pattern:** any path that replaces `S` (cloud load, onboarding
  finish, `load()`) must call `applyTheme()` and re-sync the `.dark` class on
  both elements afterward, or the UI keeps the previous/default theme. Use
  `classList.toggle('dark', !!S.dark)` (not a one-way `add`) so the class is
  cleared when dark is off.

### AXIS (AI assistant)

- AXIS is the in-app AI chat (Anthropic API, called directly from the browser
  with `anthropic-dangerous-direct-browser-access`). Configured in
  Profile → AI Settings.
- **API key is session-only.** It is held in the module-scoped `_axisSessionKey`
  variable via `getApiKey()` and is **never** written to `S` or localStorage.
  The key input is cleared after saving; the user re-enters it each session.
- `axisCheckReachability()` does a HEAD preflight to `api.anthropic.com` (5s
  timeout) and drives `setAxisDotState('online'|'connecting'|'offline')`, which
  updates the status dots (`#aiDot`, `#aiDotAxis`) and the `#axisStatusLabel`.
  Called on boot (if a key exists), after saving a key, and on AXIS page render.
- **All AI/external HTML is sanitized** with `sanitizeHTML()` (strips
  `<script>`, `on*` handlers, `javascript:`) before any `innerHTML` assignment
  in chat bubbles. Keep this wrapper on any new `innerHTML` that renders
  AI-sourced or external content.
- The AXIS page (`#page-axis`), the sidebar panel, and an expand overlay
  (`#axisOverlay`) mirror the same chat; sends are delegated through the overlay
  flow and synced across panels.

## Conventions

- Match the surrounding inline style: terse, comma-chained statements; inline
  `style="..."` attributes; `var(--token)` for all colors (never hardcode hex in
  new UI — pull from the theme variables so dark/light both work).
- IDs are camelCase; render functions are `render*`/`update*`; save handlers are
  `save*`.
- Don't rename these — they're load-bearing for stored user data or backup
  imports: localStorage key `warRoomWR_v31`, `STRATUS_MARKER`
  (`__stratus_project__`), version markers (`_warRoomVersion`), and the internal
  THEMES key `stratus`.

## Deploy / verify

- No test suite. Verify by opening `app.html` in a browser and exercising the
  changed flow (theme switch, cloud sign-in, AXIS chat).
- Security headers are enforced by `middleware.js` on Vercel, not in the HTML.

## Git

- Feature work happens on the designated branch; commit with descriptive
  messages and push with `git push -u origin <branch>`.
- Do not open a PR unless explicitly asked.
