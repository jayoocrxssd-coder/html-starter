# WAR ROOM — Security & Bug Scan Report

**Scan date:** 2026-05-19  
**Files scanned:** `index.html`, `app.html`  
**Status:** All actionable issues patched ✓

---

## Fixed in this scan

### 1 — Hardcoded admin credentials (CRITICAL) · `app.html`

**Issue:** `submitAdminLogin()` contained a hardcoded check:
```js
if (user === 'admin1' && pass === 'cres100') {
  window._adminLoggedIn = true;
  closeAdminModal();
  // bypasses auth overlay ...
}
```
Even though the "ADMIN LOGIN" button was removed from the UI in a previous session, the function body with the hardcoded credentials remained in the code.

**Fix:** Removed the `if` branch so `submitAdminLogin()` now always returns "Invalid credentials." The `handleAdminLogin` / `closeAdminModal` UI scaffolding is retained but the bypass path is gone.

---

### 2 — XSS in AI chat (CRITICAL) · `app.html`

**Issue:** User-typed chat messages were passed directly to `addChatBubble()` and `addOverlayChatBubble()`, both of which assign via `div.innerHTML`. Typing `<img src=x onerror="alert(1)">` in the chat box would execute arbitrary JS.

**Affected calls:**
```js
addChatBubble('user', text);          // main chat panel
addOverlayChatBubble('user', text);   // overlay chat panel
addChatBubble('user', text);          // overlay → main sync
```

**Fix:** Wrapped user text with the existing `esc()` sanitiser before passing to both functions:
```js
addChatBubble('user', esc(text));
addOverlayChatBubble('user', esc(text));
```
AI response HTML (`briefingHtml`, error strings) is still passed as raw HTML because it is generated internally, not from user input.

---

### 3 — XSS in AI context file preview (HIGH) · `app.html`

**Issue:** The filename of a user-uploaded AI context file was injected unsanitised into `snippet.innerHTML`:
```js
snippet.innerHTML = `<span>${fname} · ${chars} chars</span>...`;
// fname = S.profile.aiContextFilename  (set from file.name)
```
A file named `"><img src=x onerror="alert(1)">` would execute JS.

**Fix:**
```js
snippet.innerHTML = `<span>${esc(fname)} · ${chars} chars</span>...`;
```

---

## Known design limitations (not patched — require backend)

| Issue | Severity | Notes |
|---|---|---|
| Passwords stored as base64 (`btoa`) | HIGH | Not a real hash — trivially reversible. Safe only because auth lives entirely in `localStorage`. Replace with bcrypt/argon2 when migrating to a real auth provider. |
| `wr_access` token is just the string `'1'` | MEDIUM | Any JS can forge it. Acceptable for a localStorage-only app; upgrade to a signed JWT when moving to a real auth provider. |
| No login rate limiting | MEDIUM | Client-side only — trivially bypassed. Enforce server-side when auth is moved off `localStorage`. |
| Forgot password has no email verification | LOW | Current flow just checks the email exists in `wr_accounts` and lets the user reset without any email confirmation. This is a UX tradeoff, not a security risk while auth is localStorage-only. |

---

## Already-clean items (confirmed)

- `esc()` helper correctly applied to all business names and goal text in `innerHTML` insertions
- Auth gate in `app.html` strips `?bypass=1` exploit — no URL param can skip auth
- `signOut()` clears all three auth tokens (`wr_access`, `wr_user_email`, `wr_user_google`) and redirects to `/`
- No XSS risks in `index.html` — user data set via `.textContent`, not `.innerHTML`
- `netlify.toml` security headers: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, HSTS, `Referrer-Policy`

---

*WAR ROOM v5.1 · CRES Ventures*
