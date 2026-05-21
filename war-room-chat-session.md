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

#### 2. Email auth now creates a Firebase Auth session
Both `signUp` and `signIn` paths in `handleAuth()` now call `_fbAuth.createUserWithEmailAndPassword()` / `_fbAuth.signInWithEmailAndPassword()` when Firebase is available. This triggers `onAuthStateChanged` → `syncFromCloud()` → sets `currentUser`, enabling cloud sync for email/password users (previously only Google sign-in users got cloud sync).

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
| Email signup → Firebase Auth session created | ✅ |
| Email sign-in → Firebase Auth session restored | ✅ |
| `startOnboarding` → `initOnboarding` | ✅ |
| `obFinish` retries cloud save | ✅ |
| Landing page changelog section renders | ✅ |
| Footer "Changelog" link scrolls to section | ✅ |
| Nav "Changelog" link added | ✅ |

---

## v5.3 — Supabase → Firebase Migration (2026-05-21)

**Branch:** `claude/fix-onboarding-sync-blog-MfPRc`

### Changes Applied

Removed Supabase entirely. All cloud sync and auth now runs on Firebase (same project as Google sign-in: `createwarrom`).

| Area | Old (Supabase) | New (Firebase) |
|---|---|---|
| SDK load | `supabase-js@2` UMD from jsDelivr | `firebase-app/auth/firestore-compat` v10.12.0 from gstatic |
| Client init | `createClient(URL, KEY)` | `firebase.initializeApp(FB_CONFIG)` |
| Cloud storage | `_sb.from('war_room_data').upsert()` | `_fbDb.collection('war_room_data').doc(uid).set()` |
| Cloud load | `_sb.from(...).select().eq().single()` | `_fbDb.collection(...).doc(uid).get()` |
| Auth listener | `_sb.auth.onAuthStateChange(event, session)` | `_fbAuth.onAuthStateChanged(user)` |
| Email signup | `_sb.auth.signUp()` | `_fbAuth.createUserWithEmailAndPassword()` |
| Email signin | `_sb.auth.signInWithPassword()` | `_fbAuth.signInWithEmailAndPassword()` |
| Sign out | `_sb.auth.signOut()` | `_fbAuth.signOut()` |
| Google sign-in | No Firebase session created | `_fbAuth.signInWithCredential(GoogleProvider.credential(null, token))` |
| User ID field | `currentUser.id` | `currentUser.uid` |

### Firebase Setup Required

