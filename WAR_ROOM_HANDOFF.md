# War Room — Handoff Document

**File:** `War_Room_fixed.html`  
**Size:** ~905 KB (single self-contained HTML file)  
**Branch:** `claude/debug-and-fix-all-W6bW0`  
**Date:** 2026-05-16

---

## What War Room Is

A fully offline, self-contained business management OS delivered as a single HTML file. No server, no install, no dependencies. Open it in any modern browser and it runs. All data is persisted to `localStorage` and optionally synced to Supabase cloud.

---

## Features Built This Session

### Invoice System
- Per-business invoice tab inside each Business Profile
- Full Invoices page in the command sidebar with business filter
- Create, draft, send, and mark-paid funnel with status tracking
- Auto-numbered invoice IDs (collision-safe)
- Fields: client, email, line items, tax rate, discount, due date, notes
- 4 SVG charts: monthly revenue bar, status donut, top clients, upcoming collections
- KPI bar: total outstanding, overdue count, avg payment time, collection rate
- Grid/list view toggle, tab counts (All / Draft / Sent / Paid / Overdue)
- `showInvoicesForBiz(bizId)` — click a business anywhere to jump to its invoices

### Video Call / Meet
- Real WebRTC camera via `getUserMedia` — your live feed renders in your tile
- Real screen sharing via `getDisplayMedia`
- No fake participants — joining a room shows only you with a "Waiting for others" banner
- Room code displayed so you can share with real participants
- Mute / camera toggle / screen share controls all wired
- Meeting timer, notes field, participant sidebar
- Meeting history saved to `S.vcMeetings` and shown in lobby (last 5)
- Call end logs the session automatically

### Axis (AI Assistant)
- Renamed from Jarvis to Axis across all 69 references — UI labels, CSS classes, function names, strings
- War Room Intel Snapshot: pulls live data across financials, businesses, missions, goals, schedule, and bills into a structured prompt context

### Theme / Appearance System
- Seamless dark ↔ light mode switching
- 6 accent color swatches with live preview
- Aurora CSS late-load bug fixed — theme changes no longer reset stacking contexts

### Modal System (Critical Fix)
- Root cause: Aurora CSS applied `position:relative; z-index:1` to `.modal-overlay`, `.task-popup-overlay`, `.jarvis-overlay` (now `.axis-overlay`), trapping all popups inside a stacking context
- Fix: removed overlay selectors from that rule — all modals now render as proper centered popups
- Affects: invoice modal, task popup, Axis overlay, and every other dialog in the app

---

## Architecture

### Bundle Format
The app ships as one HTML file with the template HTML JSON-encoded inside a `<script type="__bundler/template">` tag. On load, the loader decodes it and calls `replaceWith()` to swap the document.

**Critical encoding rule:** All `/` characters must be escaped as `/` in the JSON string, otherwise the HTML parser terminates the `<script>` tag at any `</script>` inside the payload.

### Data Model
All state lives in the global `S` object, persisted to `localStorage` key `stratusWR_v31`.

| Key | Contents |
|---|---|
| `S.businesses` | Array of business profiles |
| `S.invoices` | Array of invoice objects |
| `S.tasks` | Missions / tasks |
| `S.goals` | Goals per business |
| `S.events` | Calendar events |
| `S.transactions` | Revenue & expense ledger |
| `S.bills` | Recurring bills |
| `S.vcMeetings` | Video call history logs |
| `S.theme` | `'dark'` or `'light'` |
| `S.accent` | Hex color string |

### Key Functions

| Function | Purpose |
|---|---|
| `openInvModal(id)` | Open create/edit invoice modal |
| `saveInvoice()` | Persist invoice to `S.invoices` |
| `sendInvoiceFromDetail()` | Mark invoice sent, stamp `sentAt` |
| `renderInvoices()` | Full invoices page render |
| `renderInvCharts()` | 4 SVG charts |
| `showInvoicesForBiz(bizId)` | Jump to invoices filtered by business |
| `joinVCall()` | Start/join a video call room |
| `_vcTryCamera()` | Request webcam via getUserMedia |
| `toggleScreenShare()` | getDisplayMedia screen share |
| `_vcSaveMeetingLog()` | Save call to history on end |
| `renderVCallParticipants()` | Render participant grid with live video |
| `openAxisOverlay()` | Open Axis AI panel |
| `buildAxisContext()` | Assemble live data snapshot for AI prompt |

---

## Known Limitations

- **No real WebRTC signaling** — the room code is UI-only; actual peer connections require a signaling server (e.g. WebSocket + STUN/TURN). Camera and screen share work locally.
- **No real AI backend** — Axis builds a context snapshot but requires you to wire in an API key (OpenAI, Anthropic, etc.) to get live responses.
- **localStorage only** — data stays in the browser. Supabase sync hooks exist in the codebase but require credentials to activate.
- **Single file** — all edits must be made to `War_Room_fixed.html`. The re-encoding rule above must be followed when modifying the template programmatically.

---

## Bugs Fixed This Session

| Bug | Root Cause | Fix |
|---|---|---|
| All modals rendering inline | Aurora CSS trapped overlays in a stacking context | Removed overlay selectors from `position:relative` rule |
| LOOK dropdown clipped by topbar | `overflow:hidden` + stacking context on `.topbar` | Portaled dropdown to `<body>`, fixed z-index |
| `SyntaxError: Unexpected identifier 'DM'` | `'DM Mono'` inside single-quoted JS string | Removed inner quotes from font-family value |
| `SyntaxError: Unexpected identifier 'all'` | `'all'` literal inside single-quoted JS string | Extracted `clearInvBizFilter()` no-arg helper |
| Unterminated JSON string at position 117572 | `/` not escaped as `/` in bundle | Applied `.replace('/', '\\u002F')` in encoder |
| Fake video call participants | Hardcoded Alex Rivera / Sam Chen / Jordan Lee seeded on join | Removed; only real user added on join |
| Theme not persisting across reload | `S.theme` not applied on init | Applied theme class before first render |

---

## How to Extend

**Add a new data type:**
1. Add a key to `S` with a default value (e.g. `S.contacts = []`)
2. Add the key to `DATA_KEYS` array so it's included in backup/restore
3. Build render and CRUD functions following the invoice pattern

**Add a real AI backend to Axis:**
1. Find `buildAxisContext()` — it returns the full prompt string
2. Wire a `fetch()` call to your chosen API inside `sendAxisMessage()`
3. Stream or append the response to the chat container

**Enable Supabase sync:**
1. Set `SUPABASE_URL` and `SUPABASE_ANON_KEY` constants at the top of the script
2. The sync hooks (`_syncToCloud`, `_loadFromCloud`) are already stubbed in

---

*Built with War Room — your offline business OS.*
