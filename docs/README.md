# Documentation

This is the documentation hub for **Application Tracker** — a small
Streamlit web app for tracking job applications, backed by Firebase.

If you are brand new to this project, read the docs in this order:

1. **[glossary.md](glossary.md)** — plain-English definitions of every
   piece of jargon used elsewhere in these docs (Firestore, Streamlit,
   Cloud Run, WebSocket, uid, and so on). Read this first if any term in
   the other docs is unfamiliar.
2. **[quickstart.md](quickstart.md)** — get the app running on your own
   machine, from a completely empty starting point, in under 15 minutes.
3. **[architecture.md](architecture.md)** — how the pieces fit together:
   the browser, the Streamlit server, Firebase Authentication, and
   Firestore. Explains *why* the system is shaped the way it is.

After that, the rest of this folder is reference material, organized by
purpose:

## `adr/` — Architecture Decision Records

A log of the significant decisions made while building this app, in the
order they were made. Each one explains a problem we ran into, the choice
we made, and the trade-off that choice implies. Read these when you want
to know *why* something is built a certain way instead of the more
"obvious" alternative.

| ADR | Decision |
|---|---|
| [0001](adr/0001-use-streamlit-for-the-ui.md) | Build the UI in Streamlit (pure Python, no HTML/JS) |
| [0002](adr/0002-auth-via-rest-api-not-web-sdk.md) | Sign in via the Firebase Auth REST API, not the Firebase Web SDK |
| [0003](adr/0003-admin-sdk-server-side-with-deny-all-rules.md) | Access Firestore only through the server-side Admin SDK; deny all direct client access |
| [0004](adr/0004-cloud-run-direct-not-firebase-hosting.md) | Serve the app directly from its Cloud Run URL, not behind Firebase Hosting |
| [0005](adr/0005-cloud-run-session-affinity.md) | Always deploy with Cloud Run session affinity enabled |

See [adr/README.md](adr/README.md) for what an ADR is and the template
used here.

## `modules/` — what every file in this repo does

One document per source file in the repository root. Each one explains,
in order: what the file is for, a walk-through of its contents from top
to bottom, and any gotchas or things that would surprise a newcomer.

See [modules/README.md](modules/README.md) for the full list.

## `sops/` — Standard Operating Procedures

Step-by-step instructions for tasks someone maintaining this app will
need to do repeatedly: deploying a change, running it locally, rotating
a secret, adding a feature, deleting a user's data, and diagnosing the
"blank loading screen" bug if it ever comes back.

See [sops/README.md](sops/README.md) for the full list.

## How this documentation is organized (and why)

- **Glossary and quickstart** are for someone who has never seen this
  project before and needs to get oriented and productive quickly.
- **Architecture** is for understanding the *shape* of the system —
  what talks to what, and why.
- **ADRs** are historical records. They are not supposed to be edited
  after the fact to reflect new decisions — instead, a new ADR is added
  when a past decision is revisited or reversed (with a note in the old
  one pointing to the new one).
- **Module docs** are a per-file reference — useful when you're about to
  change a specific file and want to understand it in isolation first.
- **SOPs** are task-oriented runbooks — useful when you know *what* you
  need to do (deploy, roll a key, debug a hosting issue) and just need
  the exact steps.
