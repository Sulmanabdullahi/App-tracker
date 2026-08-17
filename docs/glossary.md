# Glossary

Plain-English definitions of every technical term used in this project's
documentation. If you're new to Python web apps, Firebase, or Google
Cloud, start here.

## The app itself

**Streamlit**
A Python library for building web apps without writing HTML, CSS, or
JavaScript. You write a normal-looking Python script (see
[`app.py`](../app.py)) that calls functions like `st.button(...)` or
`st.text_input(...)`, and Streamlit turns that into a live web page. Every
time the user clicks something, Streamlit re-runs your Python script
top-to-bottom and re-renders the page with the new state. This is why
you'll see `st.rerun()` scattered through the code — it's an explicit
"re-run the script now" instruction.

**Session state**
The data Streamlit remembers about *one specific browser tab* between
re-runs — for example, "this tab is logged in as user X." In this app,
that's `st.session_state.session`, which holds the signed-in user's uid,
email, and tokens. Session state lives in the *server's* memory, not the
browser's. This matters a lot for how the app is hosted — see
[ADR 0005](adr/0005-cloud-run-session-affinity.md).

**WebSocket**
A network connection that, unlike a normal web request, stays open so the
server can keep sending the browser updates without the browser having to
ask again and again. Streamlit uses one (at the URL path `/_stcore/stream`)
to push UI updates to your browser after the initial page load. If this
connection can't be established, the page loads its outer shell but never
fills in with content — this is exactly the bug documented in
[ADR 0004](adr/0004-cloud-run-direct-not-firebase-hosting.md) and
[the troubleshooting SOP](sops/troubleshoot-blank-loading-screen.md).

## Firebase (the backend platform)

**Firebase**
A collection of backend services from Google, aimed at apps that don't
want to run their own servers. This project uses two of them:
**Authentication** (who is this user?) and **Firestore** (where is their
data stored?).

**Firebase Authentication**
The service that handles user sign-up/login (email + password, in this
app) and issues each signed-in user a unique, permanent ID called a
**uid**.

**uid**
Short for "user ID." A unique string Firebase Authentication assigns to
every user account, forever. Every application record in Firestore is
tagged with the `uid` of the person who created it — this is how "your
applications" are kept separate from everyone else's.

**ID token**
A signed, temporary credential Firebase Authentication hands back after a
successful sign-in. It proves "this really is user X" without needing to
send X's password around again. This app receives one from the REST API
and immediately re-checks it with the Admin SDK (see
[`firebase_auth.py`](modules/firebase_auth.py.md)) before trusting it.

**Identity Toolkit**
The actual name of the REST API behind Firebase Authentication
(`identitytoolkit.googleapis.com`). Normally, apps use Google's
"Firebase Web SDK" (JavaScript) to talk to it invisibly. This app calls
it directly over HTTPS from Python instead — see
[ADR 0002](adr/0002-auth-via-rest-api-not-web-sdk.md) for why.

**Firebase Web API key**
Not a secret in the traditional sense — it identifies *which Firebase
project* a request is for for and is safe to see in a browser's network
tab in a normal web app. This app still keeps it in an environment
variable (`FIREBASE_API_KEY`) for convenience, not because leaking it is
a security incident on its own.

**Firestore**
A NoSQL, document-based database. Data is organized into *collections*
(like a folder — e.g. `applications`) full of *documents* (like a file —
e.g. one job application), each of which is a set of key/value fields.
See the [data model section of the README](../README.md#data-model) for
the exact fields used here.

**Firebase Admin SDK**
A server-side library (`firebase-admin` on PyPI) that gives *full,
unrestricted* access to a Firebase project's Authentication and Firestore
— it deliberately bypasses the normal security rules, because it's meant
to run only in trusted server environments, never in a browser. This app
uses it from [`firestore_db.py`](modules/firestore_db.py.md) and
[`firebase_auth.py`](modules/firebase_auth.py.md).

**Firestore Security Rules** (`firestore.rules`)
A separate mini-language Firestore uses to decide whether a *direct*
client request (e.g. from browser JavaScript) is allowed to read or
write. This app's rules deny everything, because the browser never talks
to Firestore directly — see
[ADR 0003](adr/0003-admin-sdk-server-side-with-deny-all-rules.md).

**Composite index**
Firestore normally lets you filter or sort by one field for free, but
filtering by one field *and* sorting by a different field (as this app
does: "give me user X's applications, sorted by creation date") requires
a pre-built index describing that exact combination. It's declared in
[`firestore.indexes.json`](modules/firestore.indexes.json.md).

## Google Cloud (the hosting platform)

**Google Cloud Platform (GCP)**
Google's cloud computing platform. Every Firebase project is *also* a
Google Cloud project under the hood — that's why this app's deployment
uses both the `firebase` CLI and the `gcloud` CLI.

**Cloud Run**
A Google Cloud service that runs a Docker container for you and exposes
it as a public HTTPS URL, scaling the number of running copies up and
down automatically based on traffic (including down to zero when idle).
This app's container — built from the [`Dockerfile`](modules/Dockerfile.md)
— runs here.

**Container / Docker / Dockerfile**
A *container* is a self-contained package of an app plus everything it
needs to run (Python, libraries, code), so it behaves the same anywhere.
*Docker* is the tool used to build and run containers. A `Dockerfile` is
the recipe describing how to build one — see
[`modules/Dockerfile.md`](modules/Dockerfile.md).

**Session affinity**
A Cloud Run setting that keeps routing requests from the same browser to
the same running container instance, instead of spreading them across
instances at random. Required by this app because Streamlit keeps session
state in one instance's memory — see
[ADR 0005](adr/0005-cloud-run-session-affinity.md).

**Service account**
A Google Cloud identity used by *programs* instead of humans. Cloud Run
automatically attaches one to this app's container, which is how the
Python code can talk to Firestore/Auth in production without a password
or key file — see the `GOOGLE_APPLICATION_CREDENTIALS` explanation in
[`modules/env-files.md`](modules/env-files.md).

**IAM role**
A named bundle of permissions in Google Cloud (e.g. "Cloud Datastore
User" = "can read/write Firestore data"). Granted to a specific identity
(a person or a service account) on a specific project.

**Billing account**
The payment account a Google Cloud project is linked to. Most services,
including Cloud Run, refuse to turn on at all until a project has one
attached — even if actual usage stays within the free tier.

**`gcloud` CLI**
The command-line tool for Google Cloud. Used here to build/deploy the
container to Cloud Run, manage IAM permissions, and read logs.

**`firebase` CLI**
The command-line tool for Firebase specifically (a layer on top of some
of the same Google Cloud APIs). Used here to deploy Firestore rules and
indexes, and to inspect/manage Authentication users.
