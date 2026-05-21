# War Room — Landing Page Firebase Wiring

## Firebase Project
| Key | Value |
|-----|-------|
| Project ID | `createwarrom` |
| Auth Domain | `createwarrom.firebaseapp.com` |
| API Key | `AIzaSyBcdKlkPBlLxs6barPZDAgoPlB9iU82Zkg` |
| Auth methods | Email/Password |

---

## How the Auth Flow Works

### SDK Loading
Firebase is **not** bundled — it lazy-loads on first auth action so the landing page stays fast:
```
firebase-app-compat.js   (10.12.0)
firebase-auth-compat.js  (10.12.0)
```
Loaded via `_loadScript()` only when the user clicks Sign In or Create Account for the first time.

---

### Sign-In Flow
1. User clicks **Log In** → auth overlay opens in `signin` mode
2. User submits email + password → `handleAuthSubmit()` → `handleAuth()`
3. Firebase SDK lazy-loads if not already present
4. `auth.signInWithEmailAndPassword(email, password)` called directly
5. On success → overlay closes → `window.location.replace('app.html')` after 400ms
6. On failure → error message shown from Firebase error code

### Sign-Up Flow
1. User clicks **Get Access** → auth overlay opens in `signup` mode
2. User fills email + password + confirm → `handleAuthSubmit()` → `handleAuth()`
3. Passwords validated client-side (match + min 6 chars)
4. `auth.createUserWithEmailAndPassword(email, password)` called
5. On success → overlay closes → `window.location.replace('app.html')` after 400ms
6. On failure → error message shown from Firebase error code

### Forgot Password
1. User clicks "Forgot password?" → mode switches to `forgot`
2. User enters email → `handleForgotPassword()`
3. `firebase.auth().sendPasswordResetEmail(email)` sends a real reset email
4. Success/error message shown inline — no page redirect

---

## Error Codes Handled

| Firebase Code | Message Shown |
|---|---|
| `auth/invalid-credential` | No account found or incorrect password. |
| `auth/user-not-found` | No account found or incorrect password. |
| `auth/wrong-password` | Incorrect password. Please try again. |
| `auth/email-already-in-use` | An account with this email already exists. Sign in instead. |
| `auth/weak-password` | Password must be at least 6 characters. |
| `auth/invalid-email` | Enter a valid email address. |
| `auth/too-many-requests` | Too many attempts. Please wait and try again. |
| `auth/user-not-found` (reset) | No account found for that email. |

---

## What Was Fixed

### 1. `handleAuth()` — localStorage → Firebase
**Was:** Checked a `wr_accounts` hash stored in `localStorage`. Any device that hadn't run sign-up locally would get "No account found" even with valid Firebase credentials.

**Now:** Calls Firebase directly. `localStorage` is only used to cache the session token after a successful login — not for credential verification.

### 2. `handleForgotPassword()` — localStorage → Firebase email
**Was:** Looked up the email in `localStorage`, then routed to an in-app reset form that only updated a local hash. Completely non-functional across devices.

**Now:** Calls `sendPasswordResetEmail(email)` — Firebase sends a real password reset link to the user's inbox.

### 3. `handleResetPassword()` — removed
**Was:** Updated a PBKDF2 hash in `localStorage`. Had no effect on the user's actual Firebase credentials.

**Now:** Delegates to `handleForgotPassword()` so the email reset flow runs instead.

### 4. `handleAuthSubmit()` — missing `async`
**Was:** Declared as a regular (non-async) function but called `await handleAuth()` inside — the `await` was silently ignored, making Firebase errors unhandled.

**Now:** Declared `async function handleAuthSubmit()` so `await` works correctly and the disabled-button finally-block fires properly.

### 5. `_hashPwd()` — dead code removed
**Was:** PBKDF2 hashing utility used by the old localStorage auth. Left orphaned after the auth fix.

**Now:** Removed entirely.

---

## File Structure
```
index.html   → Landing page  (this file)
app.html     → War Room app  (full command center)
```

Both files must be in the **same directory** for the redirect (`window.location.replace('app.html')`) to resolve correctly.

---

## Deployment Notes
- Works on any static host (Vercel, Netlify, GitHub Pages, direct file serving)
- No server-side code required — Firebase handles all auth
- Firebase project must have **Email/Password** sign-in method enabled in the console (`createwarrom` → Authentication → Sign-in method)
