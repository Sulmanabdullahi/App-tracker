# SOP: Add or remove a Kanban status column

Example: adding a "Ghosted" column between Interview and Offer, or
removing "OA" entirely.

## Adding a new status

Two places need to change together:

1. **[`firestore_db.py`](../modules/firestore_db.py.md)** — add the new
   value to `STATUSES`, in the position you want it to appear (the list
   order *is* the column order):
   ```python
   STATUSES = ["applied", "oa", "interview", "ghosted", "offer", "rejected"]
   ```

2. **[`app.py`](../modules/app.py.md)** — add a matching entry to
   `STATUS_META` with a label and icon:
   ```python
   STATUS_META = {
       ...
       "ghosted": {"label": "Ghosted", "icon": "👻"},
       ...
   }
   ```

That's it — no database migration needed. Existing applications keep
whatever status they already have; only *new* status transitions can use
the new value (via the dropdown on each card).

**Do not skip step 2.** If a status exists in `STATUSES` but not in
`STATUS_META`, `app.py` will raise a `KeyError` the moment it tries to
render that column's header or format that value in a dropdown.

## Removing a status

More care is needed here, because existing documents may already have
the status you're removing.

1. Decide what happens to applications currently in that status. Either:
   - Manually move them to another status first (open the app, use the
     dropdown on each one), or
   - Write a one-off migration script using
     [`firestore_db.py`](../modules/firestore_db.py.md)'s
     `update_status` for every affected document.
2. Remove the entry from `STATUSES` in `firestore_db.py` and from
   `STATUS_META` in `app.py`.
3. If any documents were missed in step 1, they'll still have the old
   status string stored, but `app.py`'s `STATUS_META[s]` lookup for that
   value will now `KeyError` when the board tries to render it — so
   don't skip step 1.

## After either change

Follow [`deploy-a-change.md`](deploy-a-change.md) to ship it. No
Firestore rules or index changes are needed for this kind of change —
`status` is stored as a plain string field either way.
