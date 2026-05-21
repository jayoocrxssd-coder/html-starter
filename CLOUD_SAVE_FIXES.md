# War Room — Cloud Save Fixes

## What Was Broken

The Firebase SDK, config, and Firestore functions (`saveToCloud`, `loadFromCloud`) were all present in the code, but the **auth layer was bypassing Firebase entirely** — so `currentUser` was never set and cloud sync silently did nothing.

---

## Fixes Applied

### 1. Sign-In / Sign-Up (`handleAuth`) — *Main blocker*
**Before:** Auth checked a locally stored account hash in `localStorage`. Signing in on any device other than where you first created your account returned "No account found." Firebase was called as a silent afterthought with errors swallowed.

**After:** Calls Firebase directly:
- `_fbAuth.createUserWithEmailAndPassword()` for sign-up
- `_fbAuth.signInWithEmailAndPassword()` for sign-in

Firebase's `onAuthStateChanged` fires on success → `syncFromCloud` runs → Firestore data loads.

Proper error messages for all Firebase error codes (`auth/invalid-credential`, `auth/email-already-in-use`, `auth/too-many-requests`, etc.).

---

### 2. Forgot Password (`handleForgotPassword`)
**Before:** Checked `localStorage` for the account, routed to an in-app password reset form. Completely local — useless on any other device.

**After:** Calls `_fbAuth.sendPasswordResetEmail(email)` — sends a real reset email through Firebase.

---

### 3. Reset Password (`handleResetPassword`)
**Before:** Updated a local `localStorage` hash. Did nothing to Firebase's actual credentials.

**After:** Delegates to Firebase's email-based reset (the correct flow).

---

### 4. Google Sign-In (`handleGoogleSignIn`)
**Before:** Got a Google OAuth access token, fetched the user profile manually, then built a fake user object — never touched Firebase auth. `currentUser` was never set, so `saveToCloud` / `loadFromCloud` returned immediately without doing anything.

**After:** After getting the Google access token, calls:
```js
firebase.auth.GoogleAuthProvider.credential(null, res.access_token)
_fbAuth.signInWithCredential(credential)
```
This registers the user with Firebase, fires `onAuthStateChanged`, and cloud sync runs properly.

---

## How Cloud Sync Now Works (End to End)

1. App loads → reads from `localStorage` immediately (offline-first)
2. Firebase SDK lazy-loads in background
3. `onAuthStateChanged` listener registered
4. **If user was already signed in** (persisted session) → `syncFromCloud` fires automatically
5. **If user signs in via the form** → Firebase auth → `onAuthStateChanged` → `syncFromCloud`
6. `syncFromCloud` → `loadFromCloud` reads from Firestore → merges with local state
7. Every `save()` call → writes `localStorage` + debounced write to Firestore (`war_room_data/{uid}`)
8. Sign-out resets `currentUser` and `_cloudSynced` so next sign-in re-syncs cleanly

---

## Firebase Project

- **Project ID:** `createwarrom`
- **Auth Domain:** `createwarrom.firebaseapp.com`
- **Firestore collection:** `war_room_data/{uid}`
- **Auth methods:** Email/Password + Google OAuth

---

## Branch

`claude/add-firebase-cloud-saving-TGXG7` on `jayoocrxssd-coder/html-starter`
