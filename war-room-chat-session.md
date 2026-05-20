# WAR ROOM v5.1 — Fix Session Log

**Date:** 2026-05-20  
**Branch:** `claude/fix-google-login-json-F9o9p`  
**Repo:** `jayoocrxssd-coder/html-starter`

---

## Problem

> "Whenever I log in through Google it prompts me this message: **Error unpacking: Unexpected non-whitespace character after JSON at position 238786 (line 2 column 238786)**"

### Root Cause

The WAR ROOM app bundles its entire HTML as a JSON string inside a `<script type="__bundler/template">` tag. At runtime, `JSON.parse(templateEl.textContent)` decodes it and replaces the DOM.

Two issues were found:

1. **`</script>` tags inside the JSON** — The bundler must escape `</script` as `<\/script` inside JSON strings to prevent the browser's HTML parser from closing the outer `<script>` tag prematurely. The deployed version had a broken re-encoding step that left raw `</script>` tags in the JSON.

2. **Mock Google sign-in** — `handleGoogleSignIn` in `index.html` was a fake that just set `localStorage` and redirected after a `setTimeout`. No real OAuth ever ran.

---

## How the Auth System Works

### Account Storage
- Accounts live in `localStorage` under key `wr_accounts` as `{ [email]: { hash, created } }`
- `wr_access = '1'` is the auth gate token — set on sign-in, cleared on sign-out
- Passwords were originally stored as `btoa(pass)` — plain Base64, trivially reversible

### Sign-in Flow
1. User submits email + password → `handleAuthSubmit()` → `handleAuth()`
2. `handleAuth()` hashes the password, compares against stored hash
3. On match: sets `wr_access = '1'` and closes the overlay

### Google Sign-in (original — mock)
```js
function handleGoogleSignIn() {
  setTimeout(() => {
    localStorage.setItem('wr_access', '1');
    localStorage.setItem('wr_user_google', '1');
    setTimeout(() => closeAuthOverlay(), 900);
  }, 800);
}
```
No real OAuth. Anyone could set these localStorage values manually.

---

## Fixes Applied

### 1. JSON Bundler Round-Trip Fix
Restored clean zip files to the repo. The encoding pipeline now correctly escapes `</script` → `<\/script` in the JSON string.

### 2. Real Firebase Google Sign-In
**Chosen approach:** Firebase Auth compat SDK (v10.12.0) with `signInWithPopup`.

```js
function _loadScript(src) {
  return new Promise((res, rej) => {
    const s = document.createElement('script');
    s.src = src; s.onload = res; s.onerror = rej;
    document.head.appendChild(s);
  });
}

async function handleGoogleSignIn() {
  const btn = document.getElementById('googleSignInBtn');
  const sucEl = document.getElementById('authSuccess');
  const errEl = document.getElementById('authError');
  if (btn) { btn.disabled = true; btn.textContent = 'Connecting...'; }
  if (errEl) errEl.textContent = '';
  try {
    if (!window._fbAuthApp) {
      await _loadScript('https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js');
      await _loadScript('https://www.gstatic.com/firebasejs/10.12.0/firebase-auth-compat.js');
      window._fbAuthApp = firebase.apps.length
        ? firebase.apps[0]
        : firebase.initializeApp({
            apiKey: 'AIzaSyBcdKlkPBlLxs6barPZDAgoPlB9iU82Zkg',
            authDomain: 'createwarrom.firebaseapp.com',
            projectId: 'createwarrom'
          });
    }
    const auth = firebase.auth();
    const result = await auth.signInWithPopup(new firebase.auth.GoogleAuthProvider());
    const user = result.user;
    localStorage.setItem('wr_access', '1');
    localStorage.setItem('wr_user_google', '1');
    localStorage.setItem('wr_google_name', user.displayName || '');
    localStorage.setItem('wr_google_email', user.email || '');
    localStorage.setItem('wr_google_picture', user.photoURL || '');
    if (sucEl) sucEl.textContent = '✓ Signed in as ' + (user.email || 'Google User') + '. Launching War Room...';
    setTimeout(() => closeAuthOverlay(), 900);
  } catch (e) {
    if (btn) { btn.disabled = false; btn.textContent = 'Continue with Google'; }
    if (errEl) errEl.textContent = e.code === 'auth/popup-closed-by-user'
      ? 'Sign-in cancelled.' : 'Google sign-in failed. Please try again.';
  }
}
```

**Firebase project:** `createwarrom` (`createwarrom.firebaseapp.com`)

> **You need to do this in Firebase Console:**
> 1. Authentication → Sign-in method → Enable **Google**
> 2. Authentication → Settings → Add your deployed domain to **Authorized Domains**

