# SOP: Delete a user and their data

The app has no self-service "delete my account" or admin panel — this is
a manual, two-part cleanup: the Firebase **Authentication** account, and
their documents in **Firestore**. Do both; deleting only the auth
account leaves orphaned application data behind (harmless, but untidy
and technically still someone's job-search history sitting in the
database).

## Option A: via the Firebase Console (easiest, for one-off cleanup)

1. **Auth**: console.firebase.google.com → your project → **Build >
   Authentication > Users** tab → find the user by email → the ⋮ menu →
   **Delete account**. Note the **User UID** shown in that row before
   deleting it — you need it for step 2.
2. **Firestore data**: console.firebase.google.com → **Build > Firestore
   Database > Data** tab → open the `applications` collection → for each
   document, check its `uid` field against the UID you noted, and delete
   the matching ones (⋮ menu on the document → **Delete document**).
   There's no bulk "delete where uid = X" button in the console for a
   handful of documents; for a lot of documents, use Option B instead.

## Option B: via the command line (faster for scripting, or many documents)

Requires `gcloud` authenticated as a project owner/editor (see
[`deploy-a-change.md`](deploy-a-change.md) prerequisites).

1. **Find the user's UID:**
   ```bash
   firebase auth:export /tmp/users.json --project <project-id>
   python3 -c "
   import json
   for u in json.load(open('/tmp/users.json'))['users']:
       print(u.get('localId'), u.get('email'))
   "
   ```

2. **Delete the Auth account** (the Firebase CLI has no direct
   delete-user command, so this uses the Identity Toolkit REST API
   directly, authenticated with your own `gcloud` credentials):
   ```bash
   TOKEN=$(gcloud auth print-access-token)
   curl -s -X POST \
     "https://identitytoolkit.googleapis.com/v1/projects/<project-id>/accounts:delete" \
     -H "Authorization: Bearer $TOKEN" \
     -H "x-goog-user-project: <project-id>" \
     -H "Content-Type: application/json" \
     -d '{"localId": "<uid>"}'
   ```
   A `{"kind": "identitytoolkit#DeleteAccountResponse"}` response means
   success.

3. **Find their Firestore documents:**
   ```bash
   TOKEN=$(gcloud auth print-access-token)
   curl -s -X POST \
     "https://firestore.googleapis.com/v1/projects/<project-id>/databases/(default)/documents:runQuery" \
     -H "Authorization: Bearer $TOKEN" \
     -H "x-goog-user-project: <project-id>" \
     -H "Content-Type: application/json" \
     -d '{
       "structuredQuery": {
         "from": [{"collectionId": "applications"}],
         "where": {"fieldFilter": {"field": {"fieldPath": "uid"}, "op": "EQUAL", "value": {"stringValue": "<uid>"}}}
       }
     }'
   ```
   Note each returned document's full `name` (a path ending in
   `/applications/<doc-id>`).

4. **Delete each document:**
   ```bash
   curl -s -X DELETE \
     "https://firestore.googleapis.com/v1/projects/<project-id>/databases/(default)/documents/applications/<doc-id>" \
     -H "Authorization: Bearer $TOKEN" \
     -H "x-goog-user-project: <project-id>"
   ```

## Why the REST API, not `firestore_db.py`?

[`firestore_db.py`](../modules/firestore_db.py.md)'s
`delete_application(uid, application_id)` requires knowing the specific
document ID and is meant to be called *by the app, as that user* — it's
not a standalone admin tool. Doing this cleanup as a project
owner/editor via `gcloud`'s credentials and the raw REST APIs is the
practical option for someone outside the app itself, without writing and
running a one-off Python script that imports the Admin SDK.
