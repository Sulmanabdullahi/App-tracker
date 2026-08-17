// Small panel showing the numbers the Python script computed:
// response rate, average days to response, and a "needs follow-up" list.
//
// WHAT TO DO:
// 1. Accept the stats object as a prop (fetched by the dashboard page
//    from GET /api/stats).
// 2. Handle the "no stats yet" case gracefully — if the user hasn't run
//    the Python script yet, show a friendly message instead of crashing
//    on undefined fields.
// 3. Render total_applications, response_rate, avg_days_to_response as
//    simple stat blocks.
// 4. Render needs_followup as a short list — remember this field comes
//    back as JSON from the database, so make sure you're working with a
//    parsed array, not a raw JSON string, by the time it gets here.
//
// THIS COMPONENT NEVER COMPUTES ANYTHING ITSELF. If a number looks wrong,
// the bug is in python/analyze.py, not here — keep that boundary clean.
