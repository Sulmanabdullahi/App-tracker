# SOP: Deploy a change

Ships the current code in this repository to the live Cloud Run service.
There is no CI/CD pipeline for this project — deploys are run by hand
from a developer's machine.

## Prerequisites (one-time machine setup)

- [ ] `gcloud` CLI installed (`brew install --cask google-cloud-sdk` on
      macOS) and on your `PATH`
- [ ] `gcloud auth login` run at least once (opens a browser)
- [ ] `gcloud config set project app-tracker-76d85` (or run with
      `--project app-tracker-76d85` on every command instead)
- [ ] The Firebase CLI installed and logged in (`firebase login`) — see
      [`quickstart.md`](../quickstart.md)

If you're deploying this app to a **brand new** Google Cloud project for
the first time (not just pushing an update to the existing one), these
one-time steps are also required before the deploy command below will
work — skip them if `app-tracker-76d85` (or your project) is already
set up:

```bash
# Link a billing account — Cloud Run refuses to enable at all without one,
# even if usage stays within the free tier.
gcloud billing accounts list
gcloud billing projects link <PROJECT_ID> --billing-account=<ACCOUNT_ID>

# Enable the required APIs.
gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com --project <PROJECT_ID>

# Grant the Cloud Run service account access to Firestore.
gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member="serviceAccount:<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
  --role="roles/datastore.user" \
  --condition=None
```

## The actual deploy

From the repo root:

```bash
gcloud run deploy app-tracker \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --session-affinity \
  --set-env-vars FIREBASE_PROJECT_ID=<project-id>,FIREBASE_API_KEY=<web-api-key> \
  --project <project-id>
```

This single command builds a fresh container image from the
[`Dockerfile`](../modules/Dockerfile.md) (via Cloud Build), pushes it,
and points the `app-tracker` Cloud Run service at the new image —
typically takes 2–5 minutes. It prints a **Service URL** when done;
that's the live app.

**Do not drop `--session-affinity`** — see
[ADR 0005](../adr/0005-cloud-run-session-affinity.md). A deploy without
it will silently reintroduce the "stuck on loading screen" bug.

If Firestore rules or indexes changed (i.e. you edited
[`firestore.rules`](../modules/firestore.rules.md) or
[`firestore.indexes.json`](../modules/firestore.indexes.json.md)), also
run:

```bash
firebase deploy --only firestore --project <project-id>
```

(This is a separate command because rules/indexes are Firestore
configuration, not part of the container — see
[`architecture.md`](../architecture.md#4-deployment-shape).)

## Verify it worked

```bash
curl -s -o /dev/null -w "%{http_code}\n" <service-url>
```

Should print `200`. For a real functional check (not just "the server
responds"), open the URL in a browser and log in — or see
[`troubleshoot-blank-loading-screen.md`](troubleshoot-blank-loading-screen.md)
if it doesn't render properly.

## Rolling back

Cloud Run keeps every previous revision. To find and revert to one:

```bash
gcloud run revisions list --service app-tracker --region us-central1
gcloud run services update-traffic app-tracker --region us-central1 \
  --to-revisions=<previous-revision-name>=100
```
