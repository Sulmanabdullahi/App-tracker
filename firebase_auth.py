"""Firebase Authentication for Streamlit.

Streamlit has no browser-side JS runtime to run the Firebase Web SDK, so
sign-in/sign-up happen server-side against the Firebase Auth REST API
(Identity Toolkit). The resulting ID token is re-verified with the Admin
SDK before we trust the uid it carries.
"""
import os

import requests
from firebase_admin import auth as admin_auth

_IDENTITY_TOOLKIT_URL = "https://identitytoolkit.googleapis.com/v1/accounts:{endpoint}"


class AuthError(Exception):
    pass


def _api_key() -> str:
    try:
        return os.environ["FIREBASE_API_KEY"]
    except KeyError:
        raise AuthError(
            "FIREBASE_API_KEY is not set — copy .env.example to .env and fill it in"
        ) from None


def _call_identity_toolkit(endpoint: str, payload: dict) -> dict:
    resp = requests.post(
        _IDENTITY_TOOLKIT_URL.format(endpoint=endpoint),
        params={"key": _api_key()},
        json=payload,
        timeout=10,
    )
    data = resp.json()
    if resp.status_code != 200:
        raise AuthError(data.get("error", {}).get("message", "Authentication failed"))
    return data


def sign_up(email: str, password: str) -> dict:
    """Create a new user and return {uid, email, id_token, refresh_token}."""
    data = _call_identity_toolkit(
        "signUp", {"email": email, "password": password, "returnSecureToken": True}
    )
    return _to_session(data)


def sign_in(email: str, password: str) -> dict:
    """Sign in an existing user and return {uid, email, id_token, refresh_token}."""
    data = _call_identity_toolkit(
        "signInWithPassword",
        {"email": email, "password": password, "returnSecureToken": True},
    )
    return _to_session(data)


def _to_session(data: dict) -> dict:
    id_token = data["idToken"]
    # Re-verify server-side rather than trusting the REST response's uid directly.
    decoded = admin_auth.verify_id_token(id_token)
    return {
        "uid": decoded["uid"],
        "email": decoded.get("email", data.get("email")),
        "id_token": id_token,
        "refresh_token": data["refreshToken"],
    }
