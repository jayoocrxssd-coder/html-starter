# Stratus — Habit Tracker & Goal Planner

A single-file mobile PWA built with vanilla HTML, CSS, and JavaScript. No build step, no dependencies, no framework — open the file in any browser and it works.

---

## What it is

Stratus is a personal productivity app styled as a native iOS-like mobile UI. It tracks daily habits, long-term goals, calendar events, and focus sessions — all persisted to `localStorage` so data survives page reloads.

---

## Features

### Onboarding (4 steps)
- **Step 1 — Name:** Live greeting reacts as you type. Headline morphs from "Your rise starts here." to "Your rise starts *now*." once a name is entered.
- **Step 2 — Focus areas:** Select from 8 categories (Fitness, Mindset, Finance, Health, Learning, Career, Social, Creative). Chips bounce on tap. Button upgrades to "Build my pack →" once at least one area is chosen.
- **Step 3 — Starter pack:** Personalised habit suggestions (3 per focus area). First habit per area is pre-selected. Tap to toggle on/off. Button shows live "Add N habits →" count.
- **Step 4 — Launch:** Confetti burst, personalised title, stat cards (focus areas · habits ready · streak). Tapping "Launch Stratus" creates all selected habits, saves everything, and re-renders the full app instantly.

### Home
- Daily habit ring (progress circle)
- Habit cards with one-tap completion, streak badges, and focus-mode entry
- Quick-add goal sheet
- Home stats (best streak, weekly completion %)
- Smart context pings (Web Notifications API)

### Calendar
- Monthly grid with event dots
- Tap a day to add/edit events (title, time, repeat, category)
- Edit existing events inline
- Month/year picker

### Routine
- Full habit list with weekly completion strips
- Add habit sheet (name, category, frequency: daily / 5x / 4x / 3x per week)
- Habit detail sheet: 30-day chart, week strip, rest-day toggle, edit & delete
- Priority recalibration — low-completion habits surface to the top

### Analytics
- Focus time stats (today · sessions · avg session)
- Weekly output bar chart (per habit, built from real `completionLog`)
- Streak leaderboard
- 7-day completion heatmap
- Goal progress summary

### Profile
- Display name (live updates everywhere — hero greeting, avatar initial)
- Productivity profile card (consistency bar, style badge, focus area chips with edit panel)
- Redo onboarding — navigates back to the full 4-step flow
- Appearance accordion: 6 accent colours, card radius slider, motion intensity (Full / Subtle / Off), light/dark mode toggle
- Notifications accordion: push, weekly digest, goal reminders, smart context pings
- Data: export JSON backup, import JSON backup, reset all data
- Membership card, support accordion, sign-out with confirm

### Focus Mode
- Full-screen timer overlay (elapsed time)
- Pause / resume / mark done
- Saves session time to analytics on completion

---

## Data model (`localStorage` key: `stratus_v1`)

```json
{
  "habits": [
    {
      "id": 1,
      "name": "Morning workout",
      "cat": "Fitness",
      "icon": "<svg path data>",
      "streak": 4,
      "weekDone": [true, false, true, true, false, false, false],
      "target": 5,
      "unit": "days/wk",
      "createdAt": 1717200000000,
      "completionLog": { "2026-05-28": true, "2026-05-30": true },
      "restLog": {}
    }
  ],
  "goals": [
    {
      "id": 1,
      "name": "Save $5000",
      "cat": "Finance",
      "target": 5000,
      "current": 1200,
      "unit": "$",
      "timeline": "6 months",
      "notes": "Emergency fund",
      "completed": false,
      "createdAt": 1717200000000
    }
  ],
  "monthlyGoals": [],
  "calEvents": {
    "2026-05-31": [
      { "title": "Team standup", "time": "09:00", "repeat": "weekdays", "cat": "Career" }
    ]
  },
  "userName": "Alex",
  "obFocuses": ["Fitness", "Mindset"],
  "accent": "#22c55e",
  "accentBg": "#22c55e1a",
  "accentText": "#4ade80",
  "cardRadius": "18px",
  "theme": "dark",
  "focusTotalSeconds": 3600,
  "focusSessionCount": 4,
  "focusBlocksEnabled": false,
  "smartPingsEnabled": false
}
```

---

## Views

