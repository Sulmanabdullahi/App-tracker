// REST endpoint: /api/stats
// This route does NO math. It only reads whatever the Python script most
// recently wrote into the "stats" table. Keep it that way — recomputing
// stats live inside a web request is a different (heavier) design choice
// you're deliberately avoiding for now.

// ---------- GET /api/stats ----------
// WHAT TO DO:
// 1. Auth check, same pattern as the other routes.
// 2. SELECT * FROM stats WHERE firebase_uid = <uid> — remember this table
//    has firebase_uid as its PRIMARY KEY, so you'll get at most one row.
// 3. If no row exists yet (user hasn't run the Python script), return a
//    404 or an empty/placeholder response — decide what the frontend
//    should show in that case (e.g. "no stats yet, run the analysis").
// 4. Otherwise return that row as JSON.
