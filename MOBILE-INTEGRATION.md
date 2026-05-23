# WAR ROOM — Mobile Integration Debrief

**Date:** 2026-05-23  
**Branch:** `claude/fervent-thompson-8hp3X`  
**Repo:** `jayoocrxssd-coder/html-starter`

---

## What Was Built

Two HTML files — `index.html` (the landing page) and `app.html` (the full dashboard) — were taken from the WAR ROOM desktop build and had a complete mobile-first experience integrated directly into them. Users on phones automatically see the mobile UI; desktop users see the unchanged desktop UI. No server, no build tools, no dependencies — pure static HTML/CSS/JS.

---

## Files Delivered

| File | Lines | Notes |
|---|---|---|
| `index.html` | 3,032 | Landing page with mobile hamburger/drawer/sticky CTA |
| `app.html` | 14,360 | Full app with mobile shell (8 pages, AXIS, sheets, bottom tabs) |
| `warroom-mobile-build.zip` | 211 KB | Both files zipped for download |

---

## How Mobile Routing Works

### Device Detection (runs before first paint)
```html
<script>
(function(){
  var mob = window.innerWidth <= 768 || /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
  if(mob) document.documentElement.setAttribute('data-mob','1');
})()
</script>
```
This inline script in `<head>` sets `data-mob="1"` on `<html>` before the browser paints anything. No flicker.

### CSS Routing (two shells, one visible)
```css
html[data-mob] #d-shell { display: none !important }       /* hide desktop on mobile */
html:not([data-mob]) #m-shell { display: none !important } /* hide mobile on desktop */
html[data-mob], html[data-mob] body { height: 100%; overflow: hidden; }
```

### DOM Structure
```
<body>
  <div id="d-shell">  ← Full 13k-line desktop app (hidden on mobile)
    ...
  </div>

  <div id="m-shell">  ← Full mobile app (hidden on desktop)
    <div class="shell">
      <div class="topbar">...</div>
      <div class="content">...</div>
      <div class="tabbar">...</div>
      <div class="fab">...</div>
      <!-- sheets, drawer, overlays -->
    </div>
  </div>

  <script>
    if(document.documentElement.getAttribute('data-mob')) {
      // All mobile JS — only runs on mobile
    }
  </script>
</body>
```

---

## index.html — What Was Added

### Mobile Components
- **Hamburger button** — hidden on desktop, shown at ≤760px, opens the slide-out drawer
- **Slide-out drawer** (`#mobDrawer`) — right-side, 290px wide, contains nav links + Sign In / Reserve Access buttons
- **Sticky bottom CTA** (`#mobStickyCta`) — fixed bottom bar with live joiner count + "Get Access →" button
- **Swipe-to-close** — touch gesture on the drawer (swipe right > 60px closes it)
- **Joiner count sync** — MutationObserver watches the desktop counter and mirrors it in the sticky CTA

### CSS Classes Added
`.mob-hamburger`, `.mob-drawer-back`, `.mob-drawer`, `.mob-drawer-hd`, `.mob-drawer-close`, `.mob-drawer-nav`, `.mob-drawer-btns`, `.mob-sticky-cta`, `.mob-sticky-cta-text`, `.mob-sticky-cta-btn`

---

## app.html — What Was Added

### Mobile Shell Pages (8 total)
| Page ID | Tab | Description |
|---|---|---|
| `m-page-dashboard` | Home | Greeting card, KPI strip, AXIS briefing, goals, P&L chart, mini timer, active missions |
| `m-page-missions` | Missions | Kanban tabs (Planned/In Progress/Done), task cards with priority/biz/due date |
| `m-page-tracker` | P&L | Period selector, 4 KPI cards, 7-day bar chart, transaction list |
| `m-page-calendar` | Calendar | Month grid with event dots, day detail with event cards |
| `m-page-more` | More | Profile header, module list, workspace settings, account settings |
| `m-page-timer` | (More→) | Large focus timer, session form, EST alarm clock, session log |
| `m-page-intel` | (More→) | Note search, filter tabs, note cards with tags |
| `m-page-bills` | (More→) | Bills summary, 4 KPI cards, upcoming/overdue/paid bill cards |

