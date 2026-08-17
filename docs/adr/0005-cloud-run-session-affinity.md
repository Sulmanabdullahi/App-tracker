# 0005. Always deploy with Cloud Run session affinity enabled

**Status:** Accepted

## Context

Cloud Run can run multiple instances (copies) of a container at once,
scaling up under load and back down when idle, and by default it
balances incoming requests across whichever instances are running with
no guarantee that two requests from the same browser land on the same
one.

[Streamlit](0001-use-streamlit-for-the-ui.md) keeps a signed-in user's
session — who they are, what's currently in an open form, etc. — in
`st.session_state`, which lives entirely in the memory of *one specific*
server process. Streamlit's frontend also periodically reconnects its
WebSocket connection to the server.

Before this was fixed, users experienced the app appearing to load
forever / repeatedly reset: each WebSocket reconnect had a real chance
of landing on a *different* Cloud Run instance than the one holding that
user's session, which had no memory of them at all.

## Decision

Deploy (and redeploy) the `app-tracker` Cloud Run service with the
`--session-affinity` flag:

```bash
gcloud run deploy app-tracker \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --session-affinity \
  --set-env-vars FIREBASE_PROJECT_ID=...,FIREBASE_API_KEY=...
```

This makes Cloud Run set a cookie (`GAESA`) on first response and keep
routing that browser to the same instance for the rest of its session.

## Consequences

- **This flag must be included on every future deploy or service
  update.** It's a per-revision setting, not a one-time project setting
  — a redeploy that omits it silently regresses back into the "stuck
  loading" symptom. If that symptom reappears, check this first (see
  [`sops/troubleshoot-blank-loading-screen.md`](../sops/troubleshoot-blank-loading-screen.md)).
- This was a *necessary but not sufficient* fix on its own — the app
  also had to stop being served through Firebase Hosting, which broke
  the WebSocket handshake entirely regardless of session affinity (see
  [ADR 0004](0004-cloud-run-direct-not-firebase-hosting.md)). Both
  changes were required together.
- Session affinity trades away perfectly even load balancing across
  instances, in exchange for correctness. At this app's scale (a small
  personal/internal tool), that trade-off is a non-issue.
- If this app ever needs to run many concurrent users at real scale, the
  underlying design choice worth revisiting is Streamlit's in-memory
  session model itself (e.g. moving session state into Firestore or
  another shared store) rather than continuing to rely on sticky
  routing.
