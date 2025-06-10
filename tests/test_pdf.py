import unittest
from unittest.mock import MagicMock, patch
from utils import pdf_utils  # your utils/pdf_utils.py file

class TestPdfUtils(unittest.TestCase):

    @patch('fitz.open')
    def test_extract_text_from_pdf(self, mock_fitz_open):
        # Mock the PDF document and pages
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "Page 1 text. "
        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "Page 2 text."

        mock_doc = MagicMock()
        mock_doc.__enter__.return_value = [mock_page1, mock_page2]  # context manager returns list of pages

        mock_fitz_open.return_value = mock_doc

        # Mock uploaded_file with read method returning bytes
        mock_file = MagicMock()
        mock_file.read.return_value = b"%PDF-1.4 fake pdf content"

        result = pdf_utils.extract_text_from_pdf(mock_file)

        # Check if text is concatenated from both pages
        self.assertEqual(result, "Page 1 text. Page 2 text.")

        # Verify fitz.open called with stream=bytes and filetype='pdf'
        mock_fitz_open.assert_called_once_with(stream=mock_file.read.return_value, filetype="pdf")

if __name__ == "__main__":
    unittest.main()
