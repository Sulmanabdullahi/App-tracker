# `.env`, `.env.example`, and environment variables

## `.env.example`

```
# Firebase project (Console > Project Settings > General)
FIREBASE_PROJECT_ID=your-project-id

# Web API key (Console > Project Settings > General > Web API Key)
# Used for the Auth REST calls in firebase_auth.py.
FIREBASE_API_KEY=

# Local dev only: path to a service account key (Console > Project Settings
# > Service Accounts > Generate new private key). Grants the Admin SDK
# access to Firestore + Auth. On Cloud Run, leave this unset — the
# attached service account is picked up automatically instead.
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json
```

A template, committed to the repository, showing every environment
variable the app needs and where to find each value. It contains no
real secrets — just placeholders and instructions. Copy it to a real
`.env` file (`cp .env.example .env`) and fill in actual values, as
described in [`quickstart.md`](../quickstart.md).

## `.env`

Your own local copy, with real values filled in. **Never commit this
file** — it's listed in [`.gitignore`](../../.gitignore) specifically so
it can't be accidentally added. [`app.py`](app.py.md) loads it at
startup via `python-dotenv`'s `load_dotenv()`, which reads `.env` and
copies its values into the process's environment variables — this only
happens locally; in production, these same variable names are set
directly on the Cloud Run service instead (via `--set-env-vars` on
`gcloud run deploy`), and there is no `.env` file inside the deployed
container at all.

## The three variables, explained

### `FIREBASE_PROJECT_ID`

Identifies which Firebase/Google Cloud project the Admin SDK should
connect to. Read implicitly by the `firebase-admin` library during
`firebase_admin.initialize_app()` in [`app.py`](app.py.md) — it isn't
referenced by name anywhere in this app's own code, but the Admin SDK
looks for it in the environment.

### `FIREBASE_API_KEY`

Used only by [`firebase_auth.py`](firebase_auth.py.md), to identify
which Firebase project a sign-up/sign-in REST request is for. As
explained in [`modules/firebase_auth.py.md`](firebase_auth.py.md), this
is not a secret that grants access by itself — it's the same value
that's visible in any normal Firebase web app's browser network traffic.
Still handled as a configuration value here rather than hardcoded, so
different environments (local dev vs. production) can use different
Firebase projects without a code change.

### `GOOGLE_APPLICATION_CREDENTIALS`

The path to a downloaded **service account key** JSON file (see
[`quickstart.md`](../quickstart.md) step 4). This is the credential that
lets the Admin SDK actually authenticate as a trusted server — without
it (and without running on Cloud Run, which provides credentials a
different way), every Admin SDK call would fail with a permissions
error.

**This variable should be set locally, and left *unset* in
production.** On Cloud Run, Google's client libraries automatically
detect they're running in a Google Cloud environment and use the
service account *attached to the Cloud Run service itself* — no key
file needed, and no key file should ever be baked into the container
image (see the `.dockerignore` note in
[`Dockerfile.md`](Dockerfile.md)). The `service-account.json` file this
points to is itself listed in `.gitignore` and must never be committed —
treat it exactly like a password. If one is ever accidentally
committed or leaked, see
[`sops/rotate-the-firebase-api-key.md`](../sops/rotate-the-firebase-api-key.md)
for the closest related rotation procedure, and additionally revoke the
leaked key from **Project Settings > Service Accounts** in the Firebase
console immediately.