### 3. PBKDF2 Password Hashing
**Chosen approach:** Web Crypto API PBKDF2 — 150,000 iterations, SHA-256, per-email salt.

Replaced `btoa(pass)` in both `index.html` and `app.html`:

```js
async function _hashPwd(email, pass) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey('raw', enc.encode(pass), 'PBKDF2', false, ['deriveBits']);
  const bits = await crypto.subtle.deriveBits(
    { name: 'PBKDF2', salt: enc.encode('wr:' + email.toLowerCase()), iterations: 150000, hash: 'SHA-256' },
    key, 256
  );
  return btoa(String.fromCharCode(...new Uint8Array(bits)));
}
```

All callers updated to `async`/`await`:
- `handleAuth()` → `async`, uses `await _hashPwd()`
- `handleAuthSubmit()` → `async`, uses `await handleAuth()`
- `handleResetPassword()` → `async`, uses `await _hashPwd()`

**Applied to:** `index.html` (landing page auth) + `app.html` (in-app auth overlay)

---

## Verification Results

| Check | Result |
|---|---|
| JSON parse round-trip (both files) | ✅ Clean |
| `handleGoogleSignIn` uses Firebase `signInWithPopup` | ✅ |
| Firebase SDKs loaded dynamically | ✅ |
| No `setTimeout` mock remaining | ✅ |
| `_hashPwd` uses PBKDF2 / 150k iter / SHA-256 | ✅ |
| `handleAuthSubmit` is `async` + `await handleAuth()` | ✅ |
| `handleAuth` is `async` | ✅ |
| No plain `btoa(pass)` remaining | ✅ |
| `</script>` properly escaped in JSON strings | ✅ |

---

## Commits

| SHA | Message |
|---|---|
| `3d54c1b` | Fix: deploy clean War Room v5.1 bundle to resolve JSON unpack error |
| `3aa6f50` | Fix Google sign-in (Firebase OAuth) and upgrade password hashing to PBKDF2 |
| `d4451c7` | Remove temporary patch scripts |
| `f0a6ec9` | Refactor Firebase script loading into `_loadScript` helper |

---

## Known Limitations

- **`localStorage` as auth store** — `wr_access = '1'` is client-side only; no server-side validation. By design for this standalone app.
- **Google sign-in result is local only** — The Firebase token is not persisted or validated server-side; only `wr_access`, `wr_google_email` etc. are stored in `localStorage`.
- **PBKDF2 salt is deterministic** — Salt is derived from the email, not random. Provides per-user uniqueness but not the full protection of a random salt. Sufficient for the app's threat model.
- **Firebase API key is public** — Expected for Firebase web apps. Security enforced via Firebase security rules, not by keeping the key secret.

---

## v5.2 — Onboarding Sync & Blog (2026-05-20)

**Branch:** `claude/fix-onboarding-sync-blog-MfPRc`

### Changes Applied

#### 1. Email signup now triggers onboarding
`handleAuth()` in signup mode previously called `closeAppAuthOverlay()` and stopped. Added a chained `setTimeout` that calls `initOnboarding()` if `!S.onboarded` after the overlay closes.

#### 2. Email auth now creates a Supabase session
Both `signUp` and `signIn` paths in `handleAuth()` now call `_sb.auth.signUp()` / `_sb.auth.signInWithPassword()` when the Supabase client is available. This triggers `onAuthStateChange` → `syncFromCloud()` → sets `currentUser`, enabling cloud sync for email/password users (previously only Google sign-in users got cloud sync).

#### 3. Fixed undefined `startOnboarding` call in Google sign-in
`handleGoogleSignIn()` called `startOnboarding()` (undefined). Changed to `initOnboarding()`.

#### 4. Cloud sync retry after onboarding completes
`obFinish()` now schedules a `saveToCloud(true)` 2.5 s after calling `save()`, giving time for `onAuthStateChange` to set `currentUser` before the cloud push runs.

#### 5. Landing page changelog section
Added a `#changelog` section to `index.html` (landing page) with three entries covering v5.0, v5.1, and v5.2. Added the section to the topbar nav and wired the footer "Changelog" link.

### Verification Checklist

| Check | Result |
|---|---|
| Email signup → onboarding wizard appears | ✅ |
| Email signup → Supabase auth session created | ✅ |
| Email sign-in → Supabase auth session restored | ✅ |
| `startOnboarding` → `initOnboarding` | ✅ |
| `obFinish` retries cloud save | ✅ |
| Landing page changelog section renders | ✅ |
| Footer "Changelog" link scrolls to section | ✅ |
| Nav "Changelog" link added | ✅ |
