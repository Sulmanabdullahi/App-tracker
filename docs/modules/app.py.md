# `app.py`

The entire Streamlit UI. This is the file Streamlit actually runs
(`streamlit run app.py`), and it's the only file that renders anything
on screen — [`firebase_auth.py`](firebase_auth.py.md) and
[`firestore_db.py`](firestore_db.py.md) do the backend work this file
calls into.

If you're new to Streamlit: this script re-runs from top to bottom every
time the user interacts with anything (clicks a button, submits a form,
changes a dropdown). There's no separate "event handler" system — the
`if st.form_submit_button(...):` pattern you'll see throughout *is* the
event handling. See [ADR 0001](../adr/0001-use-streamlit-for-the-ui.md)
for why the app is built this way.

## Walkthrough

### Setup (lines 1–27)

```python
import firebase_admin
...
load_dotenv()

if not firebase_admin._apps:
    firebase_admin.initialize_app()

import firebase_auth
import firestore_db
```

`load_dotenv()` reads the `.env` file (see
[`env-files.md`](env-files.md)) into environment variables, if one
exists — this only matters for local development; in production these
variables are set directly on the Cloud Run service.

`firebase_admin.initialize_app()` sets up the Admin SDK connection to
Firebase. This has to happen **before** `firebase_auth` or
`firestore_db` are imported, because both of those modules use the Admin
SDK as soon as they're used — hence the `# noqa: E402` comments (which
tell Python linters "yes, these imports are intentionally not at the top
of the file").

`st.set_page_config(...)` sets the browser tab's title and icon, and
switches to Streamlit's "wide" layout (uses the full browser width,
which suits the multi-column Kanban board later).

The `st.markdown(...)` block right after injects a small bit of raw CSS
via `unsafe_allow_html=True` — this hides Streamlit's default hamburger
menu and footer branding (`#MainMenu, footer {visibility: hidden;}`) and
removes the default border/padding Streamlit puts around `st.form`
containers, so the login card looks like one clean box instead of a box
inside a box.

### `STATUS_META` (lines 29–35)

A dictionary mapping each internal status value (`"applied"`, `"oa"`,
etc. — the same values defined in
[`firestore_db.STATUSES`](firestore_db.py.md)) to what's actually shown
to the user: a human-readable label and an emoji icon. Kept separate
from `firestore_db.STATUSES` deliberately — the database only needs to
know the *valid values*, while the UI needs to know how to *display*
them. If you rename a status's label or icon, you only touch this
dictionary; the stored data (and `firestore_db.py`) don't change. See
[`sops/add-or-remove-a-status-column.md`](../sops/add-or-remove-a-status-column.md)
for adding an entirely new status.

### `_relative_time(value)` (lines 38–48)

A small helper that turns a stored `created_at` timestamp into a
friendly string like "added today," "added yesterday," or "added 5 days
ago," for display on each application card. Leading underscore is a
Python convention meaning "internal to this file, not meant to be
imported elsewhere."

### `render_login()` (lines 51–105)

Draws the logged-out screen: the title, a centered card (achieved with
`st.columns([1, 1.3, 1])` — three columns where only the wider middle
one is used, which visually centers its contents), and a `Log in` /
`Sign up` tabbed form.

Both tabs follow the identical pattern:

1. `st.form(...)` groups the inputs so nothing submits until the button
   is clicked (rather than re-running on every keystroke).
2. On submit, do basic client-side validation (both fields non-empty).
3. Call into [`firebase_auth.py`](firebase_auth.py.md)
   (`sign_in`/`sign_up`), inside a `try`/`except firebase_auth.AuthError`
   so a bad password or a duplicate email shows a friendly `st.error(...)`
   message instead of crashing the app.
4. On success, save the returned session dict into
   `st.session_state.session` and call `st.rerun()` — this immediately
   re-runs the script, and since `st.session_state.session` now exists,
   the bottom of the file (see below) will render the dashboard instead.

### `render_dashboard()` (lines 108–177)

Draws the logged-in screen. Runs on every interaction while logged in —
so at the top, it always re-fetches the current user's applications
fresh from Firestore (`firestore_db.list_applications(uid)`), meaning
the board is always showing current data, at the cost of one Firestore
read per interaction. Fine at this app's scale.

- **Sidebar** — shows the signed-in email, a running count of
  applications, and a **Log out** button that deletes
  `st.session_state.session` and reruns (which sends the user back to
  `render_login()`).
- **"Add application" expander** — a form for company/role/notes. Uses
  `expanded=not applications` so it's automatically open when the user
  has no applications yet (nothing to hide), and collapsed once they
  have at least one (so it doesn't dominate the screen). On submit,
  calls `firestore_db.add_application(...)`, shows a success toast
  (`st.toast(...)`), and reruns.
- **Empty state** — if there are no applications at all, shows a
  friendly message and returns early (skips rendering an empty board).
- **The Kanban board** — one `st.columns(...)` per status in
  `firestore_db.STATUSES`. For each column: a subheader with the status's
  icon, label, and count; either a "Nothing here yet" caption or one
  card per matching application.
- **Each card** (`st.container(border=True)`) shows the company, role,
  optional notes, and relative added time, followed by two controls
  side-by-side:
  - A `st.selectbox` for status. If the user picks a different value
    than the card's current column, `firestore_db.update_status(...)`
    is called immediately and the page reruns — this is what makes
    "moving" a card between columns work; there's no drag-and-drop,
    just "pick a new status from the dropdown."
  - A `st.popover` behind a 🗑️ icon, which only shows a **Confirm
    delete** button once opened — this two-step interaction is a
    deliberate guard against fat-fingering a permanent delete (see
    `firestore_db.delete_application`, which really does delete the
    document, no soft-delete/undo).

### Entry point (lines 180–183)

```python
if "session" not in st.session_state:
    render_login()
else:
    render_dashboard()
```

This is the actual "router" for the whole app — the only place that
decides which screen to show, based purely on whether a session exists
in memory. There's no URL routing at all; it's just this one `if`.
