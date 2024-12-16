import unittest
from unittest.mock import patch, MagicMock
from business_logic.user_management_v3 import UserManager
from database.models_v3 import User


class TestUserManager(unittest.TestCase):

    @patch('business_logic.user_management_v3.DatabaseRepository')
    @patch('business_logic.user_management_v3.sessionmaker')
    def setUp(self, mock_sessionmaker, mock_repo):
        """Set up the UserManager and mock dependencies."""
        self.mock_session = MagicMock()
        mock_sessionmaker.return_value = self.mock_session
        self.mock_repo = mock_repo.return_value
        self.user_manager = UserManager(db_path="test.db")

    @patch('business_logic.user_management_v3.bcrypt.hashpw')
    def test_hash_password(self, mock_hashpw):
        """Test password hashing."""
        mock_hashpw.return_value = b'hashed_password'
        hashed_password = self.user_manager.hash_password("password123")
        self.assertEqual(hashed_password, "hashed_password")

    @patch('business_logic.user_management_v3.bcrypt.checkpw')
    def test_verify_password(self, mock_checkpw):
        """Test password verification."""
        mock_checkpw.return_value = True
        result = self.user_manager.verify_password("hashed_password", "password123")
        self.assertTrue(result)

    @patch('business_logic.user_management_v3.UserManager.hash_password')
    def test_register_user_success(self, mock_hash_password):
        """Test successful user registration."""
        mock_hash_password.return_value = "hashed_password"
        self.mock_repo.insert_user.return_value = None  # Simulate successful DB insertion
        success, message = self.user_manager.register_user(
            username="testuser",
            password="password123",
            contact="1234567890",
            email="test@example.com",
            registration_type="admin"
        )
        self.assertTrue(success)
        self.assertEqual(message, "User registered successfully.")

    @patch('business_logic.user_management_v3.UserManager.hash_password')
    def test_register_user_failure(self, mock_hash_password):
        """Test failed user registration."""
        mock_hash_password.return_value = "hashed_password"
        self.mock_repo.insert_user.side_effect = Exception("Database error")
        success, message = self.user_manager.register_user(
            username="testuser",
            password="password123",
            contact="1234567890",
            email="test@example.com",
            registration_type="admin"
        )
        self.assertFalse(success)
        self.assertIn("Registration failed", message)

    def test_authenticate_user_success(self):
        """Test successful user authentication."""
        self.mock_repo.fetch_all_users.return_value = [
            (1, "testuser", "hashed_password", "1234567890", "test@example.com", "admin", "admin_role")
        ]
        with patch('business_logic.user_management_v3.bcrypt.checkpw', return_value=True):
            success, user_data = self.user_manager.authenticate_user("testuser", "password123")
            self.assertTrue(success)
            self.assertEqual(user_data, {"username": "testuser", "role_type": "admin_role"})

    def test_authenticate_user_failure(self):
        """Test failed user authentication."""
        self.mock_repo.fetch_all_users.return_value = []
        success, message = self.user_manager.authenticate_user("testuser", "password123")
        self.assertFalse(success)
        self.assertEqual(message, "Invalid username or password.")

    @patch('business_logic.user_management_v3.sessionmaker')
    @patch('business_logic.user_management_v3.User')
    def test_get_all_users(self, mock_user, mock_sessionmaker):
        """Test retrieving all users."""
        # Create a mock session and query
        mock_session = MagicMock()
        mock_sessionmaker.return_value = mock_session
        mock_query = mock_session.query.return_value
        mock_query.all.return_value = [
            MagicMock(username="testuser", email="test@example.com"),
            MagicMock(username="adminuser", email="admin@example.com")
        ]

        # Inject the mocked session into UserManager
        self.user_manager.Session = mock_sessionmaker

        # Call the method
        users = self.user_manager.get_all_users()

        # Assertions
        self.assertEqual(len(users), 2)  # Check that two users are returned
        self.assertEqual(users[0].username, "testuser")
        self.assertEqual(users[1].username, "adminuser")

        # Ensure query was called
        mock_session.query.assert_called_once_with(mock_user)
        mock_query.all.assert_called_once()

    @patch('business_logic.user_management_v3.User')
    def test_update_user_success(self, mock_user):
        """Test successful user update."""
        mock_user_instance = MagicMock()
        self.mock_session.return_value.query.return_value.filter_by.return_value.first.return_value = mock_user_instance
        success, message = self.user_manager.update_user(user_id=1, field="email", new_value="new@example.com")
        self.assertTrue(success)
        self.assertEqual(message, "User updated successfully.")

    @patch('business_logic.user_management_v3.User')
    def test_update_user_not_found(self, mock_user):
        """Test updating a non-existent user."""
        self.mock_session.return_value.query.return_value.filter_by.return_value.first.return_value = None
        success, message = self.user_manager.update_user(user_id=1, field="email", new_value="new@example.com")
        self.assertFalse(success)
        self.assertEqual(message, "User not found.")

    @patch('business_logic.user_management_v3.User')
    def test_delete_user_success(self, mock_user):
        """Test successful user deletion."""
        mock_user_instance = MagicMock()
        self.mock_session.return_value.query.return_value.filter_by.return_value.first.return_value = mock_user_instance
        success, message = self.user_manager.delete_user(user_id=1)
        self.assertTrue(success)
        self.assertEqual(message, "User deleted successfully.")

    @patch('business_logic.user_management_v3.User')
    def test_delete_user_not_found(self, mock_user):
        """Test deleting a non-existent user."""
        self.mock_session.return_value.query.return_value.filter_by.return_value.first.return_value = None
        success, message = self.user_manager.delete_user(user_id=1)
        self.assertFalse(success)
        self.assertEqual(message, "User not found.")


if __name__ == "__main__":
    unittest.main()
