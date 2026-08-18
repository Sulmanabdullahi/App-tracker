# 0004. Serve directly from the Cloud Run URL, not behind Firebase Hosting

**Status:** Accepted

## Context

The app runs as a container on Cloud Run (see
[`Dockerfile`](../modules/Dockerfile.md)). The obvious way to give it a
clean, Firebase-branded URL (`your-project.web.app`) instead of a long
Cloud Run one is to put **Firebase Hosting** in front of it, using a
`rewrite` rule that proxies all traffic to the Cloud Run service. This
is a commonly documented pattern and is what this project originally
did.

After deploying that way, the app loaded its outer page shell in a
browser but never rendered any actual content — it stayed on an empty
loading skeleton indefinitely, described by the user as "firebase
connection is not working."

**Investigation:** driving both URLs with a real headless browser
(Playwright) and inspecting the browser console showed the actual cause:

```
WebSocket connection to 'wss://<project>.web.app/_stcore/stream' failed:
Error during WebSocket handshake: Unexpected response code: 200
```

[Streamlit](0001-use-streamlit-for-the-ui.md) requires a persistent
WebSocket connection (at `/_stcore/stream`) to push any UI content to
the browser after the initial page load. Firebase Hosting's rewrite
proxy to Cloud Run does not forward the WebSocket upgrade handshake — the
server responds with a plain `200 OK` instead of the `101 Switching
Protocols` a successful WebSocket upgrade requires. The same URL, hit
*directly* at its Cloud Run address (bypassing Firebase Hosting
entirely), rendered correctly with zero console errors.

This matches externally reported instances of the same limitation:
[nicegui#3563](https://github.com/zauberzeug/nicegui/discussions/3563)
and [streamlit#10341](https://github.com/streamlit/streamlit/issues/10341).

## Decision

- Removed the `hosting` block (and its `rewrites` rule) from
  [`firebase.json`](../modules/firebase.json.md).
- Disabled the Firebase Hosting site (`firebase hosting:disable`) so it
  doesn't keep serving a broken empty shell to anyone who happens to hit
  the old `.web.app` URL.
- The app is now reached at its Cloud Run URL directly:
  `https://app-tracker-<hash>-uc.a.run.app` (see the exact current URL
  in the main [README](../../README.md) or by running
  `gcloud run services describe app-tracker --region us-central1
  --format='value(status.url)'`).

## Consequences

- The app's URL is a long, Cloud-Run-generated one instead of a clean
  `project-id.web.app` one. For a small internal/personal tool, this is
  an acceptable trade-off.
- If a clean custom domain is wanted later, **do not** re-introduce a
  Firebase Hosting rewrite — front Cloud Run with a **Google Cloud HTTPS
  Load Balancer + Serverless NEG** instead, which does support
  WebSockets. This is meaningfully more setup (a reserved static IP, a
  managed SSL certificate, and DNS records pointed at the load
  balancer), so only worth doing if a custom domain becomes a real
  requirement.
- `firebase.json` now only configures Authentication and Firestore —
  Firebase Hosting is simply not part of this project's deployment
  anymore. Don't re-add a `hosting` block without re-reading this ADR
  first.
- Any future Cloud Run redeploy command needs to keep including
  `--session-affinity` — see
  [ADR 0005](0005-cloud-run-session-affinity.md), which was also
  required (in addition to this one) to fully fix session behavior.
