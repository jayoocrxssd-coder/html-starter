# War Room — Changelog

---

## Session — 2026-05-29

### New Features

**1. Dynamic Theme System (Light + Dark)**
- Rebuilt `THEMES` object from scratch — all 8 themes (Sand, Midnight, Forest, Ember, Obsidian, Aurora, Slate, Rose) now have complete `light` and `dark` palette pairs
- Every theme carries full semantic color tokens: `--red`, `--green`, `--amber`, `--blue`, `--violet`, `--pink` and their `-bg` variants, plus `--surface2`
- Colors are harmonized to each theme's aesthetic so dark mode feels native, not just inverted
- `applyTheme()` is the sole source of truth — sets all CSS vars on `:root` via inline `style.setProperty()` calls

**2. Bulk-Delete "Dump" Button (Kanban)**
- New `dumpCompletedMissions()` function added to the Strategy / Kanban board
- Dumps all completed (Done) missions in one action, respecting the active business filter
- Protected by a danger confirmation dialog before any deletion

**3. AXIS Full Page**
- AXIS AI assistant promoted from an overlay to its own full nav page (`#page-axis`)
- Smooth navigation via the sidebar AXIS nav item or the dashboard expand button
- Full-height chat interface with briefing and reset controls
- Reuses all existing API key / context / chat history logic — no duplication

**4. Client Roster Tab (Business Profiles)**
- New "Clients" tab inside every Business Command profile
- Add, edit, and delete clients with name, contact, email, value, and notes fields
- Client count badge shown on the tab
- `clients: []` added to the default state structure with load guard

---

### Bug Fixes

**Dark mode breaks theme colors** *(root cause + fix)*
- **Problem:** The `.dark` CSS class on `body` hardcoded Sand dark palette values. Because CSS custom properties inherit from the nearest ancestor, `body.dark` vars shadowed `applyTheme()`'s theme-specific vars on `html` for all child elements — every theme showed Sand colors in dark mode.
- **Fix:** Removed all `--variable` declarations from the `.dark {}` rule. `applyTheme()` now exclusively controls all palette values.

**localStorage migration was a silent no-op**
- **Problem:** Migration code read from `'warRoomWR_v31'` (the destination key) instead of `'stratusWR_v31'` (the old key), so the condition was never true and users' existing data was silently lost on first launch.
- **Fix:** Corrected source key to `'stratusWR_v31'` and remove target to `localStorage.removeItem('stratusWR_v31')`.

**`accent-fg` always resolved to `#ffffff`**
- **Problem:** Ternary `isDark ? '#ffffff' : '#ffffff'` — both branches identical. In light themes with a bright accent color this rendered invisible white-on-white text.
- **Fix:** Changed to `lum2 > 0.5 ? themeColors.bg : '#ffffff'` so bright accents get a contrasting dark foreground from the theme's own background color.

**`nextId is not defined` (ReferenceError)**
- **Problem:** `saveEmployee` (pre-existing) and `saveClient` (new) both called an undefined function `nextId()`. Every other save function in the codebase uses `S.nextId++`.
- **Fix:** Replaced both `nextId()` calls with `S.nextId++`.

---

### Files Changed
- `app.html` — all features and fixes above
- `.gitignore` — added to exclude `node_modules/`
- `package.json` — added `playwright` dev dependency for verification
- `package-lock.json` — generated

---

### Branch
`claude/peaceful-babbage-RSvla`
