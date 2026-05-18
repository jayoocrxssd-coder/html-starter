# War Room — Phase 2 Changelog
**CRES Ventures // Internal Dev Doc**
*Compiled by Claude Code — May 18, 2026*

---

## Overview

Phase 2 adds the Plan & Billing system, role-based access control, unique room IDs, the invite link flow, and several UX fixes on top of the Phase 1 Firebase foundation. All changes are additive — nothing from Phase 1 was removed or broken.

**File modified:** `warroom_firebase.html`
**Branch:** `claude/add-plan-badge-settings-ORgKg`
**Commits:** 3

---

## Deliverable 1 — Plan Badge in Settings

**What changed:**
- Added a **"Plan" tab** to the Profile page tab bar (alongside Identity, Appearance, AI, Data, Danger)
- New **Plan & Billing card** inside the Plan tab displays the user's current plan tier with a color-coded badge:
  - `Personal` → neutral badge
  - `Small Business` → blue badge
  - `Enterprise` → amber badge
- Plan details row shows plan name, price, and description
- Role row shows `Owner · Full access` or `Operator · Team member`
- **Upgrade →** button is a placeholder (shows toast: *"Upgrade coming soon — stay locked in."*) — wired for Stripe in Phase 3
- Upgrade button is automatically hidden for Operators

**New functions:** `renderPlanCard()`, `handleUpgradeClick()`

**New CSS classes:** `.plan-badge`, `.plan-personal`, `.plan-small-biz`, `.plan-enterprise`

---

## Deliverable 2 — Workspace Cap on Personal Plan

**What changed:**
- Personal plan users are **blocked from adding a second business** — the `saveBusiness()` function gates at the very top via `checkWorkspaceCap()`
- First business is always allowed; cap triggers on the second attempt
- Instead of a hard error, a **soft upgrade prompt modal** appears:
  - Title: *"Workspace limit reached"*
  - Body explains the 1-workspace limit and suggests upgrading to Small Business
  - Two CTAs: "See Plans →" (placeholder) and "Not now" (dismiss)
- Small Business and Enterprise plans bypass the cap entirely

**New functions:** `checkWorkspaceCap()`, `showUpgradePrompt(reason)`

**New HTML:** `#upgradePromptModal`

---

## Deliverable 3 — Room ID Generation & Display

**What changed:**
- `fbInitUser(user)` is called immediately after successful Google sign-in
- Generates `room_<googleUserId>` on first login — stable, unique, tied to the Google account
- Stores on `S.profile`: `roomId`, `currentPlan`, `role`, `firebaseUid`
- **War Room ID** displayed in Profile → Plan tab with a monospace font and a **Copy ID** button
- `renderRoomId()` auto-populates the display when the profile page renders

**New functions:** `fbInitUser(user)`, `renderRoomId()`, `copyRoomId()`

**New HTML:** `#roomIdDisplay`, `#roomIdRow` (inside Plan & Billing card)

**Data stored on `S.profile`:**
```
S.profile.currentPlan   // 'personal' | 'small_business' | 'enterprise'
S.profile.role          // 'owner' | 'operator'
S.profile.roomId        // 'room_' + googleUserId
S.profile.firebaseUid   // googleUserId from Google OAuth userinfo
```

---

## Deliverable 4 — Owner vs Operator Role Gating

**What changed:**
- `isOwner()` helper checks `S.profile.role` — defaults to `'owner'` if not set (backwards-compatible with existing users)
- `requireOwner(featureName)` shows a toast and returns false if not owner
- **P&L Tracker** (`page-tracker`) shows a locked state for Operators:
  - Rendered by `renderPLLocked()` which replaces the page content
  - Message: *"The room owner controls P&L visibility. Ask your commander to grant access."*
- Upgrade button hidden from Operators in the billing card

**New functions:** `isOwner()`, `requireOwner(featureName)`, `renderPLLocked()`

---

## Deliverable 5 — Invite Link System

