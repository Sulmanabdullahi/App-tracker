# Quick Start

Goal: get this app running on your own laptop, from a completely empty
starting point (no Google Cloud project, no local tools installed), in
under 15 minutes. If any term below is unfamiliar, check the
[glossary](glossary.md).

This guide is for **local development** — running the app on
`localhost` so you can edit code and see changes immediately. To deploy
a copy to the internet, see
[`sops/deploy-a-change.md`](sops/deploy-a-change.md) after you've read
this.

## 1. Prerequisites

Install these if you don't already have them:

- **Python 3.12+** — check with `python3 --version`.
- **A Google account** — any regular Google/Gmail account works; you'll
  use it to create a Firebase project.
- **The Firebase CLI** — installs via npm:
  ```bash
  npm install -g firebase-tools
  ```
  (If you don't have Node.js/npm, install it first — e.g.
  `brew install node` on macOS.)

You do **not** need the `gcloud` CLI or Docker just to run the app
locally — those are only needed for deploying it (see the deploy SOP).

## 2. Create a Firebase project

A "Firebase project" is a free container for the Authentication and
Firestore services this app uses. If your team already has one, skip to
step 3 and ask a teammate for the project ID.

1. Go to <https://console.firebase.google.com> and click **Add project**.
   Give it any name; accept the defaults for everything else.
2. In the new project, go to **Build > Authentication**, click
   **Get started**, choose the **Email/Password** provider under
   **Sign-in method**, and enable it.
3. Go to **Build > Firestore Database**, click **Create database**,
   choose **Native mode**, pick any region, and accept the default
   ("start in production mode" — this app ships its own
   [`firestore.rules`](modules/firestore.rules.md) that deny everything
   by default anyway).
4. Note your **Project ID** — it's shown on the Project Overview page
   (also visible in the URL). You'll need it in the next step. It looks
   like `app-tracker-76d85`, not the human-readable project name.

## 3. Log the Firebase CLI in and connect this repo to your project

```bash
firebase login
```

This opens a browser window to authenticate the CLI with your Google
account.

Then, in the repo root, tell it which project to use:

```bash
firebase use --add
```

Pick your project from the list. This writes (or updates)
[`.firebaserc`](modules/firebase.json.md) with your project ID.

## 4. Get a local service account key

The app needs credentials to talk to Firebase from your machine. In
production (Cloud Run) this is automatic; locally, you need a downloaded
key file:

1. In the Firebase console: **Project Settings** (gear icon) >
   **Service Accounts** tab.
2. Click **Generate new private key**. A JSON file downloads.
3. Move/rename that file to `service-account.json` in the repo root.
   (It's already listed in [`.gitignore`](../.gitignore) — it will never
   be committed. Treat it like a password: don't share it, don't paste
   it into chat, don't commit it under a different name.)

## 5. Get your Web API key

1. Firebase console: **Project Settings > General** tab.
2. Under "Your apps," if there's no Web app yet, click the `</>` icon to
   register one (any nickname is fine, no other options needed).
3. Copy the **Web API Key** shown there.

## 6. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in:

```
FIREBASE_PROJECT_ID=your-project-id-from-step-2
FIREBASE_API_KEY=the-web-api-key-from-step-5
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json
```

See [`modules/env-files.md`](modules/env-files.md) for what each of
these does and why.

## 7. Install Python dependencies and run

```bash
python3 -m venv .venv
source .venv/bin/activate       # on Windows: .venv\Scripts\activate
pip install -r requirements.txt

streamlit run app.py
```

Streamlit will print a local URL (usually `http://localhost:8501`) and
should open it in your browser automatically. You should see the
**Application Tracker** login screen.

## 8. Try it out

1. Click the **Sign up** tab, enter any email and a 6+ character
   password, and click **Create account**.
2. You should land on the dashboard. Expand **Add application**, fill in
   a company and role, and click **Add application**.
3. Your new application should appear in the **Applied** column. Try
   moving it to another status using its dropdown, and deleting it via
   the trash icon (it asks for confirmation first).

If any of this doesn't work, see
[`sops/troubleshoot-blank-loading-screen.md`](sops/troubleshoot-blank-loading-screen.md)
— though that specific issue is a *deployed* (Cloud Run) problem, its
diagnostic steps for checking browser console errors still apply.

## What's next

- Read [`architecture.md`](architecture.md) to understand how the pieces
  you just set up actually talk to each other.
- Read the [module docs](modules/README.md) for a guided tour of each
  source file.
- When you're ready to put a copy on the internet, follow
  [`sops/deploy-a-change.md`](sops/deploy-a-change.md).
