// This file runs on the SERVER ONLY. Its job: given an incoming request,
// figure out WHO sent it, by checking the Firebase login token they attach.
//
// WHAT TO DO:
// 1. `npm install firebase-admin` (already in package.json)
// 2. Import { initializeApp, getApps, cert } from "firebase-admin/app"
//    and { getAuth } from "firebase-admin/auth"
// 3. Initialize the admin app ONCE using a service account (project id,
//    client email, private key — see .env.example for where these come
//    from). Guard against re-initializing on every hot reload by checking
//    `getApps().length` first.
// 4. Write a function, e.g. `getUidFromRequest(req)`, that:
//      a. Reads the "Authorization" header off the request
//      b. Expects it to look like "Bearer <token>" — split out the token
//      c. Calls `getAuth().verifyIdToken(token)` to check it's valid
//      d. Returns the `uid` field from the decoded token, or null/throws
//         if the header is missing or the token is invalid
//
// WHY THIS MATTERS:
// This is your entire access-control system. Every API route will call
// this function FIRST, before touching the database, so it knows whose
// data to query. If this function has a bug, that's a real security hole
// — take your time here.
//
// WHERE THE TOKEN COMES FROM: the browser gets it after calling Firebase
// Auth's sign-in functions, then must attach it to every fetch() call to
// your API routes as an Authorization header. That's built in the
// frontend, not here — but it's worth understanding the round trip.
//
// Docs: https://firebase.google.com/docs/auth/admin/verify-id-tokens