**What changed:**
- `getInviteLink()` generates a shareable URL: `<appURL>?join=<roomId>`
- `copyInviteLink()` copies to clipboard and shows a toast
- **Team card** in Profile → Plan tab (visible to Small Business / Enterprise owners only):
  - Shows seat count badge: `N / 3 seats used`
  - Lists all members with initials avatar, name, email, role
  - Member data fetched live from Firestore
- `checkInviteParam()` runs on every boot — detects `?join=<roomId>` in URL:
  - Stashes room ID in `sessionStorage`
  - Shows auth overlay with custom subtitle: *"You've been invited to a War Room. Sign in with Google to join."*
- `handlePendingJoin(user)` runs after sign-in:
  - Writes member doc to `warrooms/<roomId>/members/<uid>` in Firestore
  - Updates user's own doc: `role: 'operator'`, `currentPlan: 'small_business'`
  - Updates local `S.profile` and calls `save()`
  - Cleans URL with `history.replaceState`
  - Shows toast: *"You joined the War Room. Welcome, Operator."*

**Firebase additions:** Firestore imported and exposed as `window._fbDb`

**New functions:** `getInviteLink()`, `copyInviteLink()`, `checkInviteParam()`, `handlePendingJoin(user)`, `renderTeamSection()`, `renderMembersList()`, `renderSeatCount()`

**New HTML:** `#teamCard`, `#membersList`, `#seatCountBadge`

---

## UX Fixes (Phase 2 Session)

### Default Page: Dashboard (not Bills)
- `page-bills` was set as the initial active page in HTML — changed to `page-dashboard`
- `nav-dashboard` is now the active nav item on load
- `bootApp()` now calls `showPage('dashboard')` instead of `renderDashboard()`, ensuring nav highlight, page switch, and mobile nav sync all fire correctly

### Onboarding-First Boot
- New users (no `S.onboarded` flag) now land on the dashboard with the onboarding overlay opening after 500ms — no stray Bills page visible underneath
- Auth overlay remains `display:none` by default; only appears when user explicitly clicks Cloud Sign In or arrives via an invite link

### Nav Bar Reorganisation
The flat nav list was restructured into four labelled sections for better scanability:

| Section | Items |
|---|---|
| **Command** | Dashboard, Mission Board |
| **Operations** | Goals, Intel Notes, P&L Tracker |
| **Schedule** | Focus Timer, Calendar |
| **Finance** | Bills & Expenses, Invoices |
| *(divider)* | Updates |
| *(divider)* | Profile & Settings |

### Scope Fix
- Phase 2 JS functions were initially inserted inside the UI boot IIFE (scope invisible to app)
- Moved into the ENGINE script global scope (same scope as all other app functions)
- Rewrote arrow functions and optional chaining to plain ES5 for engine compatibility

### Toast Notification System
- Added `showToast(msg)` — creates a dismissing pill notification (auto-removes after 3s)
- CSS animation `toastIn` already existed; added matching `.toast-msg` class
- Used throughout Phase 2 for confirmations, errors, and upgrade prompts

---

## Bug Scan Results

37-point automated scan run on final build. **All checks passed.**

Categories verified:
- Phase 2 function scope (all in ENGINE, none in UI IIFE)
- Default page state (dashboard active, bills inactive)
- Boot flow correctness
- Phase 2 HTML elements present
- Workspace cap null-safety
- P&L role gate in showPage
- Firebase Firestore setup
- Nav section labels and IDs
- CSS classes
- renderProfilePage Phase 2 call sites

---

## What Phase 2 Does NOT Include

Intentionally deferred to Phase 3:

- Stripe billing integration
- Real-time Firestore listeners on shared boards
- Presence indicators (who's online)
- Push notifications for task assignments
- P&L visibility toggle (owner controls Operator access)
- Full member management UI (remove members, change roles)

---

## Files Modified

| File | Changes |
|---|---|
| `warroom_firebase.html` | All HTML, CSS, and JS additions listed above |
| Firebase Firestore | New `warrooms/<roomId>/members/<uid>` subcollection on join |
| Firebase Firestore | `role` and `roomId` fields updated on user join |

---

*Phase 1 → Firebase foundation. Phase 2 → Rooms, roles, plans. Phase 3 → Stripe + live sync.*
