import pytest
from unittest.mock import MagicMock, patch
import student_dashboard as sd

@patch("student_dashboard.st")
def test_show_student_dashboard_quiz_display(mock_st):
    # Setup session state
    mock_st.session_state = {
        "logged_in": True,
        "role": "Student",
        "uid": "student_123"
    }

    # Mock Firestore client
    mock_firestore_client = MagicMock()

    # Mock student document
    student_data = {"teacher_id": "teacher_abc"}
    student_doc = MagicMock()
    student_doc.to_dict.return_value = student_data
    mock_firestore_client.collection.return_value.document.return_value.get.return_value = student_doc

    # Mock quiz document
    quiz_doc = MagicMock()
    quiz_data = {
        "title": "Math Quiz",
        "teacher_id": "teacher_abc",
        "start_time": "2025-05-25T00:00:00+00:00",
        "end_time": "2099-05-25T23:59:59+00:00",
        "questions": [
            {
                "question": "2 + 2?",
                "options": ["3", "4", "5"],
                "answer": "4"
            }
        ]
    }
    quiz_doc.id = "quiz123"
    quiz_doc.to_dict.return_value = quiz_data
    mock_firestore_client.collection.return_value.where.return_value.stream.side_effect = [
        [quiz_doc],  # quizzes
        []           # student_results
    ]

    # Mock form submission handling
    mock_st.form = MagicMock()
    mock_form_context = MagicMock()
    mock_st.form.return_value.__enter__.return_value = mock_form_context
    mock_form_context.form_submit_button.return_value = False  # No submit action

    # Mock display functions to avoid real UI rendering
    mock_st.header = MagicMock()
    mock_st.subheader = MagicMock()
    mock_st.write = MagicMock()
    mock_st.radio = MagicMock(return_value="4")
    mock_st.success = MagicMock()
    mock_st.button = MagicMock(return_value=False)
    mock_st.info = MagicMock()
    mock_st.warning = MagicMock()
    mock_st.experimental_rerun = MagicMock()

    # Run dashboard logic
    sd.show_student_dashboard(db=mock_firestore_client)

    # Assert the dashboard header was shown
    mock_st.header.assert_called_with("🎓 Student Dashboard")
