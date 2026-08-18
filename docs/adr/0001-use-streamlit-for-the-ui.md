# 0001. Use Streamlit for the UI

**Status:** Accepted

## Context

This app needed a small, working web UI (login screen + a Kanban-style
board of job applications) built quickly, by someone comfortable in
Python but not looking to write and maintain a separate JavaScript
frontend, HTML/CSS, a build pipeline, or a REST API layer between a
frontend and backend.

## Decision

Build the entire UI in [Streamlit](https://streamlit.io) — a Python
library where you write one script
([`app.py`](../modules/app.py.md)) that both defines the page layout
*and* handles user interaction, using plain Python function calls
(`st.text_input(...)`, `st.button(...)`, `st.columns(...)`, etc.).
Streamlit runs that script as a server process and streams the rendered
UI to the browser.

## Consequences

- No separate frontend project, no build step, no REST API to design —
  the entire app is one Python process.
- In exchange, the UI is constrained to whatever Streamlit's built-in
  components support. There's no way to write custom JavaScript that
  runs in the user's browser — which directly caused
  [ADR 0002](0002-auth-via-rest-api-not-web-sdk.md) (can't use Firebase's
  normal browser-side login flow).
- Streamlit keeps each browser tab's state (`st.session_state`) in the
  memory of the server process that's currently serving it, and pushes
  updates over a persistent WebSocket connection rather than normal
  page loads. This shaped two later, non-obvious hosting decisions:
  [ADR 0004](0004-cloud-run-direct-not-firebase-hosting.md) (Firebase
  Hosting breaks that WebSocket) and
  [ADR 0005](0005-cloud-run-session-affinity.md) (Cloud Run must keep
  routing a session to the same server process).
- Every user interaction re-runs the *entire* Python script from top to
  bottom (Streamlit's execution model). This is simple to reason about
  but means expensive operations (like a Firestore read) run again on
  every single click unless deliberately avoided — worth keeping in mind
  if this app's data grows large enough for that to matter.
