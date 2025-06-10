import unittest
from unittest.mock import patch, MagicMock
from utils import auth

class TestAuthFunctions(unittest.TestCase):

    @patch('utils.auth.requests.post')
    @patch('utils.auth.db')
    def test_signup_user_success(self, mock_db, mock_post):
        # Mock the HTTP response for successful signup
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'localId': '123abc'}
        mock_post.return_value = mock_response

        # Mock Firestore doc set method
        mock_doc = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_doc

        success, message, uid = auth.signup_user('user@example.com', 'pass123', 'Test User', 'admin')

        self.assertTrue(success)
        self.assertEqual(message, "Account created successfully!")
        self.assertEqual(uid, '123abc')
        mock_post.assert_called_once()
        mock_db.collection.assert_called_once_with('users')
        mock_db.collection.return_value.document.assert_called_once_with('123abc')
        mock_doc.set.assert_called_once_with({
            'email': 'user@example.com',
            'name': 'Test User',
            'role': 'admin'
        })

    @patch('utils.auth.requests.post')
    def test_signup_user_failure(self, mock_post):
        # Mock failed signup response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'error': {'message': 'EMAIL_EXISTS'}}
        mock_post.return_value = mock_response

        success, message, uid = auth.signup_user('user@example.com', 'pass123', 'Test User', 'admin')

        self.assertFalse(success)
        self.assertEqual(message, 'EMAIL_EXISTS')
        self.assertIsNone(uid)

    @patch('utils.auth.requests.post')
    def test_login_user_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'localId': 'uid123'}
        mock_post.return_value = mock_response

        success, message, uid = auth.login_user('user@example.com', 'pass123')

        self.assertTrue(success)
        self.assertEqual(message, "Login successful")
        self.assertEqual(uid, 'uid123')

    @patch('utils.auth.requests.post')
    def test_login_user_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'error': {'message': 'INVALID_PASSWORD'}}
        mock_post.return_value = mock_response

        success, message, uid = auth.login_user('user@example.com', 'wrongpass')

        self.assertFalse(success)
        self.assertEqual(message, 'INVALID_PASSWORD')
        self.assertIsNone(uid)

    @patch('utils.auth.db')
    def test_get_user_info_exists(self, mock_db):
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {'email': 'user@example.com', 'name': 'Test User'}
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        result = auth.get_user_info('uid123')
        self.assertIsInstance(result, dict)
        self.assertEqual(result['email'], 'user@example.com')

    @patch('utils.auth.db')
    def test_get_user_info_not_exists(self, mock_db):
        mock_doc = MagicMock()
        mock_doc.exists = False
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        result = auth.get_user_info('uid123')
        self.assertIsNone(result)

    @patch('utils.auth.requests.post')
    def test_send_password_reset_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        success, message = auth.send_password_reset('user@example.com')
        self.assertTrue(success)
        self.assertEqual(message, "Password reset email sent.")

    @patch('utils.auth.requests.post')
    def test_send_password_reset_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'error': {'message': 'EMAIL_NOT_FOUND'}}
        mock_post.return_value = mock_response

        success, message = auth.send_password_reset('unknown@example.com')
        self.assertFalse(success)
        self.assertEqual(message, 'EMAIL_NOT_FOUND')


if __name__ == '__main__':
    unittest.main()
