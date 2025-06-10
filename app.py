import streamlit as st
st.set_page_config(page_title="Quiz Runner", layout="centered")

from datetime import datetime
from google.api_core.exceptions import ServiceUnavailable

# ✅ Centralized Firebase setup
from firebaseConfig import db

# Utility modules
from utils.auth import signup_user, login_user, get_user_info, send_password_reset

# ✅ Safe Firestore call wrapper
def safe_get_user_info(uid):
    try:
        doc = db.collection('users').document(uid).get()
        if doc.exists:
            return doc.to_dict()
        else:
            return None
    except ServiceUnavailable as e:
        st.error("🚫 Cannot connect to Firestore. Please check your internet connection and try again.")
        print(f"[Firestore Error] {e}")
        return None


def main():
    # ✅ Restore session state from query params
    params = st.query_params
    if 'uid' in params and 'role' in params:
        if 'logged_in' not in st.session_state or not st.session_state.logged_in:
            st.session_state.logged_in = True
            st.session_state.uid = params['uid']
            st.session_state.role = params['role']
            user = safe_get_user_info(st.session_state.uid)
            st.session_state.name = user.get("name") if user else None
    else:
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
            st.session_state.role = None
            st.session_state.name = None
            st.session_state.uid = None

    if not st.session_state.logged_in:
        st.title("📚 Quiz Runner")

        login_tab, signup_tab, reset_tab = st.tabs(["🔐 Login", "📝 Sign Up", "🔁 Reset Password"])

        with login_tab:
            st.subheader("Login")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                success, msg, uid = login_user(email, password)
                if success:
                    user = safe_get_user_info(uid)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.role = user.get("role")
                        st.session_state.name = user.get("name")
                        st.session_state.uid = uid
                        st.query_params["uid"] = uid
                        st.query_params["role"] = st.session_state.role
                        st.rerun()
                    else:
                        st.error("❌ User profile not found or Firestore error.")
                else:
                    st.error(f"❌ {msg}")

        with signup_tab:
            st.subheader("Sign Up")
            name = st.text_input("Full Name", key="signup_name")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            role = st.selectbox("Role", ["Teacher", "Student"], key="signup_role")
            if st.button("Create Account"):
                success, msg, uid = signup_user(email, password, name, role)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

        with reset_tab:
            st.subheader("Password Reset")
            email = st.text_input("Email", key="reset_email")
            if st.button("Send Reset Email"):
                success, msg = send_password_reset(email)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

        st.stop()

    # ✅ Sidebar
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.name}")
        st.markdown(f"**Role:** {st.session_state.role}")
        if st.button("Logout"):
            st.session_state.clear()
            st.query_params.clear()
            st.rerun()

    # ✅ Load Dashboards
    from teacher_dashboard import show_teacher_dashboard
    from student_dashboard import show_student_dashboard

    st.title("📚 Quiz Runner")

    if st.session_state.role == "Student":
        show_student_dashboard(db)
    elif st.session_state.role == "Teacher":
        show_teacher_dashboard(db)
    else:
        st.warning("⚠️ Unknown user role. Please contact support.")


if __name__ == "__main__":
    main()
