# Architecture Decision Records (ADRs)

## What is an ADR?

A short document that records **one significant decision**, in the order
it was made: what problem we were facing, what we decided to do about
it, and what trade-off that decision costs us. It is *not* a design
document or a how-to guide — those live in
[`../architecture.md`](../architecture.md) and [`../sops/`](../sops/README.md)
respectively.

ADRs are written once and (mostly) never edited afterward, even if the
decision later turns out to be wrong or gets reversed — that's what the
next ADR is for. This preserves the actual history of *why* the codebase
looks the way it does, instead of just the current state.

## Template

Every ADR in this folder follows the same shape:

```markdown
# NNNN. Title (a short verb phrase describing the decision)

**Status:** Accepted | Superseded by ADR-xxxx

## Context
What problem were we facing? What constraints or facts made this a
decision worth making at all, rather than an obvious default?

## Decision
What did we actually decide to do?

## Consequences
What does this cost us? What does it rule out? What should a future
maintainer watch out for because of this decision?
```

## Index

| # | Title |
|---|---|
| [0001](0001-use-streamlit-for-the-ui.md) | Use Streamlit for the UI |
| [0002](0002-auth-via-rest-api-not-web-sdk.md) | Sign in via the Firebase Auth REST API, not the Web SDK |
| [0003](0003-admin-sdk-server-side-with-deny-all-rules.md) | Access Firestore only through the server-side Admin SDK; deny all direct client access |
| [0004](0004-cloud-run-direct-not-firebase-hosting.md) | Serve directly from the Cloud Run URL, not behind Firebase Hosting |
| [0005](0005-cloud-run-session-affinity.md) | Always deploy with Cloud Run session affinity enabled |
