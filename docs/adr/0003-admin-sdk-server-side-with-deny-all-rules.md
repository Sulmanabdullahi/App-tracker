# 0003. Access Firestore only through the server-side Admin SDK; deny all direct client access

**Status:** Accepted

## Context

The typical Firestore-backed web app has the *browser* talk to Firestore
directly, using a client-side SDK, and relies on **Firestore Security
Rules** as the enforcement mechanism for "user X can only see/edit their
own data."

This app's browser never talks to Firebase directly at all — every
interaction goes through the Streamlit server first (see
[`architecture.md`](../architecture.md)). So the normal client-side
Firestore access pattern doesn't apply here.

## Decision

- All Firestore reads/writes happen in
  [`firestore_db.py`](../modules/firestore_db.py.md), using the
  **Firebase Admin SDK**, which runs with full, unrestricted access and
  bypasses Firestore Security Rules entirely (that's what "Admin" means
  — it's designed for trusted server environments, never for browsers).
- Every function in `firestore_db.py` takes the caller's `uid` as an
  argument and manually filters or checks against it — e.g.
  `list_applications` filters `where uid == <uid>`, and
  `update_status`/`delete_application` both check
  `data.get("uid") != uid` before proceeding.
- [`firestore.rules`](../modules/firestore.rules.md) is set to deny
  *all* reads and writes, unconditionally (`allow read, write: if
  false`).

## Consequences

- **The real access-control boundary for this app is the Python code in
  `firestore_db.py`, not the security rules.** The rules are a backstop
  — if anyone ever managed to point a client-side Firestore SDK at this
  project directly, they'd be flatly denied. But they do nothing to stop
  a bug in `firestore_db.py` itself.
- This means **every new function added to `firestore_db.py` must
  remember to check the `uid` manually.** There's no rules engine
  catching a mistake here — forgetting that check in a new function
  would be a real, exploitable vulnerability (one user reading or
  editing another user's applications), and nothing in Firestore itself
  would stop it.
- Because the Admin SDK doesn't need per-request user credentials, the
  app doesn't need to pass the user's ID token down to Firestore calls
  at all — it authenticates as the *service account* Cloud Run attaches
  to the container (or, locally, whatever
  `GOOGLE_APPLICATION_CREDENTIALS` points at). See
  [`modules/env-files.md`](../modules/env-files.md).
