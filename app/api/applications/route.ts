// REST endpoint: /api/applications
// Handles two things: listing all of a user's applications, and creating
// a new one. In Next.js's App Router, each exported function name
// (GET, POST, etc.) maps to that HTTP method automatically.

// ---------- GET /api/applications ----------
// WHAT TO DO:
// 1. Call getUidFromRequest(req) from lib/firebase-admin — if it returns
//    null, respond with a 401 status and stop.
// 2. Read the URL's query string for an optional ?status= filter
//    (look up `new URL(req.url).searchParams`)
// 3. Run a SELECT against the applications table:
//      - always filter WHERE firebase_uid = <uid>
//      - if a status filter was given, also filter WHERE status = <it>
//      - use PARAMETERIZED queries ($1, $2, ...) — never paste the uid or
//        status directly into the SQL string. Look up "SQL injection" if
//        you're unsure why this matters.
// 4. Return the rows as JSON.
//
// ---------- POST /api/applications ----------
// WHAT TO DO:
// 1. Same auth check as above.
// 2. Parse the request body (await req.json()) to get company, role, and
//    the other optional fields.
// 3. Validate: company and role must be present — return 400 if not.
// 4. INSERT a new row into applications, using the uid from step 1 (never
//    trust a firebase_uid sent in the request body — always use the one
//    you verified from the token).
// 5. Also INSERT a row into status_history with this new application's id
//    and its starting status. Think about why: without this, the very
//    first "applied" event would never be logged, and the Python script's
//    time-to-respond math would be missing a data point for every app.
// 6. Return the newly created row with a 201 status.
