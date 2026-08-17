# `firebase_auth.py`

Handles sign-up and sign-in. This is the only file that talks to
Firebase **Authentication** — [`firestore_db.py`](firestore_db.py.md) is
a separate file for the separate concern of storing application data.

Read [ADR 0002](../adr/0002-auth-via-rest-api-not-web-sdk.md) first —
it explains *why* this file calls a raw REST API instead of using
Firebase's normal browser-based login flow. The short version: Streamlit
can't run custom JavaScript in the browser, so this has to happen
server-side instead.

## Walkthrough

### Module docstring and imports (lines 1–13)

```python
_IDENTITY_TOOLKIT_URL = "https://identitytoolkit.googleapis.com/v1/accounts:{endpoint}"
```

This is the base URL for Google's **Identity Toolkit** REST API — the
actual service behind Firebase Authentication. `{endpoint}` gets filled
in with either `signUp` or `signInWithPassword` depending on which
action is happening.

### `AuthError` (line 16–17)

A custom exception type. [`app.py`](app.py.md) catches specifically
`firebase_auth.AuthError` to show the user a friendly message — any
*other* unexpected exception would still crash the app (which is
intentional: we only want to hide errors we've deliberately decided are
"expected," like a wrong password).

### `_api_key()` (lines 20–26)

Reads the `FIREBASE_API_KEY` environment variable (see
[`env-files.md`](env-files.md)). If it's missing, raises `AuthError`
with an instruction to fill in `.env` — rather than a raw `KeyError`,
which would be a much less helpful crash message for someone setting
the project up for the first time.

### `_call_identity_toolkit(endpoint, payload)` (lines 29–39)

The shared HTTP-calling logic behind both `sign_up` and `sign_in` (they
only differ in *which* endpoint and payload they use — this function is
the part that actually makes the network request).

```python
resp = requests.post(
    _IDENTITY_TOOLKIT_URL.format(endpoint=endpoint),
    params={"key": _api_key()},
    json=payload,
    timeout=10,
)
```

The Web API key is passed as a URL query parameter (`?key=...`) — this
is how the Identity Toolkit API identifies *which Firebase project* the
request is for. It is **not** a per-user password or secret.

If the response isn't a `200`, the error message Google's API returned
(e.g. `"EMAIL_NOT_FOUND"`, `"INVALID_PASSWORD"`, `"WEAK_PASSWORD :
Password should be at least 6 characters"`) is re-raised as an
`AuthError`, so it bubbles up to `app.py`'s `st.error(...)` call.

### `sign_up(email, password)` and `sign_in(email, password)` (lines 42–56)

Thin wrappers that call `_call_identity_toolkit` with the right endpoint
name (`signUp` or `signInWithPassword`) and payload shape, then hand the
result to `_to_session`. Both return the same shape of dict — `app.py`
doesn't need to know or care which one was used.

### `_to_session(data)` (lines 59–68)

```python
id_token = data["idToken"]
decoded = admin_auth.verify_id_token(id_token)
return {
    "uid": decoded["uid"],
    "email": decoded.get("email", data.get("email")),
    "id_token": id_token,
    "refresh_token": data["refreshToken"],
}
```

This is the most important line in the file for security:
`admin_auth.verify_id_token(id_token)`. The Identity Toolkit REST
response already includes fields like `localId` (the uid) directly — it
would be *simpler* to just trust those. Instead, the ID token it also
returns is independently re-verified using the **Admin SDK**, which
cryptographically checks the token's signature. This is what
[ADR 0002](../adr/0002-auth-via-rest-api-not-web-sdk.md) means by "don't
trust the REST response's uid directly" — the `uid` this function
actually returns comes from the *verified, decoded token*, not from the
raw REST payload.

The returned dict becomes `st.session_state.session` in
[`app.py`](app.py.md), and its `uid` is what gets passed into every
[`firestore_db.py`](firestore_db.py.md) function from then on, to scope
that user to only their own data.

Note: `id_token` and `refresh_token` are stored in session state but
**not currently used again anywhere else in the app** after login — the
app relies on `st.session_state` itself (which lives in server memory,
per [ADR 0005](../adr/0005-cloud-run-session-affinity.md)) to represent
"is this user logged in," rather than re-checking the token on every
request. If this app ever needs the tokens to expire and force
re-login, or to refresh a token, `refresh_token` is what would be used
for that — it isn't wired up yet.
