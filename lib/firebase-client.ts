// This file initializes Firebase for use IN THE BROWSER (not the server —
// that's lib/firebase-admin.ts).
//
// WHAT TO DO:
// 1. `npm install firebase` (already in package.json)
// 2. Import { initializeApp } from "firebase/app" and { getAuth } from
//    "firebase/auth"
// 3. Build a config object from the NEXT_PUBLIC_FIREBASE_* env vars
//    (see .env.example — these ARE safe to expose to the browser, unlike
//    the FIREBASE_PRIVATE_KEY used on the server. The NEXT_PUBLIC_ prefix
//    is what tells Next.js to actually bundle them into client code —
//    look up why that prefix matters.)
// 4. Call initializeApp(config) and export the result of getAuth(app) as
//    something like `export const auth = ...`
//
// WHY: every login/signup UI component will import { auth } from this
// file and call functions like signInWithEmailAndPassword(auth, ...) or
// createUserWithEmailAndPassword(auth, ...) on it.
//
// Docs: https://firebase.google.com/docs/auth/web/start
