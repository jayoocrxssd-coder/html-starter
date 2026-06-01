# War Room Mobile — Integration Plan & Session Notes

## What Was Done

### Phase 1a — File Extraction & Audit
- Unzipped `WF_Warroom_Mobile_Layot.zip` from upload
- Identified the primary layout file: `warroom_mobile_upload/mobile/app.html`
- Audited all hardcoded content across 2,540 lines
- Reviewed existing app: `stratus_mobile (2) (1).html`

### Phase 1b — Data Layer Refactor
- Created `warroom-mobile-app.html` as the clean integration-ready output
- Added `const APP_DATA = { ... }` config block (~150 lines) at the top of the script section
- Extracted all hardcoded content into structured objects:
  - `user` — initials, name, email, role, founded date
  - `session` — label and date string
  - `businesses` — array with name, color, active state
  - `kpis` — KPI cards (revenue, expenses, net profit, missions, hours)
  - `dashMini` — compact dashboard strip values
  - `schedule` — daily schedule pills
  - `axisBriefing` — AXIS AI daily briefing text
  - `goals` — progress bar goals with percentages
  - `chartData` — bar chart data arrays for dashboard and tracker
  - `dashMissions` — dashboard mission rows
  - `transactions` — transaction list with type, name, amount
  - `calendar` — month config, event dots, today marker
  - `calendarDayEvents` — individual day event cards
  - `missionData` — planned / progress / done task arrays
  - `intel` — intel note cards with tags and content
  - `bills` — bills due list with status and amounts
  - `invoices` — invoice list with client, number, sent/due dates
  - `goalsPage` — goals page cards with progress and time left
  - `payroll` — total, breakdown by business, people list, open role
  - `changelog` — version history entries
  - `backups` — backup timestamps and sizes
  - `axisResponses` — AXIS contextual response scripts
  - `appVersion` — current version string
- Replaced ~40 static HTML blocks with empty containers and render functions
- All navigation, tab switching, sheet animations, session timer, and AXIS chat kept intact

### Phase 1c — Data Reset (Layout Shell)
- Cleared all values from `APP_DATA` (arrays `[]`, strings `''`, numbers `0`)
- Stripped remaining static HTML content: avatar initials, biz chips, greeting text, version strings, dates, amounts, task cards, call logs, whiteboard notes, billing history, intel counts, badge counts
- File reduced from 2,748 → 2,372 lines
- Result: a clean layout shell with zero hardcoded data, ready for real data binding

**Output file:** `warroom-mobile-app.html`
**Branch:** `claude/focused-heisenberg-MehRz`

---

## Remaining Integration Phases

---

### Phase 2 — File Structure & Routing

**Goal:** Establish a proper project structure so the mobile app lives alongside the main warroom app without conflicts.

**Tasks:**
1. Create a `pages/` or `views/` directory — move `warroom-mobile-app.html` into it
2. Decide on routing strategy:
   - Option A: Single-page app with a JS router (hash-based `#/dashboard`, `#/missions`)
   - Option B: Separate HTML files per view, linked via `<a href>`
   - Option C: Keep single-file but add a top-level shell that loads mobile vs desktop view based on screen width
3. Ensure `index.html` acts as the entry point and routes to the correct shell
4. Set up a shared `assets/` folder for fonts, icons, and any shared images

**Files to touch:** `index.html`, `warroom-mobile-app.html`, new `pages/` directory

---

### Phase 3 — Shared CSS Variables & Design Tokens

**Goal:** Reconcile the two design systems so they don't clash when merged.

**Current conflict:**
| Token | War Room Mobile | Stratus Mobile |
|---|---|---|
| Background | `#f4f4f2` (light) | `#000000` (dark) |
| Font | Syne + DM Mono | Outfit + Bebas Neue |
| Accent | `#0e0e0d` | `#22c55e` (green) |
| Border radius | `10px` | `18px` |

**Tasks:**
1. Create a `tokens.css` file with a single source of truth for all CSS variables
2. Namespace the two systems if keeping both themes (e.g. `.theme-light`, `.theme-dark`)
3. Or: pick one design direction and migrate both files to it
4. Consolidate font imports into one `<link>` block
5. Test that neither file's styles leak into the other

**Files to touch:** new `tokens.css`, `warroom-mobile-app.html`, `stratus_mobile.html`

---

### Phase 4 — Navigation & Shell Integration

**Goal:** Merge the tab navigation systems and share the top bar / sheet components between views.

**Tasks:**
1. Extract the bottom tab bar into a reusable component or include pattern
2. Merge the top command bar (breadcrumb + business switcher + avatar) — both apps have one
3. Unify the bottom sheet / modal system — both use draggable sheets, currently duplicated
4. Ensure deep-linking works: opening the app to a specific tab (e.g. `/missions`) shows the right view
5. Handle back navigation on mobile (swipe back, browser back button)
6. Add transition animations between top-level views if not already present

