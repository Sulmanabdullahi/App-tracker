"""Firestore access for the application tracker.

Uses the Admin SDK, so it runs with full trust server-side. Every read/write
is scoped to the caller's uid — Firestore security rules deny all direct
client access (see firestore.rules), so this module is the only path in.
"""
import datetime as dt

from firebase_admin import firestore

STATUSES = ["applied", "oa", "interview", "offer", "rejected"]

_db = None


def client():
    global _db
    if _db is None:
        _db = firestore.client()
    return _db


def list_applications(uid: str) -> list[dict]:
    docs = (
        client()
        .collection("applications")
        .where("uid", "==", uid)
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .stream()
    )
    results = []
    for doc in docs:
        item = doc.to_dict()
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
    if not doc.exists or doc.to_dict().get("uid") != uid:
        raise PermissionError("Application not found for this user")
    doc_ref.update({"status": status, "updated_at": dt.datetime.now(dt.timezone.utc)})


def delete_application(uid: str, application_id: str) -> None:
    doc_ref = client().collection("applications").document(application_id)
    doc = doc_ref.get()
    if not doc.exists or doc.to_dict().get("uid") != uid:
        raise PermissionError("Application not found for this user")
    doc_ref.delete()
