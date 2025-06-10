# 📚 Quiz Runner

**Quiz Runner** is a web-based quiz management system built with **Streamlit** and **Firebase Firestore**. It enables teachers to create quizzes using PDF input and allows students to register under teachers, attempt quizzes, and track their performance.

---

## 🚀 Features

### 👩‍🏫 For Teachers:
- Upload PDFs and auto-generate multiple choice questions (MCQs).
- Set quiz titles, schedules, and publish to students.
- Accept/reject student registration requests.
- View registered students and their scores.

### 👨‍🎓 For Students:
- Sign up and request registration under a teacher.
- View assigned quizzes and attempt them during active windows.
- Review past scores and manage quiz history.

---

## 🛠 Tech Stack

| Component     | Technology                 |
|---------------|-----------------------------|
| Frontend/UI   | [Streamlit](https://streamlit.io/) |
| Backend       | Python                      |
| Database      | [Firebase Firestore](https://firebase.google.com/docs/firestore) |
| Authentication| Firebase Auth (email/password) |
| Hosting       | Any Python-compatible host (e.g., Streamlit Cloud, Render, etc.) |
| Timezone Mgmt | [`tzlocal`](https://pypi.org/project/tzlocal/) for local time support |

---

## 📂 Project Structure

```plaintext
quiz-runner/
│
├── app.py                    # Main entry point, handles routing and login
├── teacher_dashboard.py      # Teacher dashboard with quiz and student management
├── student_dashboard.py      # Student dashboard for quiz participation
├── utils/
│   ├── auth.py               # Firebase auth functions (signup/login/reset)
│   ├── pdf_utils.py          # Extract text from uploaded PDFs
│   ├── mcqs_generator.py     # Generate MCQs from text
│   └── quiz_db.py            # Quiz data saving and retrieval from Firestore
├── requirements.txt          # Python dependencies
└── serviceAccountKey.json    # 🔐 Firebase Admin SDK credentials (DO NOT SHARE)
