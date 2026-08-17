# `firestore_db.py`

All reads and writes to Firestore live here. This is the *only* file
that imports `firebase_admin.firestore` — [`app.py`](app.py.md) never
talks to the database directly, it only calls functions in this file.

Read [ADR 0003](../adr/0003-admin-sdk-server-side-with-deny-all-rules.md)
first — it explains the most important thing about this file: because
it uses the Admin SDK (full, unrestricted access), **the manual `uid`
checks inside these functions are the actual security boundary**, not
Firestore's rules. Every function here that touches a specific document
must check it belongs to the calling user.

## Walkthrough

### `STATUSES` (line 15)

```python
STATUSES = ["applied", "oa", "interview", "offer", "rejected"]
```

The single source of truth for which status values are valid, and what
order they display in on the Kanban board. [`app.py`](app.py.md)'s
`STATUS_META` dictionary must have an entry for every value in this
list (see [`sops/add-or-remove-a-status-column.md`](../sops/add-or-remove-a-status-column.md)
for adding a new one).

### `client()` (lines 20–28)

```python
_db = None

def client():
    global _db
    if _db is None:
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        _db = firestore.client()
    return _db
```

Returns a Firestore client, creating it once and reusing it afterward
(the `global _db` / `if _db is None` pattern — a simple form of
memoization/lazy-singleton). The `if not firebase_admin._apps:` check is
a safety net: normally [`app.py`](app.py.md) calls
`firebase_admin.initialize_app()` before this module is even imported,
but if some other code path ever imports `firestore_db` first, this
makes sure the Admin SDK still gets initialized rather than crashing.

### `list_applications(uid)` (lines 31–56)

Fetches every application belonging to one user, newest first:

```python
.where(filter=FieldFilter("uid", "==", uid))
.order_by("created_at", direction=Query.DESCENDING)
```

Filtering by one field (`uid`) *and* sorting by a different field
(`created_at`) is exactly the kind of query that requires a **composite
index** in Firestore — see
[`firestore.indexes.json.md`](firestore.indexes.json.md). If that index
doesn't exist, Firestore raises `FailedPrecondition`; this function
catches that specific error and re-raises a much clearer `RuntimeError`
explaining exactly what's missing and how to fix it, instead of letting
a cryptic Google Cloud exception reach the user.

```python
for doc in docs:
    item = doc.to_dict()
    if item is None:
        continue  # doc exists but has no fields — skip it
```

`doc.to_dict()` can return `None` for a document that technically exists
in Firestore but has no fields (an edge case that can happen from manual
console edits or certain write patterns) — this guards against crashing
on `item["id"] = doc.id` a line later if that happens.

Each result dict gets its own `id` field added (`doc.id`, the Firestore
document ID) — this is what `app.py` uses as the `key=` for Streamlit
widgets (e.g. `key=f"status_{app_['id']}"`) and what
`update_status`/`delete_application` take as `application_id`.

### `add_application(uid, company, role, notes)` (lines 59–72)

Creates a new document in the `applications` collection. Every new
application starts life with `status: "applied"` — there's no way to
add an application directly into a later stage; the UI enforces this by
only exposing an "Add application" form with no status picker. Both
`created_at` and `updated_at` are set to the same timestamp on creation.

### `update_status(uid, application_id, status)` (lines 75–83)

```python
if status not in STATUSES:
    raise ValueError(f"Unknown status: {status}")
doc_ref = client().collection("applications").document(application_id)
doc = doc_ref.get()
data = doc.to_dict()
if not doc.exists or data is None or data.get("uid") != uid:
    raise PermissionError("Application not found for this user")
doc_ref.update({"status": status, "updated_at": ...})
```

This is the pattern every mutating function in this file follows, and
the one to copy if you add a new one: **fetch the document first, check
it exists AND belongs to the calling `uid`, only then act on it.**
Raising `PermissionError` rather than silently doing nothing means a bug
that tries to touch someone else's data fails loudly instead of quietly
succeeding-but-doing-nothing.

### `delete_application(uid, application_id)` (lines 86–92)

Same ownership-check pattern as `update_status`, then
`doc_ref.delete()`. There is no "undo" — this is a hard delete. The UI
guards against accidental clicks with a confirmation popover (see
[`app.py.md`](app.py.md)), but this function itself has no safety net —
anything calling it deletes immediately.
