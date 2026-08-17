// Login page — the only page a logged-out user should be able to reach.
//
// WHAT TO DO:
// 1. Mark this file with "use client" at the very top (it needs
//    useState and browser interactivity, which server components can't
//    do — look up the difference between server and client components
//    in the App Router if that's new).
// 2. Import { auth } from "@/lib/firebase-client" (once you've built it).
// 3. Build a simple form: email + password inputs, a submit button.
// 4. On submit, call Firebase's signInWithEmailAndPassword(auth, email,
//    password) — or createUserWithEmailAndPassword for a signup flow.
//    Decide if you want one page that does both, or two separate ones.
// 5. On success, redirect to the dashboard (look up useRouter from
//    "next/navigation").
// 6. On failure, show the error message back to the user.
//
// THE PART THAT CONNECTS TO YOUR BACKEND:
// After login, Firebase gives you a user object with a method
// `getIdToken()`. Every fetch() call to your /api/* routes from now on
// needs to include that token as:
//   headers: { Authorization: `Bearer ${token}` }
// Without this header, your API routes' getUidFromRequest() will always
// return null. This is the single most common thing to forget.
