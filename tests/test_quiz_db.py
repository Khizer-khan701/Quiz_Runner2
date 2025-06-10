import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from utils import quiz_db

class TestQuizDB(unittest.TestCase):
    @patch('utils.quiz_db.firestore.client')
    def test_create_quiz(self, mock_client):
        mock_db = MagicMock()
        mock_client.return_value = mock_db
        mock_collection = MagicMock()
        mock_db.collection.return_value = mock_collection
        mock_collection.add.return_value = ('mock_doc_ref', None)

        teacher_id = "teacher123"
        quiz_title = "Sample Quiz"
        questions = [{"question": "Q1?", "answer": "A1", "options": ["A1", "A2"]}]
        start_time = datetime(2025, 5, 25, 10, 0, tzinfo=timezone.utc)
        end_time = datetime(2025, 5, 25, 10, 30, tzinfo=timezone.utc)

        result = quiz_db.create_quiz(teacher_id, quiz_title, questions, start_time, end_time)

        self.assertEqual(result, ('mock_doc_ref', None))
        mock_db.collection.assert_called_once_with("quizzes")
        mock_collection.add.assert_called_once()

        doc_data = mock_collection.add.call_args[0][0]
        self.assertEqual(doc_data["teacher_id"], teacher_id)
        self.assertEqual(doc_data["title"], quiz_title)
        self.assertEqual(doc_data["questions"], questions)
        self.assertEqual(doc_data["start_time"], start_time)
        self.assertEqual(doc_data["end_time"], end_time)
        self.assertEqual(doc_data["duration"], 30)
        self.assertIsInstance(doc_data["created_at"], datetime)

if __name__ == "__main__":
    unittest.main()
