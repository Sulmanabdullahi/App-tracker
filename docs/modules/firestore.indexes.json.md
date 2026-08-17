# `firestore.indexes.json`

```json
{
  "indexes": [
    {
      "collectionGroup": "applications",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "uid", "order": "ASCENDING" },
        { "fieldPath": "created_at", "order": "DESCENDING" }
      ]
    }
  ],
  "fieldOverrides": []
}
```

## What a composite index is, and why this one exists

Firestore can filter or sort by a single field automatically, with no
setup. But [`firestore_db.list_applications`](firestore_db.py.md) does
**both at once** — it filters by `uid` (only this user's documents) and
sorts by `created_at` (newest first):

```python
.where(filter=FieldFilter("uid", "==", uid))
.order_by("created_at", direction=Query.DESCENDING)
```

Combining a filter on one field with sorting on a *different* field
requires Firestore to have a pre-built **composite index** describing
exactly that combination — it's how Firestore keeps that specific query
fast even as the collection grows to millions of documents, rather than
scanning and sorting every document on every request.

This file declares that index (`uid` ascending, `created_at`
descending) so it's created automatically whenever
`firebase deploy --only firestore` runs, instead of relying on someone
clicking through the Firebase console by hand.

## What happens if this index is ever missing

`list_applications` in `firestore_db.py` specifically catches this case
(`FailedPrecondition`) and raises a clear error explaining that the
index needs to be created — rather than letting a cryptic Google Cloud
exception surface to the user. See
[`firestore_db.py.md`](firestore_db.py.md).

## When would you add another index here?

Any time a new query is added elsewhere in the app that filters by one
field and sorts/filters by another (or filters by two different fields
with certain operators) — Firestore will refuse the query and (in local
development) usually gives you a direct console link to create the
needed index with one click, which is also a valid way to discover the
exact `fields` block to copy into this file.
