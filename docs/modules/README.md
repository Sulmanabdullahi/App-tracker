# Module Reference

One document per file in the repository root, explaining what it's for
and walking through its contents. Read [`../glossary.md`](../glossary.md)
first if you're unfamiliar with the terminology, and
[`../architecture.md`](../architecture.md) for how these files relate to
each other.

## Application code

| File | What it is |
|---|---|
| [`app.py.md`](app.py.md) | The Streamlit UI — every screen the user sees |
| [`firebase_auth.py.md`](firebase_auth.py.md) | Sign-up/login logic (talks to Firebase Authentication) |
| [`firestore_db.py.md`](firestore_db.py.md) | All database reads/writes (talks to Firestore) |

## Configuration and infrastructure

| File | What it is |
|---|---|
| [`Dockerfile.md`](Dockerfile.md) | Recipe for building the container Cloud Run runs |
| [`requirements.txt.md`](requirements.txt.md) | Python packages the app depends on |
| [`firebase.json.md`](firebase.json.md) | Firebase project configuration (Auth + Firestore settings) |
| [`firestore.rules.md`](firestore.rules.md) | Firestore's client-access security rules (deny-all) |
| [`firestore.indexes.json.md`](firestore.indexes.json.md) | Declares the Firestore composite index this app's queries need |
| [`env-files.md`](env-files.md) | `.env`, `.env.example`, and the environment variables the app reads |
