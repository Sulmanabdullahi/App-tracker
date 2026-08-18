# `requirements.txt`

The list of Python packages the app depends on, installed via
`pip install -r requirements.txt` (locally — see
[`quickstart.md`](../quickstart.md) — and inside the
[`Dockerfile`](Dockerfile.md) during a container build).

```
streamlit>=1.38
firebase-admin>=6.5
requests>=2.32
python-dotenv>=1.0
```

| Package | Used for | Used in |
|---|---|---|
| `streamlit` | Renders the entire web UI | [`app.py`](app.py.md) |
| `firebase-admin` | Server-side Firebase access: verifying ID tokens and reading/writing Firestore with full trust | [`firebase_auth.py`](firebase_auth.py.md), [`firestore_db.py`](firestore_db.py.md) |
| `requests` | Makes the raw HTTPS call to the Identity Toolkit REST API | [`firebase_auth.py`](firebase_auth.py.md) |
| `python-dotenv` | Loads variables from a local `.env` file into the environment (local development only — see [`env-files.md`](env-files.md)) | [`app.py`](app.py.md) |

Each entry uses `>=` (a minimum version) rather than pinning an exact
version. This means `pip install` always grabs the latest compatible
release available at install time. That's a deliberate simplicity
trade-off for a small project: it avoids ever having to manually bump
version numbers, at the cost of a (small) chance that a future major
release of one of these libraries introduces a breaking change that
isn't caught until a deploy fails. If this app grows in importance,
switching to exact pins (or a lockfile-based tool) would be a reasonable
next step — worth its own ADR if that ever happens.

`firebase-admin` itself pulls in the `google-cloud-firestore` package as
a transitive dependency — that's where the `firestore`, `Query`, and
`FieldFilter` imports used in
[`firestore_db.py`](firestore_db.py.md) actually come from, even though
`google-cloud-firestore` isn't listed here directly.