### Mobile UI Components
- **Dual-row topbar** — Row 1: hamburger + AXIS search + avatar. Row 2: breadcrumb + business switcher chip
- **Bottom tab bar** — 5 tabs with SVG icons: Home, Missions, P&L, Calendar, More
- **AXIS FAB** — Fixed bottom-right button above tab bar with green online dot indicator
- **AXIS sheet** — 88vh dark slide-up panel (`#161615`) with suggestion chips + chat UI
- **Business switcher sheet** — Bottom sheet with list of businesses to switch between
- **Left slide-out drawer** — Full nav with section headers, all pages linked, sync + export buttons

### CSS Architecture
All mobile CSS (~300 rules) is scoped under `#m-shell` to prevent conflicts with the desktop's CSS:
```css
#m-shell .topbar { ... }
#m-shell .content { ... }
#m-shell .tabbar { ... }
/* etc. */
```
Custom properties (CSS vars) are declared on `#m-shell` itself:
```css
#m-shell {
  --bg: #f4f4f2;
  --accent: #0e0e0d;
  --tab-h: 64px;
  --top-h: 96px;
  /* etc. */
}
```

### JS Architecture
All mobile functions are prefixed with `m` and all element IDs are prefixed with `m-`:

| Mobile JS | Does | Element ID |
|---|---|---|
| `mGoPage(name)` | Navigate between pages | `m-page-{name}` |
| `mOpenSheet(id)` | Slide up a bottom sheet | `m-{id}`, `m-{id}Back` |
| `mCloseSheet(id)` | Dismiss a bottom sheet | same |
| `mOpenDrawer()` | Open left nav drawer | `m-drawer`, `m-drawerBack` |
| `mCloseDrawer()` | Close left nav drawer | same |
| `mSetMissionTab(k,el)` | Switch kanban tab | `m-missionList` |
| `mMakeChart(elId,data)` | Build bar charts | `m-dashChart`, `m-trkChart` |
| `mToggleTimer()` | Start/pause focus timer | `m-bigTimer`, `m-bigBtn` |
| `mResetTimer()` | Reset focus timer | same |
| `mAskAxis(k)` | Trigger AXIS suggestion | `m-axisMsgs` |
| `mSendAxis(e)` | Submit AXIS message | `m-axisInput`, `m-axisMsgs` |
| `mTickClocks()` | Update EST clock (1s interval) | `m-alarmEst` |
| `mSetCrumb(name)` | Update breadcrumb topbar | `m-topCrumb`, `m-crumbNow` |

---

## Mobile UX Details

### Safe Area Support (iPhone notch/home indicator)
```css
.tabbar { padding-bottom: env(safe-area-inset-bottom); }
.axis-sheet-input { padding-bottom: max(11px, env(safe-area-inset-bottom)); }
```

### iOS Scroll Performance
```css
.content { -webkit-overflow-scrolling: touch; }
.axis-msgs { -webkit-overflow-scrolling: touch; }
```

### Prevent iOS Input Auto-Zoom
```css
#m-shell input, #m-shell select, #m-shell textarea { font-size: 16px; }
```
iOS zooms in when `font-size < 16px` on inputs. Fixed.

### Touch Targets (min 44×44px)
All interactive elements (tabs, buttons, drawer items, CTA buttons) meet Apple's 44px minimum touch target recommendation.

### Viewport
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
```
The mobile design files originally shipped with `width=390` — fixed to `width=device-width` so it works on all devices.

---

## What Was NOT Changed

- The entire desktop app JS (10,000+ lines across multiple `<script>` blocks) was left completely untouched
- Firebase Auth / Firestore config untouched
- Google Drive sync config untouched
- All desktop CSS (1,800 lines) untouched
- Landing page desktop CSS and JS untouched

---

## Deployment Notes

Both files are self-contained static HTML. Drop them into any static host (Vercel, Netlify, GitHub Pages, S3) and they work immediately. No bundler, no npm, no backend required.

The build is on branch `claude/fervent-thompson-8hp3X` in the `jayoocrxssd-coder/html-starter` repo.
