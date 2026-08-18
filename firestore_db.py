"""Firestore access for the application tracker.

Uses the Admin SDK, so it runs with full trust server-side. Every read/write
is scoped to the caller's uid — Firestore security rules deny all direct
client access (see firestore.rules), so this module is the only path in.
"""
import datetime as dt

import firebase_admin
from firebase_admin import firestore
from google.api_core.exceptions import FailedPrecondition
from google.cloud.firestore import Query
from google.cloud.firestore_v1.base_query import FieldFilter

STATUSES = ["applied", "oa", "interview", "offer", "rejected"]

_db = None


def client():
    global _db
    if _db is None:
        # Make sure the Admin SDK is initialized even if this module gets
        # imported before the app's entrypoint calls initialize_app().
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        _db = firestore.client()
    return _db


def list_applications(uid: str) -> list[dict]:
    try:
        docs = (
            client()
            .collection("applications")
            .where(filter=FieldFilter("uid", "==", uid))
            .order_by("created_at", direction=Query.DESCENDING)
            .stream()
        )
    except FailedPrecondition as e:
        raise RuntimeError(
            "Firestore query requires a composite index on "
            "(uid ASC, created_at DESC) for the 'applications' collection. "
            "Create it in the Firebase console, or click the link in the "
            "original error below.\n"
            f"Original error: {e}"
        ) from e

    results = []
    for doc in docs:
        item = doc.to_dict()
        if item is None:
            continue  # doc exists but has no fields — skip it
        item["id"] = doc.id
        results.append(item)
    return results


def add_application(uid: str, company: str, role: str, notes: str = "") -> str:
    now = dt.datetime.now(dt.timezone.utc)
    _, ref = client().collection("applications").add(
        {
            "uid": uid,
            "company": company,
            "role": role,
            "notes": notes,
            "status": "applied",
            "created_at": now,
            "updated_at": now,
        }
    )
    return ref.id


def update_status(uid: str, application_id: str, status: str) -> None:
    if status not in STATUSES:
        raise ValueError(f"Unknown status: {status}")
    doc_ref = client().collection("applications").document(application_id)
    doc = doc_ref.get()
    data = doc.to_dict()
    if not doc.exists or data is None or data.get("uid") != uid:
        raise PermissionError("Application not found for this user")
    doc_ref.update({"status": status, "updated_at": dt.datetime.now(dt.timezone.utc)})


def delete_application(uid: str, application_id: str) -> None:
    doc_ref = client().collection("applications").document(application_id)
    doc = doc_ref.get()
    data = doc.to_dict()
    if not doc.exists or data is None or data.get("uid") != uid:
        raise PermissionError("Application not found for this user")
    doc_ref.delete()