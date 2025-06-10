from datetime import datetime, timedelta, timezone
import streamlit as st
from utils.mcqs_generator import generate_mcqs
from utils.pdf_utils import extract_text_from_pdf
from utils.quiz_db import create_quiz

# Compatibility helper for rerun (handles older versions of Streamlit)
def rerun():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

def show_teacher_dashboard(db):
    if not st.session_state.get("logged_in") or st.session_state.get("role") != "Teacher":
        st.error("Access denied. Please log in as a Teacher.")
        return

    st.header("👩‍🏫 Teacher Dashboard")

    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "📝 Create & Publish Quiz"

    tab_labels = ["📝 Create & Publish Quiz", "📚 Registered Students", "📋 View Student Scores"]
    selected_tab_index = tab_labels.index(st.session_state.active_tab)
    tabs = st.tabs(tab_labels)

    for i, tab_label in enumerate(tab_labels):
        if tabs[i].button(f"Switch to {tab_label}", key=f"switch_{i}"):
            st.session_state.active_tab = tab_label
            rerun()

    # TAB 0: Create & Publish Quiz
    with tabs[0]:
        if st.session_state.active_tab == tab_labels[0]:
            if "quiz_state" not in st.session_state:
                st.session_state.quiz_state = {"uploaded": False, "pdf_text": None, "questions": None}
            quiz_state = st.session_state.quiz_state

            if not quiz_state["uploaded"]:
                uploaded_file = st.file_uploader("📄 Upload PDF", type="pdf", key="teacher_pdf_uploader")
                if uploaded_file:
                    quiz_state["pdf_text"] = extract_text_from_pdf(uploaded_file)
                    quiz_state["uploaded"] = True
                    st.success("✅ PDF uploaded and text extracted.")

            if quiz_state["uploaded"] and quiz_state["pdf_text"]:
                num_questions = st.slider("🧮 Number of questions", 1, 10, 5, key="teacher_num_questions")
                if st.button("🧠 Generate Questions"):
                    with st.spinner("Generating MCQs..."):
                        quiz_state["questions"] = generate_mcqs(quiz_state["pdf_text"], num_questions)
                    st.success("✅ MCQs generated!")

            if quiz_state.get("questions"):
                st.subheader("📋 Generated MCQs")
                for i, q in enumerate(quiz_state["questions"], 1):
                    st.markdown(f"**Q{i}:** {q['question']}")
                    st.markdown(f"✅ **Answer:** {q['answer']}")
                    st.markdown(f"🅾️ **Options:** {', '.join(q['options'])}")
                    st.markdown("---")

                title = st.text_input("📝 Quiz Title")
                duration = st.number_input("⏱️ Quiz Duration (in minutes)", min_value=1, max_value=180, value=10, step=1)

                if st.button("📤 Publish Quiz"):
                    if not title.strip():
                        st.error("❌ Please enter a quiz title.")
                    else:
                        try:
                            now_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
                            end_time = now_utc + timedelta(minutes=duration)
                            create_quiz(
                                teacher_id=st.session_state.uid,
                                quiz_title=title.strip(),
                                questions=quiz_state["questions"],
                                start_time=now_utc,
                                end_time=end_time,
                            )
                            st.success(f"✅ Quiz '{title}' published successfully!")
                            st.session_state.quiz_state = {"uploaded": False, "pdf_text": None, "questions": None}
                            rerun()
                        except Exception as e:
                            st.error(f"❌ Error publishing quiz: {e}")

    # TAB 1: Registered Students & Requests
    with tabs[1]:
        if st.session_state.active_tab == tab_labels[1]:
            st.subheader("📚 Registered Students")
            try:
                students_query = db.collection("users").where("teacher_id", "==", st.session_state.uid).stream()
                students = [s.to_dict() for s in students_query]
            except Exception as e:
                st.error(f"Error fetching registered students: {e}")
                students = []

            if students:
                for student in students:
                    st.write(f"👤 **Name:** {student.get('name', 'N/A')}")
                    st.write(f"   ✉️ Email: {student.get('email', 'N/A')}")
                    st.write(f"   🆔 Student ID: {student.get('uid', 'N/A')}")
                    st.markdown("---")
            else:
                st.info("No students have registered under you yet.")

            st.subheader("📥 Pending Student Requests")
            try:
                requests = db.collection("teacher_requests")\
                    .where("teacher_id", "==", st.session_state.uid)\
                    .where("status", "==", "pending").stream()
                pending_requests = list(requests)
            except Exception as e:
                st.error(f"Error fetching requests: {e}")
                pending_requests = []

            if pending_requests:
                for req in pending_requests:
                    req_data = req.to_dict()
                    student_id = req_data["student_id"]
                    student_doc = db.collection("users").document(student_id).get()
                    student_info = student_doc.to_dict() if student_doc.exists else {}
                    student_name = student_info.get("name", "Unknown")
                    student_email = student_info.get("email", "Unknown")

                    st.write(f"👤 {student_name} ({student_email})")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Accept", key=f"accept_{student_id}"):
                            db.collection("users").document(student_id).update({
                                "teacher_id": st.session_state.uid
                            })
                            db.collection("teacher_requests").document(req.id).update({
                                "status": "accepted"
                            })
                            st.success(f"Accepted {student_name}")
                            rerun()

                    with col2:
                        if st.button("❌ Reject", key=f"reject_{student_id}"):
                            db.collection("teacher_requests").document(req.id).update({
                                "status": "rejected"
                            })
                            st.info(f"Rejected {student_name}")
                            rerun()
            else:
                st.info("No pending student requests.")

    # TAB 2: View Student Scores & Manage Quizzes
    with tabs[2]:
        if st.session_state.active_tab == tab_labels[2]:
            st.header("📋 View Student Scores")
            try:
                quizzes = list(db.collection("quizzes").where("teacher_id", "==", st.session_state.uid).stream())
            except Exception as e:
                st.error(f"Error fetching quizzes: {e}")
                quizzes = []

            if quizzes:
                quiz_list = [(quiz.id, quiz.to_dict().get("title", "Untitled")) for quiz in quizzes]
                quiz_ids, quiz_titles = zip(*quiz_list)
                selected_quiz_title = st.selectbox("Select a quiz to view student scores", quiz_titles)
                selected_quiz_id = quiz_ids[quiz_titles.index(selected_quiz_title)]

                try:
                    submissions = list(db.collection("student_results").where("quiz_id", "==", selected_quiz_id).stream())
                except Exception as e:
                    st.error(f"Error fetching student submissions: {e}")
                    submissions = []

                if submissions:
                    st.subheader(f"Scores for '{selected_quiz_title}'")
                    for res in submissions:
                        res_dict = res.to_dict()
                        student_id = res_dict.get("student_id")
                        score = res_dict.get("score")
                        submitted_at = res_dict.get("submitted_at")
                        try:
                            submitted_at = submitted_at.strftime("%Y-%m-%d")
                        except Exception:
                            submitted_at = str(submitted_at)[:10]

                        student_doc = db.collection("users").document(student_id).get()
                        student_name = student_doc.to_dict().get("name") if student_doc.exists else student_id
                        st.write(f"👤 **{student_name}** — Score: {int(score)} — Submitted: {submitted_at}")

                    st.info("You cannot delete this quiz because students have submitted it.")
                else:
                    if st.button(f"❌ Delete Quiz: {selected_quiz_title}", key=f"del_{selected_quiz_id}"):
                        try:
                            db.collection("quizzes").document(selected_quiz_id).delete()
                            st.success(f"Quiz '{selected_quiz_title}' deleted.")
                            rerun()
                        except Exception as e:
                            st.error(f"Error deleting quiz: {e}")
            else:
                st.info("You haven't published any quizzes yet.")
