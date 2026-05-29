# AXIS — Change Log & Implementation Guide
> Applies to: `app.html` (War Room)  
> Session date: 2026-05-29

---

## Overview

Four improvements were identified and should be applied to the War Room's existing AXIS implementation. The app already has a live AXIS chat page (`#page-axis`), an overlay (`#axisOverlay`), and API key settings in the Profile section. The changes below harden security, fix a logic error, and improve the connection status UX.

---

## Change 1 — Real API Reachability Check

### Problem
The current `sendChat()` / `sendAxisChat()` flow calls the Anthropic API directly, but the status dot (`#aiDot`, `#aiDotAxis`) has no independent "is the API reachable?" check on load. There is no pre-flight validation — the dot stays in its default state until a message is actually sent and either succeeds or fails.

### Fix
Add a lightweight HEAD preflight on page load (and whenever the API key is saved) that pings `https://api.anthropic.com` with `mode: 'no-cors'` and a 5-second timeout. Update the status dot based on the result.

**Where to add — after the `saveProfile()` function (~line 4320) and at the bottom of the init block:**

```js
async function axisCheckReachability() {
  setAxisDotState('connecting');
  try {
    await Promise.race([
      fetch('https://api.anthropic.com', { method: 'HEAD', mode: 'no-cors' }),
      new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 5000))
    ]);
    setAxisDotState('online');
  } catch (_) {
    setAxisDotState('offline');
  }
}

function setAxisDotState(state) {
  // colours: online = accent, connecting = amber, offline = muted red
  const colours = { online: 'var(--accent)', connecting: '#f59e0b', offline: '#ef4444' };
  const dots = [
    document.getElementById('aiDot'),
    document.getElementById('aiDotAxis')
  ];
  dots.forEach(d => {
    if (!d) return;
    d.style.background = colours[state] || colours.offline;
    d.style.animation = state === 'online' ? 'pulse 2s ease-in-out infinite' : 'none';
  });
}
```

**Call it in two places:**
1. At the end of `saveProfile()` after the API key is written to storage.
2. Once during page init (after `loadState()` runs), but only if a key already exists in storage.

---

## Change 2 — API Key Never Stored in Plaintext

### Problem
The API key entered in Profile → AI Settings is written directly to the `S` (state) object and persisted via `localStorage`. Any script on the page — including browser extensions or an XSS payload — can read it with one line.

### Current location
`~line 2943` (input field) and `~line 4320` (`saveProfile` writes `S.profile.apiKey`).

### Fix
Do **not** persist the API key in localStorage. Instead, hold it in a module-scoped variable for the session only. On page reload the user re-enters it. The key field should be an empty password input every session.

```js
// Replace the localStorage-persisted key with a session variable
let _axisSessionKey = '';

function getApiKey() {
  return _axisSessionKey;
}

// In saveProfile(), replace direct storage of the key:
// BEFORE: S.profile.apiKey = document.getElementById('apiKeyInput').value.trim();
// AFTER:
_axisSessionKey = document.getElementById('apiKeyInput').value.trim();
// Do NOT write the key into S or localStorage.
// Clear the field after saving so it's not sitting in the DOM.
document.getElementById('apiKeyInput').value = '';
```

Update every reference that reads `S.profile.apiKey` or `S.profile?.apiKey` to call `getApiKey()` instead. These appear in `buildSystemPrompt()` (~line 4008) and the fetch calls inside `sendChat()` / `runBriefing()`.

Also update the confirmation banner (~line 2954) to show without storing the key:

```js
// Show confirmation without echoing the key value back into the DOM
document.getElementById('apiKeyStatus').textContent = '✓ Key loaded — AXIS is active this session.';
```

---

## Change 3 — Safe Log / Chat Bubble Rendering (XSS)

### Problem
`addChatBubble()` (~line 4138) sets `div.innerHTML = content` where `content` can include formatted text from the AI response. If the API ever returns a response containing `<script>` tags or event attributes, they execute. Currently the HTML is also constructed via string concatenation with user-visible values in `runBriefing()`.

### Fix
Sanitize AI response text before injecting as HTML. Since full Markdown rendering is already happening, apply a minimal allowlist strip before assignment:

```js
function sanitizeHTML(str) {
  // Strip script tags and on* event attributes; allow formatting tags only
  return str
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/\son\w+\s*=\s*["'][^"']*["']/gi, '')
    .replace(/javascript:/gi, '');
}

// In addChatBubble(), wrap the content:
// BEFORE: div.innerHTML = formatted;
// AFTER:
div.innerHTML = sanitizeHTML(formatted);
```

Add the same wrapper anywhere `innerHTML` is set with external/AI-sourced content (search for `.innerHTML =` and verify each one).

---

## Change 4 — Status Badge: Visual Online / Offline / Connecting States

### Problem
The existing `#aiDot` and `#aiDotAxis` dots are static — they don't reflect actual connection state. There's no "connecting" amber state and no pulse animation tied to confirmed reachability.

### Fix — CSS additions (add to the existing stylesheet)

```css
/* AXIS connection states */
#aiDot, #aiDotAxis {
  transition: background 0.3s ease;
}

@keyframes axispulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.4; transform: scale(0.7); }
}
```

The `setAxisDotState()` function from Change 1 drives these states. No additional HTML changes are needed — the existing dot elements are reused.

### Status badge on the AXIS page header

The AXIS page header (`~line 2158`) currently only shows a dot and the name. Add a text label next to the dot so the state is readable at a glance:

```html
<!-- Replace the existing dot+name row in #page-axis header with: -->
<div style="display:flex;align-items:center;gap:6px">
  <div class="ai-dot" id="aiDotAxis"></div>
  <span id="axisStatusLabel" style="font-size:10px;font-weight:600;color:var(--text3);letter-spacing:.06em;text-transform:uppercase">Offline</span>
</div>
```

Update `setAxisDotState()` to also set `#axisStatusLabel` text:

```js
const statusLabel = document.getElementById('axisStatusLabel');
if (statusLabel) {
  statusLabel.textContent = { online: 'Online', connecting: 'Connecting…', offline: 'Offline' }[state] || 'Offline';
}
```

---

## Summary Table

| # | Issue | Severity | Location in app.html |
|---|-------|----------|----------------------|
| 1 | No real reachability check — dot never updates on load | Medium | After `saveProfile()` ~L4320, init block |
| 2 | API key persisted in `localStorage` (plaintext) | **High** | `saveProfile()` ~L4320, `S.profile.apiKey` references |
| 3 | `innerHTML` set with unsanitized AI/external content | **High** | `addChatBubble()` ~L4138, `runBriefing()` |
| 4 | Status dot is static — no online/connecting/offline states | Low | `#aiDot`, `#aiDotAxis` elements + CSS |

---

## Implementation Order

Apply in this order to avoid regressions:

1. **Change 2 first** — remove key from storage before adding any new flows that read it
2. **Change 1** — add `getApiKey()` helper and reachability check (depends on Change 2's session variable)
3. **Change 3** — wrap all `innerHTML` assignments with `sanitizeHTML()`
4. **Change 4** — CSS + label additions (purely additive, safe to do last)
