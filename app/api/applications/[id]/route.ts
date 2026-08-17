// REST endpoint: /api/applications/:id
// Handles reading, updating, and deleting ONE specific application.
// The [id] folder name is how Next.js captures that part of the URL —
// it shows up as params.id in each function below.

// ---------- GET /api/applications/:id ----------
// WHAT TO DO:
// 1. Auth check (same pattern as the other route).
// 2. SELECT the one row WHERE id = params.id AND firebase_uid = <uid>.
//    Both conditions matter: the second one stops User A from reading
//    User B's application just by guessing its id.
// 3. If no row comes back, return 404. Otherwise return the row.

// ---------- PATCH /api/applications/:id ----------
// This is the most involved one — it's what runs every time you drag a
// card to a new column, or edit any field.
// WHAT TO DO:
// 1. Auth check.
// 2. Parse the body — it may contain any subset of the editable fields
//    (company, role, status, notes, etc.). Figure out which fields were
//    actually sent (don't assume all of them).
// 3. Build an UPDATE query that only touches the fields that were sent.
//    Look up how people build "dynamic SET clauses" safely with
//    parameterized queries — this is a common real-world pattern.
// 4. Also update last_update to today's date and updated_at to now() as
//    part of the same UPDATE.
// 5. Filter WHERE id = params.id AND firebase_uid = <uid>, same reasoning
//    as GET.
// 6. IMPORTANT: if "status" was one of the fields being changed, insert a
//    new row into status_history with the new status. This is the piece
//    that keeps the history table accurate — if you forget it here, your
//    Python stats will quietly go stale.
// 7. Return the updated row, or 404 if nothing matched.

// ---------- DELETE /api/applications/:id ----------
// WHAT TO DO:
// 1. Auth check.
// 2. DELETE WHERE id = params.id AND firebase_uid = <uid>.
// 3. Return whether anything was actually deleted (404 if not).
// Note: because status_history has application_id referencing this
// table, decide (back in your schema) whether deleting an application
// should also delete its history rows automatically (ON DELETE CASCADE)
// or block the delete. Either is defensible — just be deliberate.
