import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch
from utils.mcqs_generator import generate_mcqs

class TestMCQGeneration(unittest.TestCase):
    def setUp(self):
        self.sample_text = (
            "Photosynthesis is the process used by plants to convert sunlight into energy. "
            "This process primarily occurs in the chloroplasts of plant cells using chlorophyll. "
            "Carbon dioxide and water are converted into glucose and oxygen."
        )

    @patch("utils.mcqs_generator.call_question_generation_pipeline")
    @patch("utils.mcqs_generator.call_question_answering_pipeline")
    def test_generate_mcqs_structure(self, mock_answering, mock_questioning):
        mock_questioning.return_value = [
            "What is photosynthesis?",
            "Where does photosynthesis occur?",
            "What is the role of chlorophyll?"
        ]
        mock_answering.side_effect = [
            "Photosynthesis is the process of converting sunlight into energy.",
            "In the chloroplasts of plant cells.",
            "Chlorophyll captures light energy."
        ]

        num_questions = 3
        mcqs = generate_mcqs(self.sample_text, num_questions=num_questions)

        self.assertEqual(len(mcqs), num_questions)
        for mcq in mcqs:
            self.assertIn("question", mcq)
            self.assertIn("answer", mcq)
            self.assertIn("options", mcq)
            self.assertEqual(len(mcq["options"]), 4)
            self.assertIn(mcq["answer"], mcq["options"])

if __name__ == "__main__":
    unittest.main()