| ID | Tab | Description |
|----|-----|-------------|
| `v-home` | Home | Daily overview, habit ring, habit cards |
| `v-cal` | Calendar | Monthly calendar, event management |
| `v-routine` | Routine | Full habit list, add/edit habits |
| `v-analytics` | Analytics | Focus stats, charts, leaderboards |
| `v-profile` | Profile | Settings, appearance, data management |
| `v-onboarding` | — | 4-step setup flow (not a nav tab) |

Navigation uses `sw(tab)` which swaps the `.active` class between `.view` elements and syncs the bottom nav. Swipe left/right between the 5 main tabs.

---

## Key functions

| Function | What it does |
|----------|-------------|
| `showOnboarding()` | Activates `v-onboarding`, resets step |
| `obFinish()` | Creates selected habits, saves data, re-renders app, navigates to Home |
| `renderHomeHabits()` | Re-renders habit cards on the Home tab |
| `renderRoutineHabits()` | Re-renders the full Routine habit list |
| `renderAllGoals()` | Re-renders goal cards on Home |
| `buildCalendar()` | Rebuilds the monthly calendar grid |
| `updateAnalytics()` | Rebuilds all Analytics charts |
| `updateProductivityProfile()` | Updates consistency bar, style badge, focus chips on Profile |
| `saveToStorage()` | Snapshots full app state to `localStorage` |
| `loadFromStorage()` | Restores state from `localStorage` on page load |
| `setName(v)` | Updates name everywhere (hero, profile display, avatar initial) |
| `setAccent(sw)` | Applies a new accent colour via CSS custom properties |
| `applyTheme(mode)` | Switches dark / light theme |
| `sw(tab)` | Navigates to a tab view |
| `todayKey()` | Returns zero-padded `YYYY-MM-DD` for today |
| `calKey(y,m,d)` | Returns zero-padded date key for any date |

---

## Onboarding data flow

```
Step 1  →  obName = "Alex"
Step 2  →  obFocuses = ["Fitness", "Mindset"]
Step 3  →  obSelectedHabits = ["Fitness-0", "Mindset-0", "Mindset-1"]
Step 4  →  obFinish()
              ↳ setName("Alex")          → all name displays update
              ↳ habits.push(...)         → 3 habit objects created
              ↳ saveToStorage()          → persisted to localStorage
              ↳ renderHomeHabits()       → Home tab shows new habits
              ↳ renderRoutineHabits()    → Routine tab shows new habits
              ↳ updateProductivityProfile() → focus chips populated
              ↳ updateAnalytics()        → analytics seeded
              ↳ sw(homeTab)              → lands on Home
```

---

## Starter habit catalogue

| Focus | Habits |
|-------|--------|
| Fitness | Morning workout (5x), Evening walk (5x), Daily stretching (daily) |
| Mindset | Daily meditation (daily), Journaling (5x), Gratitude log (daily) |
| Finance | Review budget (3x), Track spending (daily), No-spend check-in (5x) |
| Health | Drink 8 glasses of water (daily), Sleep by 10pm (daily), Take vitamins (daily) |
| Learning | Read 20 minutes (daily), Watch something educational (5x), Practice a skill (5x) |
| Career | Review weekly goals (5x), Network outreach (3x), Learn something new (5x) |
| Social | Check in with a friend (3x), Family time (5x), Send a kind message (3x) |
| Creative | Create something (5x), Practice my craft (5x), Explore new ideas (3x) |

---

## Theming

All colours are CSS custom properties on `.phone`:

| Variable | Default | Description |
|----------|---------|-------------|
| `--accent` | `#22c55e` | Primary action colour |
| `--accent-bg` | `#22c55e1a` | Accent tint background |
| `--accent-text` | `#4ade80` | Accent text / label colour |
| `--bg` | `#000000` | App background |
| `--card` | `#1c1c1e` | Card background |
| `--card2` | `#2c2c2e` | Secondary card / input background |
| `--card3` | `#3a3a3c` | Tertiary / border colour |
| `--white` | `#ffffff` | Primary text |
| `--muted` | `#8e8e93` | Secondary text |
| `--r` | `18px` | Card border radius |
| `--r-sm` | `12px` | Small element border radius |

---

## PWA

- Manifest injected via Blob URL at runtime
- Service worker registered via Blob URL (offline shell caching)
- `beforeinstallprompt` captured for the install banner
- Safe-area insets respected throughout (`env(safe-area-inset-top/bottom)`)
