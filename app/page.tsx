// Dashboard — the main page, shown after login. This is where the
// Kanban-style board lives (Applied / OA / Interview / Offer-Rejected).
//
// WHAT TO DO:
// 1. "use client" at the top — this page needs state and effects.
// 2. On load (useEffect), check if a user is logged in (Firebase's
//    onAuthStateChanged, from lib/firebase-client). If not, redirect to
//    /login.
// 3. Once you have a logged-in user, get their ID token and fetch
//    GET /api/applications with the Authorization header.
// 4. Store the results in state (useState).
// 5. Group the applications by their `status` field into four buckets
//    matching your pipeline stages — this is pure JavaScript array
//    filtering, no new API call needed for this part.
// 6. Render one column per status, and render <ApplicationCard /> for
//    each application inside its column (component described below).
// 7. Also fetch GET /api/stats and render a small stats summary
//    somewhere on the page (see StatsPanel component below).
// 8. Include a button/form to add a new application — this can open
//    <ApplicationForm /> (see below) or link to a separate page, your
//    call.
//
// STATE-MANAGEMENT QUESTION TO THINK ABOUT:
// When a user changes an application's status, do you re-fetch the
// whole list from the server, or update it optimistically in local
// state and only fall back to a re-fetch if the API call fails? Both
// are legitimate — decide and be able to explain why.
