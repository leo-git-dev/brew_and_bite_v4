# business_logic/user_management_v3.py

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.models_v3 import Base, User
import bcrypt
import os
import logging

from database.setup_v3 import DatabaseRepository


class UserManager:
    def __init__(self, db_path='brew_and_bite_v3.db'):
        # Initialize logging
        self.repo = DatabaseRepository(db_path)
        self.logger = logging.getLogger('UserManager')
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            handler = logging.FileHandler('application.log')
            formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Setup database connection
        try:
            self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            self.logger.debug("Database connected and tables created if not existing.")
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            raise e

    def initialize_gui(self):
        """Set up the main GUI layout."""
        notebook = ttk.Notebook(self)
        self.create_registration_tab(notebook)
        self.create_view_users_tab(notebook)
        self.create_update_users_tab(notebook)
        notebook.pack(expand=True, fill="both")


    def hash_password(self, password):
        """Hash a password for storing."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, hashed_password, user_password):
        """Verify a stored password against one provided by user."""
        return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def register_user(self, username, password, contact, email, registration_type,
                      role_type=None, company_name=None, company_city=None,
                      company_phone=None, company_category=None):
        """Register a new user."""
        try:
            hashed_password = self.hash_password(password)  # Encrypt the password
            user_data = (
                username, hashed_password, contact, email, registration_type,
                role_type, company_name, company_city, company_phone, company_category
            )
            self.repo.insert_user(user_data)  # Insert user into the database
            return True, "User registered successfully."
        except Exception as e:
            return False, f"Registration failed: {e}"

        """Register a new user."""
        session = self.Session()
        try:
            # Check for existing username or email
            if session.query(User).filter((User.username == username) | (User.email == email)).first():
                self.logger.warning(f"Attempt to register with existing username/email: {username}, {email}")
                return False, "Username or Email already exists."

            hashed_pw = self.hash_password(password)

            new_user = User(
                username=username,
                password=hashed_pw,
                contact=contact,
                email=email,
                registration_type=registration_type,
                role_type=role_type,
                company_name=company_name,
                company_city=company_city,
                company_phone=company_phone,
                company_category=company_category
            )
            session.add(new_user)
            session.commit()
            self.logger.info(f"User registered successfully: {username}")
            return True, "User registered successfully."
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error during registration: {e}")
            return False, f"Registration failed: {e}"
        finally:
            session.close()

    def authenticate_user(self, username, password):
        """Authenticate a user."""
        try:
            # Fetch all users from the database
            users = self.repo.fetch_all_users()

            # Search for the user with the given username
            for user in users:
                if user[1] == username:  # Assuming username is in the second column (index 1)
                    stored_hashed_password = user[2]  # Assuming password is in the third column (index 2)
                    role_type = user[6]  # Assuming role_type is in the seventh column (index 6)

                    # Verify the hashed password
                    if self.verify_password(stored_hashed_password, password):
                        # Authentication successful
                        return True, {"username": username, "role_type": role_type}

            # If no matching user or password mismatch
            return False, "Invalid username or password."
        except Exception as e:
            # Handle database or other errors
            return False, f"Authentication failed: {e}"

    def get_all_users(self):
        """Retrieve all users."""
        session = self.Session()
        try:
            users = session.query(User).all()
            self.logger.debug(f"Retrieved {len(users)} users from the database.")
            return users
        except Exception as e:
            self.logger.error(f"Error retrieving users: {e}")
            return []
        finally:
            session.close()

    def update_user(self, user_id, field, new_value):
        """Update a user's information."""
        session = self.Session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user:
                self.logger.warning(f"No user found with ID: {user_id}")
                return False, "User not found."

            # Handle password update
            if field == "password":
                new_value = self.hash_password(new_value)

            setattr(user, field, new_value)
            session.commit()
            self.logger.info(f"User ID {user_id} updated: {field} set to {new_value}")
            return True, "User updated successfully."
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error updating user: {e}")
            return False, f"Update failed: {e}"
        finally:
            session.close()

    def delete_user(self, user_id):
        """Delete a user."""
        session = self.Session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user:
                self.logger.warning(f"No user found with ID: {user_id}")
                return False, "User not found."

            session.delete(user)
            session.commit()
            self.logger.info(f"User ID {user_id} deleted successfully.")
            return True, "User deleted successfully."
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error deleting user: {e}")
            return False, f"Deletion failed: {e}"
        finally:
            session.close()
