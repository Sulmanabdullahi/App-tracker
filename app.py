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

STATUS_LABELS = {
    "applied": "Applied",
    "oa": "OA",
    "interview": "Interview",
    "offer": "Offer",
    "rejected": "Rejected",
}


def render_login():
    st.title("📋 Application Tracker")
    tab_login, tab_signup = st.tabs(["Log in", "Sign up"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.form_submit_button("Log in"):
                try:
                    st.session_state.session = firebase_auth.sign_in(email, password)
                    st.rerun()
                except firebase_auth.AuthError as e:
                    st.error(str(e))

    with tab_signup:
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input(
                "Password (min 6 characters)", type="password", key="signup_password"
            )
            if st.form_submit_button("Create account"):
                try:
                    st.session_state.session = firebase_auth.sign_up(email, password)
                    st.rerun()
                except firebase_auth.AuthError as e:
                    st.error(str(e))


def render_dashboard():
    session = st.session_state.session
    uid = session["uid"]

    with st.sidebar:
        st.write(f"Signed in as **{session['email']}**")
        if st.button("Log out"):
            del st.session_state.session
            st.rerun()

    st.title("📋 Application Tracker")

    with st.expander("➕ Add application"):
        with st.form("add_application_form", clear_on_submit=True):
            company = st.text_input("Company")
            role = st.text_input("Role")
            notes = st.text_area("Notes", height=80)
            if st.form_submit_button("Add") and company and role:
                firestore_db.add_application(uid, company, role, notes)
                st.rerun()

    applications = firestore_db.list_applications(uid)
    if not applications:
        st.info("No applications yet — add one above.")
        return

    columns = st.columns(len(firestore_db.STATUSES))
    for col, status in zip(columns, firestore_db.STATUSES):
        with col:
            st.subheader(STATUS_LABELS[status])
            for app_ in [a for a in applications if a["status"] == status]:
                with st.container(border=True):
                    st.markdown(f"**{app_['company']}**")
                    st.caption(app_["role"])
                    if app_.get("notes"):
                        st.caption(app_["notes"])
                    new_status = st.selectbox(
                        "Status",
                        firestore_db.STATUSES,
                        index=firestore_db.STATUSES.index(status),
                        format_func=lambda s: STATUS_LABELS[s],
                        key=f"status_{app_['id']}",
                        label_visibility="collapsed",
                    )
                    if new_status != status:
                        firestore_db.update_status(uid, app_["id"], new_status)
                        st.rerun()
                    if st.button("Delete", key=f"delete_{app_['id']}"):
                        firestore_db.delete_application(uid, app_["id"])
                        st.rerun()


if "session" not in st.session_state:
    render_login()
else:
    render_dashboard()
