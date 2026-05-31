# Stratus — Feature Build Changelog

## Overview

Complete add-on stack built across 4 phases on branch `claude/youthful-bohr-9xsb9`.
All features are implemented in a single self-contained HTML file (`stratus.html`),
persisted via `localStorage`, and fully compatible with both dark and light modes.

---

## Phase 1 — Core Foundation

### Natural Language Input
- Smart parser (`nliParse`) detects category, time-of-day, and frequency keywords as you type in any input field
- Covers all major inputs: Home quick-add, Calendar add sheet, Habit creation sheet
- Detected values surface as a tap-to-apply hint chip below the input
- Category detection: Fitness, Finance, Mindset, Health, Learning, Career
- Time detection: Morning, Afternoon, Evening
- Frequency detection: Daily, 5x/wk, 4x/wk, 3x/wk

### Focus Mode
- Full-screen overlay triggered via the ⚡ button on any Routine habit row
- Live countdown timer with pause/resume
- "Mark done ✓" marks the habit complete and exits
- "Exit" closes without marking done
- Accent color applied dynamically to match user theme

### Live Time Tracking
- Cumulative focus time tracked in `focusTotalSeconds` across all sessions
- "Today's focus time" stat card on the Home view
- Focus session count tracked separately (`focusSessionCount`)
- Both values persisted to `localStorage` and restored on reload

### Habit Tracker
- Already present in the base build — Phase 1 complete
- Enhanced with NLI integration and Focus Mode triggers

### Light Mode
- Toggle in Profile → Appearance accordion
- Switches all CSS custom properties (`--bg`, `--card`, `--card2`, `--card3`, `--white`, `--off-white`, `--muted`, `--muted2`) to light values
- Persisted to `localStorage` as `theme: 'light' | 'dark'`
- Restored correctly on reload including toggle state

---

## Phase 2 — AI Intelligence Layer

### Personalized Productivity Profile
- Card in Profile view showing: weekly consistency score + bar, productivity style badge, focus area chips
- Style badge: **High Output** (≥80%), **Building** (≥50%), **Developing** (<50%), **Getting Started** (no habits)
- Focus areas sourced from onboarding `obFocuses[]` or derived from habit categories
- Updates live whenever habits change

### AI Schedule Optimization
- "✦ Optimize" button on the Home AI Schedule card
- Pulls today's calendar events + unfinished habits as virtual tasks
- Sorts by energy pattern: Fitness/Health → early, Finance/Career → afternoon, Mindset → evening
- Assigns optimal time slots (6:00 AM → 8:00 PM) and renders a preview schedule
- Shows count of tasks optimized

### Automated Focus Blocks
- Toggle in Routine view
- When enabled, generates up to 4 timed deep-work blocks for all incomplete habits
- Each block is tappable to launch Focus Mode directly
- State (`focusBlocksEnabled`) persisted to `localStorage` and restored correctly (including `false` state)

### Priority Recalibration
- Warning banner + "⚠ Recalibrate priorities" button appear on the Home hero card
- Triggers only for habits that are actively behind pace (< 50% done with an established streak)
- "Recalibrate" re-sorts the habit list by urgency (least % done first) and re-renders
- Banner and button are hidden when all habits are on track

---

## Phase 3 — Voice & Smart Notifications

### Voice-to-Schedule
- 🎙 Voice button alongside the Optimize button on the Home AI Schedule card
- Uses Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`)
- Live transcription shown in a status line below the schedule preview
- Stop button turns red while listening; one tap stops recognition
- `processVoiceInput()` strips filler words ("add", "remind me to", "i need to", etc.), runs `nliParse` for category + time, and pushes the event to today's calendar
- Graceful fallback toast if browser doesn't support speech recognition or mic is denied
- Auto-runs schedule optimization after adding the voice entry

### Smart Reminders / Context Pings
- Toggle in Profile → Notifications ("Smart context pings")
- Fires time-aware nudges based on current hour and pending habits:
  - **6–9 AM** Morning check-in with first pending habit name
  - **12–2 PM** Midday progress update
  - **5–8 PM** Evening wind-down count
  - **8 PM+** Last-call list of remaining habits
- Checks every 30 seconds (real-world use: configurable interval)
- Delivers via `showToast()` for in-app display
- Also fires native browser `Notification` if permission is granted
- State persisted and restored; `startSmartPings()` auto-resumes on reload if enabled

---

## Phase 4 — Surface & Analytics

### Deep Work Analytics
- 5th nav tab: **Analytics** (chart icon)
- **Focus time** card: Today's focus time, total sessions, average session length
- **Weekly output** card: Per-habit progress bars showing done/target for the week
- **Streak leaderboard**: All habits ranked by current streak, #1 highlighted in accent color
- **7-day completion heatmap**: Bar chart of daily completion rates (full accent ≥70%, dimmed ≥40%, muted <40%)
- **Goal progress summary**: All active goals with progress bars and % complete
- All data updates live when navigating to the tab
- `focusSessionCount` persisted alongside `focusTotalSeconds`

### Home Screen Widget (PWA Install)
- App manifest injected via `<link rel="manifest">` with app name, icons, display mode, and theme color
- Dismissible install banner appears on the Home view when the browser fires `beforeinstallprompt`
- "Add to Home Screen" button triggers the native install prompt
- `appinstalled` event handled with confirmation toast
- Dismiss state stored in `localStorage` (`stratus_install_dismissed`) so the banner doesn't re-appear
- Graceful fallback message if the install prompt isn't available (direct "Add to Home Screen" instruction)

---

## Bug Fixes & Hardcoded Value Corrections

| Fix | Details |
|---|---|
| `TODAY_IDX` hardcoded to Friday | Now computed dynamically: `(new Date().getDay() + 6) % 7` |
| Calendar defaulted to May 1 2026 | `selYear/selMonth/selDay` now initialized from `new Date()` |
| Hero name hardcoded to "Jaylen" | Defaults to "you" until onboarding or profile name is set |
| "Member since May 2026" hardcoded | Now stored in `localStorage` on first visit, reflects real join month |
| `focusBlocksEnabled` not restored as `false` | Changed to `!== undefined` check with explicit `!!` cast |
| Priority recal fired on brand-new habits | Removed `noStreak` filter; only tracks habits actively behind pace |
| `focusTotalSeconds` not persisted | Added to `saveToStorage` snapshot and restored in `loadFromStorage` |
| NLI time tap-to-apply did nothing | Added `id="hcat-time-btns"` and `id="sheet-time-btns"` and passed to `nliAttach` |
| `toggleLightMode` double-toggled class | `applyTheme` now owns toggle state; `toggleLightMode` just reads intent |
| `focusSessionCount` declared after first use | Moved declaration to Focus Mode block alongside other focus state vars |

---

## Technical Notes

- **Single file**: All HTML, CSS, and JS in `stratus.html` — no build step, no dependencies beyond Google Fonts
- **Storage key**: `stratus_v1` in `localStorage`
- **Theme**: CSS custom properties on `.phone` — all features respect dark/light mode
- **Nav**: 5 tabs — Home, Calendar, Routine, Profile, Analytics
- **Function count**: 105 JS functions
- **Lines of code**: ~3,400
