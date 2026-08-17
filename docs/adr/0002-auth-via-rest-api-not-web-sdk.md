# 0002. Sign in via the Firebase Auth REST API, not the Web SDK

**Status:** Accepted

## Context

The standard way to add login to a web app with Firebase is the
**Firebase Web SDK** — a JavaScript library that runs in the user's
browser, handles the sign-in UI/flow, and talks to Firebase directly
from there.

This app is built in [Streamlit](0001-use-streamlit-for-the-ui.md),
which renders Python into a web page but gives the developer no way to
inject and run custom JavaScript that talks back to the Python session.
There is no supported way to run the Firebase Web SDK from inside a
Streamlit app.

## Decision

Implement sign-up/login by calling the **Identity Toolkit REST API**
(`identitytoolkit.googleapis.com`) directly over HTTPS, *from the
Python server*, in [`firebase_auth.py`](../modules/firebase_auth.py.md).
The user's email and password are submitted through a normal Streamlit
form, sent server-side to that REST endpoint, and the resulting **ID
token** is re-verified using the Firebase Admin SDK
(`admin_auth.verify_id_token`) before the app trusts the `uid` inside
it.

## Consequences

- Works from any backend language — this isn't Streamlit-specific,
  it's how you'd do server-side Firebase Auth from any Python/Ruby/Go/etc.
  backend that isn't the browser.
- Requires a **Firebase Web API key** (`FIREBASE_API_KEY`), which
  identifies the request as belonging to this Firebase project. This
  key is not a secret that grants access on its own (it's visible in any
  browser's network tab in a normal Firebase web app), but the app still
  keeps it in an environment variable for cleanliness — see
  [`modules/env-files.md`](../modules/env-files.md).
- The user's password is submitted to Google's REST endpoint from *our*
  server rather than directly from their browser. It's still sent over
  HTTPS and never stored, but it does mean our server process briefly
  handles the plaintext password in memory during the request — a normal
  characteristic of any server-mediated password login, but worth being
  aware of.
- No "Sign in with Google" / social login buttons — those specifically
  rely on browser redirects and JS that this architecture can't run.
  Only email/password is supported. Adding social login later would
  require a fundamentally different approach (e.g. a thin JS/HTML login
  page hosted separately, outside Streamlit).
- We do **not** blindly trust the `uid` the REST API's response claims —
  see the re-verification step in
  [`firebase_auth.py`](../modules/firebase_auth.py.md). This closes the
  gap where a malformed or tampered response could otherwise be trusted.
