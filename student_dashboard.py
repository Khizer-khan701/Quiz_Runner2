import streamlit as st
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials, firestore
import tzlocal  # For local timezone conversion

def get_firestore_client():
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")  # adjust path as needed
        firebase_admin.initialize_app(cred)
    return firestore.client()

def show_student_dashboard(db=None):
    if db is None:
        db = get_firestore_client()

    if not st.session_state.get("logged_in") or st.session_state.get("role") != "Student":
        return

    st.header("🎓 Student Dashboard")

    # Fetch current student data
    student_doc = db.collection("users").document(st.session_state.uid).get()
    student_data = student_doc.to_dict()

    # Get current UTC time and local timezone
    now_utc = datetime.now(timezone.utc)
    local_tz = tzlocal.get_localzone()
    now_local = now_utc.astimezone(local_tz)

    # Fetch quizzes of the assigned teacher
    quizzes = db.collection("quizzes").where("teacher_id", "==", student_data.get("teacher_id")).stream()

    # Fetch quizzes already submitted by this student
    submitted_quiz_ids = {
        res.to_dict().get("quiz_id")
        for res in db.collection("student_results")
                     .where("student_id", "==", st.session_state.uid)
                     .stream()
    }

    quiz_available = False
    expired_quiz_ids = []

    for quiz in quizzes:
        if quiz.id in submitted_quiz_ids:
            continue  # Skip quizzes already submitted

        data = quiz.to_dict()
        quiz_title = data.get("title", "Untitled Quiz")

        try:
            start_val = data["start_time"]
            end_val = data["end_time"]

            if isinstance(start_val, datetime):
                start_utc = start_val.astimezone(timezone.utc)
            else:
                start_utc = datetime.fromisoformat(start_val).replace(tzinfo=timezone.utc)

            if isinstance(end_val, datetime):
                end_utc = end_val.astimezone(timezone.utc)
            else:
                end_utc = datetime.fromisoformat(end_val).replace(tzinfo=timezone.utc)
        except Exception:
            st.warning(f"Invalid start or end time for quiz '{quiz_title}'. Skipping.")
            continue

        start_local = start_utc.astimezone(local_tz)
        end_local = end_utc.astimezone(local_tz)

        if now_local < start_local:
            st.info(f"🔒 Quiz '{quiz_title}' is locked. It will unlock at {start_local.strftime('%Y-%m-%d %H:%M %Z')}.")
        elif start_local <= now_local <= end_local:
            quiz_available = True
            st.subheader(f"Quiz: {quiz_title}")
            st.write(f"Available until: {end_local.strftime('%Y-%m-%d %H:%M %Z')}")

            if st.session_state.get("active_quiz_id") == quiz.id:
                with st.form(f"quiz_form_{quiz.id}"):
                    answers = {}
                    for i, q in enumerate(data["questions"], 1):
                        st.write(f"**Q{i}: {q['question']}**")
                        answers[q["question"]] = st.radio(
                            label="Choose:", options=q["options"], key=f"{quiz.id}_{i}"
                        )
                    if st.form_submit_button("Submit"):
                        correct = sum(
                            1 for q in data["questions"] if answers[q["question"]] == q["answer"]
                        )
                        total = len(data["questions"])
                        score = round((correct / total) * 100, 2)
                        db.collection("student_results").add({
                            "student_id": st.session_state.uid,
                            "quiz_id": quiz.id,
                            "quiz_title": quiz_title,
                            "score": score,
                            "submitted_at": datetime.now(timezone.utc).isoformat()
                        })
                        st.success("✅ Quiz submitted successfully!")
                        st.session_state.active_quiz_id = None
                        st.rerun()
            else:
                if st.button(f"📝 Attempt Quiz: {quiz_title}", key=f"btn_{quiz.id}"):
                    st.session_state.active_quiz_id = quiz.id
                    st.rerun()
        else:
            st.warning(f"⏰ Quiz '{quiz_title}' has expired.")
            expired_quiz_ids.append(quiz.id)
            if st.session_state.get("active_quiz_id") == quiz.id:
                st.session_state.active_quiz_id = None
                st.rerun()

    if not quiz_available:
        st.info("No quizzes are currently available to attempt.")

    if expired_quiz_ids:
        if st.button("🗑️ Clear Expired Quizzes"):
            for qid in expired_quiz_ids:
                db.collection("quizzes").document(qid).delete()
            st.success("✅ Expired quizzes deleted.")
            st.rerun()

    with st.expander("📊 Your Past Quiz Scores"):
        results_query = db.collection("student_results").where("student_id", "==", st.session_state.uid).stream()
        results = [(res.id, res.to_dict()) for res in results_query]

        if results:
            for doc_id, r in results:
                quiz_title = r.get("quiz_title", "Untitled Quiz")
                submitted_at = r.get("submitted_at", "")[:10]
                st.write(f"**{quiz_title}** — Score: {r['score']}% — Submitted: {submitted_at}")

            if st.button("🗑️ Delete All Records"):
                for doc_id, _ in results:
                    db.collection("student_results").document(doc_id).delete()
                st.success("✅ All past quiz records deleted.")
                st.rerun()
        else:
            st.info("You have not attempted any quizzes yet.")

    # 🔻 Teacher Registration Section (Dropdown at Bottom)
    st.subheader("📚 Register Under a Teacher")

    # Fetch all teachers
    teachers_query = db.collection("users").where("role", "==", "Teacher").stream()
    teacher_list = [(t.id, t.to_dict().get("name", "Unnamed")) for t in teachers_query]

    # Fetch pending requests
    pending_requests = {
        req.to_dict()["teacher_id"]
        for req in db.collection("teacher_requests")
                     .where("student_id", "==", st.session_state.uid)
                     .where("status", "==", "pending")
                     .stream()
    }

    # Label each teacher appropriately
    teacher_display_list = []
    teacher_id_map = {}

    for tid, tname in teacher_list:
        if tid == student_data.get("teacher_id") or tid in pending_requests:
            display = f"{tname} ✅ Registered"
        else:
            display = tname
        teacher_display_list.append(display)
        teacher_id_map[display] = tid

    selected_display = st.selectbox("Select a teacher to register under:", teacher_display_list)

    selected_tid = teacher_id_map[selected_display]

    if selected_tid != student_data.get("teacher_id") and selected_tid not in pending_requests:
        if st.button("Send Registration Request"):
            db.collection("teacher_requests").add({
                "student_id": st.session_state.uid,
                "teacher_id": selected_tid,
                "status": "pending",
                "timestamp": datetime.now(timezone.utc)
            })
            st.success("✅ Registration request sent.")
            st.rerun()

if __name__ == "__main__":
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = True
    if "role" not in st.session_state:
        st.session_state.role = "Student"
    if "uid" not in st.session_state:
        st.session_state.uid = "student_123"

    show_student_dashboard()
