# SOP: Rotate the Firebase Web API key

When to do this: routine credential hygiene, or the key has appeared
somewhere it shouldn't have (a public repo, a shared screenshot, etc.).
As explained in [`modules/env-files.md`](../modules/env-files.md), this
specific key is not a high-severity secret on its own (it's visible in
any normal Firebase web app's browser traffic) — but rotating it is
still cheap and reasonable if you're unsure.

## 1. Restrict or regenerate the key

Web API keys for Firebase projects are managed as **Google Cloud API
keys**. In the [Google Cloud Console](https://console.cloud.google.com)
for the project: **APIs & Services > Credentials**.

- To **restrict** the existing key (recommended first step, often
  sufficient on its own): click the key, and under "API restrictions,"
  limit it to only the APIs this app actually needs (Identity Toolkit /
  Token Service). This means even if the key leaks, it can't be used for
  unrelated Google APIs.
- To fully **regenerate** it: click **Regenerate Key** — this
  immediately invalidates the old value everywhere it's in use.

## 2. Get the new key value

Either copy it from the Cloud Console credentials page, or via the
Firebase CLI:

```bash
firebase apps:list --project <project-id>
firebase apps:sdkconfig WEB <app-id> --project <project-id>
```

The `apiKey` field in that output is the current value.

## 3. Update everywhere it's used

- **Local development**: update `FIREBASE_API_KEY` in your `.env` file
  (see [`modules/env-files.md`](../modules/env-files.md)).
- **Production (Cloud Run)**: redeploy with the new value —
  ```bash
  gcloud run services update app-tracker --region us-central1 \
    --set-env-vars FIREBASE_API_KEY=<new-key>
  ```
  (This updates the env var without a full rebuild. If you're also
  shipping a code change at the same time, just include
  `FIREBASE_API_KEY=<new-key>` in the normal
  [deploy command](deploy-a-change.md) instead.)

## 4. Verify

Open the live app URL and try logging in. A stale/invalid key shows up
as a login failure (`AuthError`) — see
[`modules/firebase_auth.py.md`](../modules/firebase_auth.py.md).

## If a service account key (not the Web API key) leaked

This is more serious — a service account key grants the same trust as
the Admin SDK (see
[ADR 0003](../adr/0003-admin-sdk-server-side-with-deny-all-rules.md)).
In the Firebase console: **Project Settings > Service Accounts**, find
the leaked key under the relevant service account, and delete it
immediately, then generate a new one and update your local
`service-account.json` (never used in production — see
[`modules/env-files.md`](../modules/env-files.md)).
