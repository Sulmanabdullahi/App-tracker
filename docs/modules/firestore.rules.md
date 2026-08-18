# `firestore.rules`

```
rules_version = '2';

service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

Firestore's **Security Rules** — a separate mini-language (not regular
code) that Firestore itself evaluates on every request that comes from a
*direct client* (e.g. browser-side JavaScript using the Firebase Web
SDK, or a mobile app). This file's rule is about as simple as it gets:
`match /{document=**}` matches every document in every collection, and
`allow read, write: if false;` unconditionally denies every operation on
all of them.

## Why deny everything?

Because this app's browser **never talks to Firestore directly** — every
read and write goes through the Streamlit server, which uses the
**Admin SDK** in [`firestore_db.py`](firestore_db.py.md). The Admin SDK
runs with full administrative trust and **completely bypasses these
rules** — they don't apply to it at all.

So this file isn't the thing enforcing "user X can only see their own
applications" (that happens in the manual `uid` checks inside
`firestore_db.py` — see
[ADR 0003](../adr/0003-admin-sdk-server-side-with-deny-all-rules.md) for
the full reasoning). Instead, it's a deliberate backstop: if anyone ever
misconfigured a client-side Firebase SDK to point at this project (by
accident, or by copy-pasting this app's Firebase config into an
unrelated client-side project), they'd be flatly denied rather than
accidentally exposing the raw database.

## When would you ever change this file?

Only if the app's architecture changes to have the browser talk to
Firestore directly (which would be a significant redesign away from
Streamlit's server-side model — see
[ADR 0001](../adr/0001-use-streamlit-for-the-ui.md)). Until then, this
file should stay exactly as restrictive as it is.
