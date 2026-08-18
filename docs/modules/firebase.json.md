# `firebase.json` and `.firebaserc`

Configuration files read by the `firebase` CLI — they tell it which
Google Cloud/Firebase project to act on, and how to configure that
project's Authentication and Firestore settings.

## `.firebaserc`

```json
{
  "projects": {
    "default": "app-tracker-76d85",
    "App tracker": "app-tracker-76d85"
  },
  "targets": {},
  "etags": {}
}
```

Maps a short alias (`default`) to an actual Firebase **project ID**
(`app-tracker-76d85`). Every `firebase` CLI command run in this
directory (e.g. `firebase deploy`) acts on whichever project `default`
points to, unless overridden with `--project`. Generated/updated by
running `firebase use --add` (see [`quickstart.md`](../quickstart.md)).
Safe to commit — it identifies a project, it isn't a credential.

## `firebase.json`

```json
{
  "firestore": {
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  },
  "auth": {
    "authorizedDomains": ["localhost"],
    "providers": {
      "emailPassword": true
    }
  }
}
```

Two sections, corresponding to the two Firebase services this app uses:

- **`firestore`** — points at the two files that get deployed by
  `firebase deploy --only firestore`:
  [`firestore.rules`](firestore.rules.md) (client access rules) and
  [`firestore.indexes.json`](firestore.indexes.json.md) (composite
  index definitions).
- **`auth`** — declares that the **Email/Password** sign-in provider
  should be enabled (`emailPassword: true`), and that `localhost` is an
  authorized domain (relevant for local development flows that involve
  browser redirects — this app's actual login doesn't use redirects, per
  [ADR 0002](../adr/0002-auth-via-rest-api-not-web-sdk.md), but this
  section can still be deployed with `firebase deploy --only auth` to
  configure the provider without clicking through the console).

### What used to be here

This file previously also had a `"hosting"` section that pointed Firebase
Hosting at the Cloud Run service via a `rewrite` rule. It was removed
because Firebase Hosting's proxy doesn't support the WebSocket
connection Streamlit requires — see
[ADR 0004](../adr/0004-cloud-run-direct-not-firebase-hosting.md) for the
full story before considering adding a `hosting` block back.
