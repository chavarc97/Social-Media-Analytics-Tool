from pymongo import MongoClient
from bson.objectid import ObjectId
from cerberus import Validator
import datetime
import logging
import os

# Logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("model")

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["app_database"]

class User:
    """Handles user-related MongoDB operations."""

    collection = db["users"]

    @staticmethod
    def create_user(username, email, hashed_password, profile={}):
        """
        Create a new user in the database.
        """
        try:
            schema = {
                "username": {"type": "string", "minlength": 3, "maxlength": 30},
                "email": {"type": "string", "regex": r".+@.+\..+"},
                "hashed_password": {"type": "string"},
                "profile": {"type": "dict", "default": {}},
            }
            validator = Validator(schema)
            user = {
                "username": username,
                "email": email,
                "hashed_password": hashed_password,
                "profile": profile,
                "ui_preferences": {"theme": "light", "accessibility_options": []},
                "two_factor_auth": {"enabled": False, "secret_key": None, "last_used": None},
                "privacy_settings": {"profile_visibility": "public", "content_visibility": []},
                "created_at": datetime.datetime.utcnow(),
                "updated_at": datetime.datetime.utcnow(),
            }
            if not validator.validate(user):
                raise ValueError(f"Invalid user data: {validator.errors}")
            result = User.collection.insert_one(user)
            logger.info(f"User created with ID: {result.inserted_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise RuntimeError(f"Database operation failed: {str(e)}")

    @staticmethod
    def find_user(query):
        """
        Find a user based on a query (e.g., username or email).
        """
        try:
            return User.collection.find_one(query)
        except Exception as e:
            logger.error(f"Failed to find user: {str(e)}")
            raise

    @staticmethod
    def update_user(user_id, updates):
        """
        Update a user's details.
        """
        try:
            updates["updated_at"] = datetime.datetime.utcnow()
            result = User.collection.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
            logger.info(f"User updated: {user_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to update user: {str(e)}")
            raise

    @staticmethod
    def delete_user(user_id):
        """
        Delete a user from the database.
        """
        try:
            result = User.collection.delete_one({"_id": ObjectId(user_id)})
            logger.info(f"User deleted: {user_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to delete user: {str(e)}")
            raise


class PasswordReset:
    """Handles password reset operations."""

    collection = db["password_resets"]

    @staticmethod
    def create_request(user_id, reset_token):
        """
        Create a new password reset request.
        """
        try:
            reset_request = {
                "user_id": ObjectId(user_id),
                "reset_token": reset_token,
                "expires_at": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
                "is_used": False,
            }
            result = PasswordReset.collection.insert_one(reset_request)
            logger.info(f"Password reset request created for user: {user_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to create password reset request: {str(e)}")
            raise


class Content:
    """Handles user-generated content operations."""

    collection = db["content"]

    @staticmethod
    def create_content(user_id, text, media_url="", tags=[], visibility="public"):
        """
        Create a content entry.
        """
        try:
            content_item = {
                "user_id": ObjectId(user_id),
                "text": text,
                "media_url": media_url,
                "tags": tags,
                "created_at": datetime.datetime.utcnow(),
                "updated_at": datetime.datetime.utcnow(),
                "visibility": visibility,
            }
            result = Content.collection.insert_one(content_item)
            logger.info(f"Content created with ID: {result.inserted_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to create content: {str(e)}")
            raise

    @staticmethod
    def find_content(query):
        """
        Find content entries based on a query.
        """
        try:
            return list(Content.collection.find(query))
        except Exception as e:
            logger.error(f"Failed to find content: {str(e)}")
            raise

    @staticmethod
    def update_content(content_id, updates):
        """
        Update a content entry.
        """
        try:
            updates["updated_at"] = datetime.datetime.utcnow()
            result = Content.collection.update_one({"_id": ObjectId(content_id)}, {"$set": updates})
            logger.info(f"Content updated: {content_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to update content: {str(e)}")
            raise


class Connection:
    """Handles user connections (follow/unfollow)."""

    collection = db["connections"]

    @staticmethod
    def follow_user(follower_id, followed_id):
        """
        Create a follow relationship between users.
        """
        try:
            connection = {
                "follower_id": ObjectId(follower_id),
                "followed_id": ObjectId(followed_id),
                "timestamp": datetime.datetime.utcnow(),
            }
            result = Connection.collection.insert_one(connection)
            logger.info(f"User {follower_id} followed user {followed_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to follow user: {str(e)}")
            raise
