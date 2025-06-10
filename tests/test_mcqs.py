import unittest
from unittest.mock import patch, MagicMock
from utils import mcqs_generator

class TestMCQsGenerator(unittest.TestCase):

    @patch('utils.mcqs_generator.qa_pipeline')
    @patch('utils.mcqs_generator.qg_pipeline')
    def test_generate_mcqs(self, mock_qg_pipeline, mock_qa_pipeline):
        # Mock the output of question generation pipeline
        mock_qg_pipeline.return_value = [
            {"generated_text": "What is AI?"},
            {"generated_text": "Explain ML."},
            {"generated_text": "Define data science."},
            {"generated_text": "What is Python?"},
            {"generated_text": "Describe deep learning."}
        ]

        # Mock the output of question answering pipeline
        def qa_side_effect(question, context):
            return {"answer": "Mocked Answer"}

        mock_qa_pipeline.side_effect = qa_side_effect

        # Sample text input
        sample_text = ("AI is the field of computer science. ML is a subset of AI. "
                       "Data science involves statistics. Python is a programming language. "
                       "Deep learning is a branch of ML.")

        # Call generate_mcqs with mocked pipelines
        mcqs = mcqs_generator.generate_mcqs(sample_text, num_questions=5)

        # Check that 5 questions were generated
        self.assertEqual(len(mcqs), 5)

        for mcq in mcqs:
            self.assertIn("question", mcq)
            self.assertIn("answer", mcq)
            self.assertIn("options", mcq)
            self.assertEqual(mcq["answer"], "Mocked Answer")
            # The options must include the correct answer
            self.assertIn("Mocked Answer", mcq["options"])
            # There should be 4 options (1 correct + 3 distractors)
            self.assertEqual(len(mcq["options"]), 4)

        # Ensure the pipelines were called
        mock_qg_pipeline.assert_called_once()
        self.assertEqual(mock_qa_pipeline.call_count, 5)


if __name__ == '__main__':
    unittest.main()