**Files to touch:** `warroom-mobile-app.html`, `stratus_mobile.html`, shared `components/` if created

---

### Phase 5 — AXIS AI Integration

**Goal:** Wire the AXIS AI chat panel to real, context-aware data instead of static scripts.

**Current state:** `axisResponses` in `APP_DATA` holds five pre-written response strings (`briefing`, `margin`, `focus`, `bills`, `intel`). The AXIS input and chat panel are fully rendered but not connected to any real intelligence.

**Tasks:**
1. Connect AXIS input to a real API endpoint (Claude API recommended — model: `claude-sonnet-4-6`)
2. Build a context-injection function that reads current `APP_DATA` and injects it as system context before each AXIS request
3. Replace static `axisResponses` with dynamic fetch calls
4. Add streaming support so AXIS responses appear word-by-word (use Claude API streaming)
5. Add suggested prompt chips that reflect current data (e.g. "What's overdue?" only shows if there are overdue invoices)
6. Add a conversation history array so AXIS remembers context within a session

**API setup:**
```js
// Example AXIS API call with context injection
async function askAxis(userMessage) {
  const context = buildContext(APP_DATA); // serialize current state
  const response = await fetch('/api/axis', {
    method: 'POST',
    body: JSON.stringify({ message: userMessage, context }),
  });
  // stream response into chat panel
}
```

**Files to touch:** `warroom-mobile-app.html`, new `api/axis.js` or `middleware.js`

---

### Phase 6 — Live Data Binding

**Goal:** Replace the static `APP_DATA` object with real data fetched from a backend or stored in the browser.

**Tasks:**
1. Choose a data source:
   - **Supabase** (already referenced in changelog) — recommended for real-time sync
   - **localStorage** — for offline-first / single-user
   - **REST API** — if a backend already exists
2. Write a `loadData()` async function that fetches and populates `APP_DATA` on startup
3. Add loading states to each rendered section (skeleton loaders or spinners)
4. Add empty states for each section when data is genuinely empty (e.g. "No missions yet — add one")
5. Add error states for failed fetches
6. Wire the session timer to actually track and persist session duration
7. Make the mission board interactive — add, complete, and reorder tasks with changes saved back to the data source

**Example structure:**
```js
async function loadData() {
  const [kpis, missions, invoices] = await Promise.all([
    fetch('/api/kpis').then(r => r.json()),
    fetch('/api/missions').then(r => r.json()),
    fetch('/api/invoices').then(r => r.json()),
  ]);
  APP_DATA.kpis = kpis;
  APP_DATA.missionData = missions;
  APP_DATA.invoices = invoices;
  renderAll();
}
```

**Files to touch:** `warroom-mobile-app.html`, new `api/` directory, Supabase config

---

### Phase 7 — Business Context Switcher

**Goal:** Build a proper multi-business selector that filters all views by the active business.

**Current state:** The business switcher chip in the top bar opens a sheet listing businesses, but selecting one does not filter any data.

**Tasks:**
1. Add an `activeBusiness` field to `APP_DATA` (or `null` for "All")
2. Wire the business sheet selection to update `activeBusiness` and re-render all views
3. Filter each render function by `activeBusiness`:
   - Missions: show only tasks for active business
   - Transactions: filter by business tag
   - Invoices / Bills: filter by business
   - Payroll: filter by business
   - Goals: filter by business
4. Show an "All businesses" aggregate view when no filter is active
5. Persist the active business selection in `localStorage` across sessions
6. Add per-business color theming (the pip colors are already defined in `businesses` array)

**Files to touch:** `warroom-mobile-app.html`

---

### Phase 8 — PWA / Mobile Hardening

**Goal:** Make the app installable and functional on real iOS and Android devices.

**Tasks:**
1. Create a `manifest.json` with app name, icons, theme color, display mode (`standalone`)
2. Write a `service-worker.js` that caches the app shell for offline use
3. Register the service worker in the main HTML
4. Consolidate the duplicate PWA meta tags between the two HTML files into one shared block
5. Test on real devices:
   - iOS Safari: check safe area insets, status bar, bottom nav overlap
   - Android Chrome: check install prompt, splash screen, back gesture
6. Add haptic feedback on key interactions (missions complete, sheet open) using the Vibration API
7. Audit touch targets — all interactive elements should be minimum 44×44px
8. Test landscape orientation (currently likely broken — add a rotation lock or landscape layout)

**Files to touch:** new `manifest.json`, new `service-worker.js`, `warroom-mobile-app.html`, `index.html`

---

## File Reference

| File | Description |
|---|---|
| `warroom-mobile-app.html` | Clean mobile layout shell — primary working file |
| `warroom_mobile_upload/mobile/app.html` | Mirror copy from original upload |
| `stratus_mobile (2) (1).html` | Existing dark-theme warroom app |
| `index.html` | Current entry point |
| `middleware.js` | Existing middleware — extend for AXIS API |

## Branch
All work is on: `claude/focused-heisenberg-MehRz`
