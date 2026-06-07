# WAR ROOM — Build Notes & Launch Checklist

**Session date:** May 24, 2026  
**Branch:** `claude/zealous-mayer-n2G2k`  
**Files:** `index.html` (landing page) · `app.html` (full app) · `stratus_mobile (2) (1).html` (legacy mobile prototype)

---

## What Was Worked On This Session

### 1. Color System Redesign

The entire color system was rebuilt around two intentional neutral bases — one per mode — with distinct semantic palettes for each.

**Light mode → Stratus neutrals** (warm cream base `#f4f4f2`)

| Token | Value | Description |
|---|---|---|
| `--red` | `#c53020` | Warm vermillion |
| `--green` | `#1a7048` | Forest emerald |
| `--amber` | `#c07c00` | Golden amber |
| `--blue` | `#1e4890` | Deep navy |
| `--violet` | `#5825b8` | Amethyst |
| `--pink` | `#c02e7a` | Deep rose |

**Dark mode → Obsidian neutrals** (pure black base `#000000`)

| Token | Value | Description |
|---|---|---|
| `--red` | `#f06860` | Coral ember |
| `--green` | `#3de090` | Electric mint |
| `--amber` | `#f0b030` | Warm gold |
| `--blue` | `#5ab0f8` | Cornflower |
| `--violet` | `#9c6ee8` | Electric amethyst |
| `--pink` | `#f068a8` | Hot rose |

- Dark mode upgraded from near-black (`#0f0f0e`) to true obsidian black (`#000000`)
- Semantic colors added to `THEMES.stratus` and `THEMES.obsidian` JS objects so `applyTheme()` fully applies them per mode
- `violet` and `pink` were missing from dark mode — both added
- Landing page (`index.html`) now has full dark mode via `@media (prefers-color-scheme: dark)`

---

### 2. Branding Cleanup — "Stratus" → "WAR ROOM"

The app was previously named Stratus. All user-facing and storage references have been updated:

| What changed | Old | New |
|---|---|---|
| localStorage key | `stratusWR_v31` | `warRoomWR_v31` |
| Update merge flag | `stratusUpdateMerge` | `warRoomUpdateMerge` |
| Session flags | `stratusDebriefDone` etc. | `warRoomDebriefDone` etc. |
| P&L export filename | `stratus-pl-export.csv` | `warroom-pl-export.csv` |
| Theme display name | `Stratus` | `Sand` |

**Data migration shim** added to `load()` — on first run after update, it reads the old `stratusWR_v31` key, copies it to `warRoomWR_v31`, then removes the old key. Existing user data is fully preserved. Users with exported JSON backups are unaffected (import reads content, not key names).

**Left intentionally unchanged** (renaming would break data or imports):
- `STRATUS_MARKER = '__stratus_project__'` — internal pinned-business identifier stored in user data
- `_stratusVersion` / `_warRoomVersion` — version markers in exported JSON, changing would break import of old backups
- THEMES JS key `stratus` — internal code identifier, not user-visible

---

### 3. Files Added / Changed

| File | Status | Notes |
|---|---|---|
| `index.html` | Replaced | Vercel starter → WAR ROOM landing page with updated color system + dark mode |
| `app.html` | Added | Full WAR ROOM app with updated colors and branding |
| `stratus_mobile (2) (1).html` | Unchanged | Legacy iOS-style prototype, separate color system |

---

## Potential Improvements

### High Priority (before launch)

- [ ] **Rename `stratus_mobile` file** — rename to `warroom_mobile.html` and update its hardcoded `#000` / `#22c55e` color system to match the new obsidian dark palette
- [ ] **`meta name="theme-color"`** on `index.html` is hardcoded `#0e0e0d` — won't adapt to light mode; set it dynamically or add both light and dark `<meta>` tags
- [ ] **Supabase credentials** — the app references cloud sync but needs real Supabase keys wired in via env vars or a config block before launch
- [ ] **Domain** — `index.html` has hardcoded `https://warroom.app/` in canonical URL and OG tags; confirm/update if domain differs
- [ ] **OG image** — `og-image.png` is referenced but not in the repo; create and add before launch
- [ ] **AXIS API key** — the live AXIS chat in `index.html` needs an API key; currently it may be using a placeholder or demo mode

### Medium Priority

- [ ] **Onboarding "Sand" theme swatch preview** — the onboarding chip for "Sand" theme shows a dark swatch (`#0e0e0d`) as the preview color. Consider updating `preview[0]` to use the light-mode ink `#f4f4f2` background as the swatch background so it looks like cream in the picker
- [ ] **`stratus_mobile` dark colors** — that file uses `#22c55e` (Tailwind green) as its accent; align with `#3de090` obsidian dark green for consistency
- [ ] **`jarvis-stage` gradient tints** in `index.html` use hardcoded `rgba(216,58,38,...)` (old red) — update to `rgba(197,48,32,...)` to match `--red: #c53020`
- [ ] **Pricing section `--green` reference** in `index.html` — `pricing-annual` uses `color: var(--green)` which is now `#1a7048`; verify it reads well at small font size on cream
- [ ] **Error boundary / fallback** — if AXIS API fails, the landing page chat should gracefully fall back to a static response rather than showing a broken state
- [ ] **Font loading fallback** — Syne + DM Mono are loaded from Google Fonts; add a local system-font fallback stack in case the CDN is slow

### Lower Priority / Post-Launch

- [ ] **PWA manifest** — add a `manifest.json` so `app.html` installs cleanly as a home screen app (icon, `start_url`, `display: standalone`, `theme_color`)
- [ ] **Service worker** — offline support; the app stores data in localStorage already, a SW would let it work fully offline
- [ ] **THEMES for other themes** — `midnight`, `forest`, `ember`, `aurora`, `slate`, `rose` don't have semantic color overrides; switching to them leaves the new `--violet` / `--pink` values at CSS defaults rather than theme-tuned values
- [ ] **Keyboard shortcut sheet** — `⌘K` quick command is referenced in the demo but a visible shortcut guide would improve power-user onboarding
- [ ] **Analytics** — `index.html` has `/_vercel/insights/script.js` wired in; ensure it's enabled in the Vercel project dashboard
- [ ] **Remove Vercel-specific insight script** from `index.html` if not deploying to Vercel

---

## Launch Checklist

```
[ ] Supabase project created, keys inserted into app.html
[ ] Domain DNS pointed to Vercel / host
[ ] OG image (1200×630) created and deployed
[ ] meta theme-color updated for light/dark
[ ] AXIS API key live (or demo mode locked down)
[ ] Stripe / payment flow wired if selling access
[ ] Privacy policy and ToS pages linked in footer
[ ] Beta waitlist / email capture tested end-to-end
[ ] Mobile tested on iOS Safari and Android Chrome
[ ] Lighthouse audit run (target: Performance ≥90, Accessibility ≥90)
[ ] stratus_mobile.html aligned to WAR ROOM branding if shipping it
```
