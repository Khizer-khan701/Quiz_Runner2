import firebase_admin
from firebase_admin import firestore
from datetime import datetime

def create_quiz(teacher_id, quiz_title, questions, start_time, end_time):
    # Initialize Firestore client inside the function to avoid init on import
    db = firestore.client()

    quiz_doc = {
        "teacher_id": teacher_id,
        "title": quiz_title,
        "questions": questions,
        "start_time": firestore.SERVER_TIMESTAMP if start_time is None else start_time,
        "end_time": firestore.SERVER_TIMESTAMP if end_time is None else end_time,
        "duration": (end_time - start_time).total_seconds() // 60,
        "created_at": datetime.utcnow()
    }
    quiz_ref = db.collection("quizzes").add(quiz_doc)
    return quiz_ref