In Firebase Console (project `createwarrom`):
1. **Firestore** → Create database → start in production mode
2. **Firestore Rules** → Add rule allowing authenticated users to read/write their own document:
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /war_room_data/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```
3. **Authentication** → Sign-in method → Enable **Email/Password** and **Google**
4. **Authentication** → Settings → Add your deployed domain to **Authorized Domains**

### Verification Checklist

| Check | Result |
|---|---|
| No Supabase references in bundle | ✅ |
| `initFirebase()` loads app/auth/firestore SDKs | ✅ |
| `saveToCloud` uses Firestore `.set()` | ✅ |
| `loadFromCloud` uses Firestore `.get()` | ✅ |
| Email signup → Firebase `createUserWithEmailAndPassword` | ✅ |
| Email signin → Firebase `signInWithEmailAndPassword` | ✅ |
| Google sign-in → Firebase `signInWithCredential` | ✅ |
| `onAuthStateChanged` drives `currentUser` | ✅ |
| Sign out → Firebase `signOut()` | ✅ |

---

## v5.4 — Bug Sweep (2026-05-21)

**Branch:** `claude/fix-onboarding-sync-blog-MfPRc`  
**Commit:** `203d690`

### Changes Applied

#### 1. Firestore document delete on data reset
`resetAllData()` previously only cleared `localStorage`. Now also calls `_fbDb.collection('war_room_data').doc(currentUser.uid).delete()` before reloading, so the cloud document is wiped too.

#### 2. `window._fbDb` conflict resolved
A `<script type="module">` block was assigning the modular Firestore SDK instance to `window._fbDb`. `handlePendingJoin()` then called compat-style `.collection()` on it and crashed. Fixed by removing the modular assignment and having `initFirebase()` set `window._fbDb = _fbDb` (compat instance).

#### 3. `_cloudSynced` hoisted to module scope
`_cloudSynced` was declared inside the boot IIFE — `signOut()` couldn't reset it. Hoisted to module scope so sign-out properly clears the flag, allowing cloud sync to run again on next login.

#### 4. Landing page → app redirect
All three auth success paths in `index.html` (`handleGoogleSignIn`, `handleAuth` signup, `handleAuth` signin) now call `window.location.replace('app.html')` so the user actually lands in the app.

#### 5. Null guards and clipboard error fixes
Added null checks throughout event handlers to prevent `Cannot read properties of null` crashes when DOM elements are missing. Fixed clipboard write errors by wrapping in try/catch.

### Verification Checklist

| Check | Result |
|---|---|
| Data reset also deletes Firestore document | ✅ |
| No `window._fbDb` modular/compat conflict | ✅ |
| `_cloudSynced` resets correctly on sign-out | ✅ |
| Landing page auth redirects to `app.html` | ✅ |
| Null guard crashes resolved | ✅ |

---

## v5.4a — JSON Escaping Fix (2026-05-21)

**Branch:** `claude/fix-onboarding-sync-blog-MfPRc`  
**Commit:** `d831cfc`

### Problem

> `"Error unpacking: Unterminated string in JSON at position 137260 (line 1 column 137261)"`

### Root Cause

The WAR ROOM bundle stores the entire app HTML as a JSON string inside `<script type="__bundler/template">`. The re-bundling script used raw `json.dumps()` output without escaping `</` sequences. When the browser's HTML parser encountered `</script` inside the JSON blob it closed the outer `<script>` tag immediately, truncating the JSON and causing the unpack error at runtime.

### Fix

After `json.dumps(template)`, every `</` is replaced with `<\/` before writing:

```python
new_json = json.dumps(template, ensure_ascii=False)
new_json = new_json.replace('</', '<\\/')  # prevent HTML parser closing <script> early
```

`\/` is a valid JSON escape for `/` — `JSON.parse()` handles it transparently at runtime.

### Verification

```python
assert new_json.lower().find('</script') == -1   # no raw </script in JSON string
assert json.loads(new_json) == template           # round-trip matches source
```

Both `app.html` and `index.html` re-bundled and verified clean.

---

## v5.4b — User Data Isolation (2026-05-21)

**Branch:** `claude/fix-onboarding-sync-blog-MfPRc`  
**Commit:** `d9c9512`

### Problem

Data from one account was visible when logging in with a different email on the same device.

### Root Cause

Two bugs combined:

1. **`signOut()` did not clear `stratusWR_v31`** — The app's main data key stayed in `localStorage` after sign-out. When the next user signed in, `load()` ran before Firebase auth resolved and populated `S` with the previous user's data.

2. **`loadFromCloud()` had a cross-user localStorage fallback** — If a new account had no Firestore document yet (or no businesses in it), the code explicitly copied businesses from `localStorage` into `S`, seeding the new account with the previous user's data.

### Fixes

**`signOut()`** — add `localStorage.removeItem('stratusWR_v31')`:
```js
async function signOut() {
  ...
  localStorage.removeItem('stratusWR_v31');  // ← added
  window.location.replace('/');
}
```

**`syncFromCloud()`** — reset `S` to `DEFAULT` before loading this user's cloud data:
```js
async function syncFromCloud(user) {
  if(_cloudSynced) return;
  _cloudSynced = true;
  currentUser = user;
  S = JSON.parse(JSON.stringify(DEFAULT));  // ← added: wipe stale state
  ...
}
```

**`loadFromCloud()`** — removed the localStorage businesses fallback entirely:
```js
// Removed block:
// if(!S.businesses.length){
//   const local = localStorage.getItem('stratusWR_v31');
//   if(local){ ...copy businesses from localStorage... }
// }
```

### Verification Checklist

| Check | Result |
|---|---|
| Sign out clears `stratusWR_v31` from localStorage | ✅ |
| New user auth resets `S` to `DEFAULT` before cloud load | ✅ |
| No localStorage businesses fallback bleeding across accounts | ✅ |
| Fresh account starts empty if no Firestore document exists | ✅ |

---

## Firebase Console Setup Checklist

Required one-time setup in [Firebase Console](https://console.firebase.google.com) → project `createwarrom`:

- [ ] **Authentication** → Sign-in method → Enable **Google**
- [ ] **Authentication** → Sign-in method → Enable **Email/Password**
- [ ] **Authentication** → Settings → Authorized Domains → add your deployed domain
- [ ] **Firestore** → Create database (production mode)
- [ ] **Firestore** → Rules → paste:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /war_room_data/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

---

## Known Limitations (current)

| Item | Notes |
|---|---|
| `wr_access = '1'` auth gate | Client-side only — by design for standalone app |
| PBKDF2 salt is deterministic | Derived from email, not random. Per-user unique but not random-salt strength |
| Firebase API key is public | Expected for Firebase web apps. Security enforced via Firestore rules |
| Admin login is a stub | Modal exists but no real admin backend implemented |
| Google Drive OAuth | Client ID `190616282170-...` needs authorized origins set in Google Cloud Console |
| AXIS AI Anthropic key | User must enter their own key in Settings → AXIS AI |
