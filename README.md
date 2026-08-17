# Application Tracker

A Streamlit app for tracking job applications, backed by Firebase
(Authentication for login, Firestore for storage) and deployed via Cloud Run
behind Firebase Hosting.

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
- Firebase Hosting has no server to run Python, so `firebase.json` rewrites
  all traffic to a Cloud Run service running the Docker image built from
  `Dockerfile`.

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

The app runs as a container on Cloud Run; Firebase Hosting just proxies to
it (see the `rewrites` entry in `firebase.json`).

```bash
# Build and deploy the container to Cloud Run (uses the attached service
# account automatically — no key file needed in production).
gcloud run deploy app-tracker \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FIREBASE_PROJECT_ID=your-project-id,FIREBASE_API_KEY=your-web-api-key

# Point Firebase Hosting at it.
npx -y firebase-tools@latest deploy --only hosting,firestore
```

Make sure the Cloud Run service's service account has the **Cloud
Datastore User** (or Firebase Admin) IAM role so the Admin SDK can read/write
Firestore.

If you deploy under a different service name or region, update the
`hosting.rewrites[0].run` block in `firebase.json` to match.

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
