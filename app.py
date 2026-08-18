import datetime as dt

import firebase_admin
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

if not firebase_admin._apps:
    # ApplicationDefault() picks up GOOGLE_APPLICATION_CREDENTIALS locally,
    # or the attached service account automatically on Cloud Run.
    firebase_admin.initialize_app()

import firebase_auth  # noqa: E402  (must run after initialize_app)
import firestore_db  # noqa: E402

st.set_page_config(page_title="Application Tracker", page_icon="📋", layout="wide")

st.markdown(
    """
    <style>
    #MainMenu, footer {visibility: hidden;}
    div[data-testid="stForm"] {border: none; padding: 0;}
    </style>
    """,
    unsafe_allow_html=True,
)

STATUS_META = {
    "applied": {"label": "Applied", "icon": "📥"},
    "oa": {"label": "OA", "icon": "🧪"},
    "interview": {"label": "Interview", "icon": "🎤"},
    "offer": {"label": "Offer", "icon": "🎉"},
    "rejected": {"label": "Rejected", "icon": "❌"},
}


def _relative_time(value: dt.datetime | None) -> str:
    if value is None:
        return ""
    if value.tzinfo is None:
        value = value.replace(tzinfo=dt.timezone.utc)
    days = (dt.datetime.now(dt.timezone.utc) - value).days
    if days <= 0:
        return "added today"
    if days == 1:
        return "added yesterday"
    return f"added {days} days ago"


def render_login():
    _, center, _ = st.columns([1, 1.3, 1])
    with center:
        st.markdown(
            "<h1 style='text-align: center'>📋 Application Tracker</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='text-align: center; color: gray'>"
            "Keep every job application in one place.</p>",
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            tab_login, tab_signup = st.tabs(["Log in", "Sign up"])

            with tab_login:
                with st.form("login_form"):
                    email = st.text_input("Email", key="login_email", placeholder="you@example.com")
                    password = st.text_input(
                        "Password", type="password", key="login_password"
                    )
                    submitted = st.form_submit_button("Log in", type="primary", use_container_width=True)
                    if submitted:
                        if not email or not password:
                            st.warning("Enter your email and password.")
                        else:
                            try:
                                with st.spinner("Signing in…"):
                                    st.session_state.session = firebase_auth.sign_in(email, password)
                                st.rerun()
                            except firebase_auth.AuthError as e:
                                st.error(str(e))

            with tab_signup:
                with st.form("signup_form"):
                    name_col1, name_col2 = st.columns(2)
                    first_name = name_col1.text_input("First name", key="signup_first_name")
                    last_name = name_col2.text_input("Last name", key="signup_last_name")
                    email = st.text_input(
                        "Email", key="signup_email", placeholder="you@example.com"
                    )
                    password = st.text_input(
                        "Password (min 6 characters)", type="password", key="signup_password"
                    )
                    submitted = st.form_submit_button(
                        "Create account", type="primary", use_container_width=True
                    )
                    if submitted:
                        if not first_name or not last_name or not email or not password:
                            st.warning("Fill in your name, email, and password.")
                        else:
                            try:
                                with st.spinner("Creating your account…"):
                                    st.session_state.session = firebase_auth.sign_up(
                                        email, password, first_name, last_name
                                    )
                                st.rerun()
                            except firebase_auth.AuthError as e:
                                st.error(str(e))


def render_dashboard():
    session = st.session_state.session
    uid = session["uid"]
    applications = firestore_db.list_applications(uid)

    with st.sidebar:
        st.markdown(f"👋 **{session.get('full_name') or session['email']}**")
        st.caption(f"{len(applications)} application{'s' if len(applications) != 1 else ''} tracked")
        st.divider()
        if st.button("🚪 Log out", use_container_width=True):
            del st.session_state.session
            st.rerun()

    st.title("📋 Application Tracker")

    with st.expander("➕ Add application", expanded=not applications):
        with st.form("add_application_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            company = col1.text_input("🏢 Company")
            role = col2.text_input("💼 Role")
            notes = st.text_area("📝 Notes (optional)", height=80)
            submitted = st.form_submit_button("Add application", type="primary")
            if submitted:
                if company and role:
                    firestore_db.add_application(uid, company, role, notes)
                    st.toast(f"Added {company} — {role}", icon="✅")
                    st.rerun()
                else:
                    st.warning("Company and role are required.")

    if not applications:
        st.info("No applications yet — add your first one above. 🚀")
        return

    columns = st.columns(len(firestore_db.STATUSES))
    for col, status in zip(columns, firestore_db.STATUSES):
        meta = STATUS_META[status]
        matching = [a for a in applications if a["status"] == status]
        with col:
            st.subheader(f"{meta['icon']} {meta['label']} ({len(matching)})")
            if not matching:
                st.caption("Nothing here yet")
            for app_ in matching:
                with st.container(border=True):
                    st.markdown(f"**{app_['company']}**")
                    st.caption(app_["role"])
                    if app_.get("notes"):
                        st.caption(app_["notes"])
                    st.caption(_relative_time(app_.get("created_at")))

                    status_col, delete_col = st.columns([3, 1])
                    new_status = status_col.selectbox(
                        "Status",
                        firestore_db.STATUSES,
                        index=firestore_db.STATUSES.index(status),
                        format_func=lambda s: STATUS_META[s]["label"],
                        key=f"status_{app_['id']}",
                        label_visibility="collapsed",
                    )
                    if new_status != status:
                        firestore_db.update_status(uid, app_["id"], new_status)
                        st.toast(f"Moved {app_['company']} to {STATUS_META[new_status]['label']}", icon="📌")
                        st.rerun()

                    with delete_col.popover("🗑️", use_container_width=True):
                        st.write(f"Delete **{app_['company']}**?")
                        if st.button("Confirm delete", key=f"delete_{app_['id']}", type="primary"):
                            firestore_db.delete_application(uid, app_["id"])
                            st.toast(f"Deleted {app_['company']}", icon="🗑️")
                            st.rerun()


if "session" not in st.session_state:
    render_login()
else:
    render_dashboard()
