# Application Tracker

A Streamlit app for tracking job applications, backed by Firebase
(Authentication for login, Firestore for storage) and deployed straight to
Cloud Run.

The app is served **directly from its Cloud Run URL**, not through Firebase
Hosting. Streamlit needs a persistent WebSocket (`/_stcore/stream`) to push
UI updates to the browser, and Firebase Hosting's rewrite proxy to Cloud Run
doesn't forward the WebSocket upgrade (the handshake comes back as a plain
`200` instead of `101 Switching Protocols`), so the page never renders past
an empty shell. This is a known limitation, not a config mistake — see
[nicegui#3563](https://github.com/zauberzeug/nicegui/discussions/3563) and
[streamlit#10341](https://github.com/streamlit/streamlit/issues/10341). If a
custom domain is needed later, front Cloud Run with a Google Cloud HTTPS
Load Balancer + Serverless NEG (which does support WebSockets) rather than a
Firebase Hosting rewrite.

## How it fits together

- **`app.py`** — Streamlit UI: login/signup screen, then a Kanban-style
  dashboard (Applied / OA / Interview / Offer / Rejected).
- **`firebase_auth.py`** — signs users in/up against the Firebase Auth REST
  API (Identity Toolkit), since Streamlit has no browser JS runtime to run
  the normal Firebase Web SDK. The returned ID token is re-verified with the
  Admin SDK before the uid is trusted.
- **`firestore_db.py`** — all Firestore reads/writes, via the Admin SDK,
  scoped to the signed-in user's `uid`.
- **`firestore.rules`** — denies all *direct* client access to Firestore.
  The Admin SDK (used server-side by this app) bypasses these rules, which
  is the point: clients never talk to Firestore directly.
- `Dockerfile` builds the Streamlit app into a container that Cloud Run
  runs directly; `firebase.json` only manages Auth and Firestore config now.

## One-time Firebase setup

1. Create a Firebase project (or use an existing one) and update
   `.firebaserc` with its project ID.
2. Enable **Authentication > Sign-in method > Email/Password** in the
   [Firebase Console](https://console.firebase.google.com), or run:
   ```bash
   npx -y firebase-tools@latest deploy --only auth
   ```
3. Create a **Firestore database** in the console (Native mode, any region).
4. Grab your **Web API key**: Project Settings > General > Web API Key.
5. Generate a **service account key** for local dev: Project Settings >
   Service Accounts > Generate new private key. Save it as
   `service-account.json` in this folder (it's gitignored).

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# fill in FIREBASE_PROJECT_ID and FIREBASE_API_KEY in .env

streamlit run app.py
```

## Deploying

The app runs as a container on Cloud Run, and is accessed at its Cloud Run
URL directly (see the note above on why Firebase Hosting isn't used for
this). `--session-affinity` is required so a browser stays pinned to the
same instance — otherwise Streamlit's in-memory session state resets on
every reconnect.

```bash
# Build and deploy the container to Cloud Run (uses the attached service
# account automatically — no key file needed in production).
gcloud run deploy app-tracker \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --session-affinity \
  --set-env-vars FIREBASE_PROJECT_ID=your-project-id,FIREBASE_API_KEY=your-web-api-key

# Push updated Firestore rules/indexes.
npx -y firebase-tools@latest deploy --only firestore
```

Make sure the Cloud Run service's service account has the **Cloud
Datastore User** (or Firebase Admin) IAM role so the Admin SDK can read/write
Firestore.

## Data model

Firestore collection `applications`, one document per application:

| field        | type      | notes                              |
|--------------|-----------|-------------------------------------|
| `uid`        | string    | owner's Firebase Auth uid           |
| `company`    | string    |                                      |
| `role`       | string    |                                      |
| `notes`      | string    | optional                            |
| `status`     | string    | `applied` / `oa` / `interview` / `offer` / `rejected` |
| `created_at` | timestamp |                                      |
| `updated_at` | timestamp |                                      |
