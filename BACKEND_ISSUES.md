# WAR ROOM — Backend Issues (Cannot Fix in Frontend)

This document lists issues that require backend configuration, external service setup,
or server-side changes that cannot be resolved by editing the HTML/JS bundle alone.

---

## 1. Firebase Configuration (Hard-coded credentials)

**Severity: HIGH — Security Risk**

The Firebase project credentials are hard-coded directly in the bundle:

```
apiKey:            "AIzaSyBcdKlkPBlLxs6barPZDAgoPlB9iU82Zkg"
authDomain:        "createwarrom.firebaseapp.com"
projectId:         "createwarrom"
storageBucket:     "createwarrom.firebasestorage.app"
messagingSenderId: "394212942606"
appId:             "1:394212942606:web:99b7bb6e3d46c840f12d5f"
measurementId:     "G-HDE0905K1P"
```

**What you need to do:**
- In the Firebase Console (`console.firebase.google.com`), restrict the `apiKey` to your
  specific domain(s) under **API restrictions** in Google Cloud Console.
- Set **Authorized domains** in Firebase Auth → Settings → Authorized domains.
- Enable **App Check** to prevent API key abuse.
- Set proper **Firestore Security Rules** — the current app uses `setDoc`, `getDoc`,
  `updateDoc`, `getDocs`, and `collection` (10+ usages) which will fail unless rules
  allow reads/writes for the authenticated user.

**Firestore functions used in code:**
`setDoc`, `updateDoc`, `getDoc`, `getDocs`, `collection`, `doc`, `signOut`,
`onAuthStateChanged`, `signInWithPopup` (via Google Auth)

---

## 2. Google OAuth / Firebase Authentication

**Severity: HIGH — Sign-in will not work without this**

The app uses `signInWithPopup` with `GoogleAuthProvider` for Google Sign-In.
Firebase Authentication must be enabled and configured in the Firebase Console.

**What you need to do:**
- In Firebase Console → Authentication → Sign-in method → enable **Google**.
- Add the deployed domain to **Authorized domains** (Firebase Auth settings).
- If running locally (`file://`), sign-in popups will be blocked — deploy to a real
  domain (Firebase Hosting, Vercel, Netlify, etc.).

---

## 3. Google Drive Backup Integration

**Severity: MEDIUM — Backup/restore feature will not work**

The app has Google Drive backup functionality (`driveSave`, `driveLoad`) using the
Google Drive API via `gapi`. The OAuth client ID is hard-coded:

```
DRIVE_CLIENT_ID  = '190616282170-hkcq273fdvm3740p6h222u6pohlbjdih.apps.googleusercontent.com'
DRIVE_FOLDER_NAME = 'WarRoom Backups'
```

**What you need to do:**
- In Google Cloud Console, ensure the OAuth 2.0 client has the correct
  **Authorized JavaScript origins** (must match your deployed domain).
- The `gapi.load` call requires the Google Identity Services library to load
  from `https://apis.google.com/js/api.js` — this will be blocked in offline/
  local file environments.
- The app targets a folder named `'WarRoom Backups'` in the user's Drive;
  Drive API v3 must be enabled in the Cloud Console for the project.

---

## 4. Supabase (Referenced but not fully implemented)

**Severity: LOW — Currently placeholder/unused**

The code comments reference Supabase as "background-only cloud sync" and there is
a stub `initSupabase()` function, but no Supabase URL or API key is configured.
Supabase is mentioned as a replacement/alternative to Firebase but the credentials
are never set.

**What you need to do (if you want Supabase sync):**
- Create a project at `supabase.com`.
- Add your `SUPABASE_URL` and `SUPABASE_ANON_KEY` to the bundle.
- Implement `initSupabase()` with `createClient(url, key)` from the Supabase JS SDK.
- Define the schema tables in Supabase (businesses, goals, entries, etc.).
- Wire up Row Level Security (RLS) policies to restrict data to authenticated users.

---

## 5. Firebase Firestore Security Rules

**Severity: HIGH — Data is either locked or open to everyone**

Without explicit Firestore Security Rules, all reads/writes will be denied by default
(or open to all if the project was created with test mode). The app expects to
read and write user-specific documents.

**Recommended rules (starting point):**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

---

## 6. Firebase Storage Rules (Profile photo uploads)

**Severity: MEDIUM — Profile photo upload will fail**

The app references Firebase Storage (`uploadBytes`, `getDownloadURL`, `deleteObject`)
for profile photo management. Default storage rules deny all access.

**Recommended rules:**
```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /users/{userId}/profile/{allPaths=**} {
      allow read: if true;
      allow write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

---

## 7. AI Briefing Feature

**Severity: MEDIUM — AI feature requires API key**

The app has an "AI Briefing" panel in the dashboard. Based on the UI structure,
this likely calls an AI API (OpenAI or similar). No API key is configured in the
frontend bundle.

**What you need to do:**
- If this calls an AI API directly from the client, add your API key (not recommended
  for production — exposes key to users).
- Preferred: create a server-side proxy endpoint (Cloud Function, Edge Function, etc.)
  that your app calls, which then calls the AI API with a server-stored key.

---

## 8. Invite / Referral System

**Severity: LOW — Feature incomplete**

The app calls `checkInviteParam()` on startup to check URL query parameters for
invite codes. The function is defined in the frontend, but invite code *validation*
and *attribution* require a backend:

- Invite codes need to be stored and validated server-side.
- The referral attribution (linking invited user to referrer) needs a database write.
- Currently the frontend only reads the URL param; no backend endpoint exists.

---

## 9. Seat/Team Limit Enforcement

**Severity: LOW — Client-only enforcement is bypassable**

The workspace seat limit ("3 seats used") is currently enforced only in client-side
JavaScript. Any user can bypass it by editing localStorage. For a real multi-user
workspace, seat limits must be enforced server-side (Firestore rules + Cloud
Functions or equivalent).

---

## Summary Table

| Issue | Severity | Service | Estimated Effort |
|-------|----------|---------|-----------------|
| Firebase credentials should be restricted | HIGH | Firebase / GCP | 30 min |
| Google OAuth authorized domains | HIGH | Firebase Auth | 15 min |
| Firestore Security Rules | HIGH | Firebase | 1-2 hrs |
| Firebase Storage Rules | MEDIUM | Firebase | 30 min |
| Google Drive OAuth origins | MEDIUM | Google Cloud | 30 min |
| AI Briefing API key / proxy | MEDIUM | OpenAI / custom | 2-4 hrs |
| Supabase integration | LOW | Supabase | 4-8 hrs |
| Invite system backend | LOW | Custom | 4-8 hrs |
| Server-side seat enforcement | LOW | Firebase / custom | 2-4 hrs |
