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

class UserModel:
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

class Session:
    """Handles session-related operations."""
    collection = db["sessions"]

    @staticmethod
    def create_session(user_id, session_token):
        """
        Create a new session for a user.

        Args:
            user_id (str): The ID of the user.
            session_token (str): The token for the session.

        Returns:
            ObjectId: The ID of the created session document.
        """
        try:
            session = {
                "user_id": ObjectId(user_id),
                "session_token": session_token,
                "expires_at": datetime.datetime.utcnow() + datetime.timedelta(days=7),  # 7-day session expiry
            }
            result = Session.collection.insert_one(session)
            logger.info(f"Session created for user: {user_id}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Failed to create session: {str(e)}")
            raise

    @staticmethod
    def find_session(session_token):
        """
        Find a session by its token.

        Args:
            session_token (str): The token of the session.

        Returns:
            dict: The session document if found.
        """
        try:
            return Session.collection.find_one({"session_token": session_token})
        except Exception as e:
            logger.error(f"Failed to find session: {str(e)}")
            raise

    @staticmethod
    def delete_expired_sessions():
        """
        Delete all expired sessions from the database.

        Returns:
            int: Number of sessions deleted.
        """
        try:
            result = Session.collection.delete_many({"expires_at": {"$lt": datetime.datetime.utcnow()}})
            logger.info(f"Deleted {result.deleted_count} expired sessions.")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Failed to delete expired sessions: {str(e)}")
            raise


class ActivityLog:
    """Handles user activity logs."""
    collection = db["activity_logs"]

    @staticmethod
    def log_action(user_id, action, metadata=None):
        """
        Log a user's action.

        Args:
            user_id (str): The ID of the user.
            action (str): Description of the action.
            metadata (dict, optional): Additional details about the action.

        Returns:
            ObjectId: The ID of the created log document.
        """
        try:
            log_entry = {
                "user_id": ObjectId(user_id),
                "action": action,
                "timestamp": datetime.datetime.utcnow(),
                "metadata": metadata or {},
            }
            result = ActivityLog.collection.insert_one(log_entry)
            logger.info(f"Action logged for user: {user_id}, Action: {action}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Failed to log action: {str(e)}")
            raise

    @staticmethod
    def get_recent_logs(user_id, limit=10):
        """
        Retrieve the most recent logs for a user.

        Args:
            user_id (str): The ID of the user.
            limit (int): The number of logs to retrieve.

        Returns:
            list: A list of recent activity logs.
        """
        try:
            logs = list(
                ActivityLog.collection.find({"user_id": ObjectId(user_id)})
                .sort("timestamp", -1)
                .limit(limit)
            )
            return logs
        except Exception as e:
            logger.error(f"Failed to retrieve recent logs: {str(e)}")
            raise


class Notification:
    """Handles notifications for users."""
    collection = db["notifications"]

    @staticmethod
    def send_notification(user_id, message, action_link):
        """
        Send a notification to a user.

        Args:
            user_id (str): The ID of the user.
            message (str): The notification message.
            action_link (str): A link related to the notification.

        Returns:
            ObjectId: The ID of the created notification document.
        """
        try:
            notification = {
                "user_id": ObjectId(user_id),
                "message": message,
                "action_link": action_link,
                "created_at": datetime.datetime.utcnow(),
                "is_read": False,
            }
            result = Notification.collection.insert_one(notification)
            logger.info(f"Notification sent to user: {user_id}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            raise

    @staticmethod
    def get_unread_notifications(user_id):
        """
        Retrieve all unread notifications for a user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            list: A list of unread notifications.
        """
        try:
            notifications = list(
                Notification.collection.find({"user_id": ObjectId(user_id), "is_read": False})
            )
            return notifications
        except Exception as e:
            logger.error(f"Failed to retrieve unread notifications: {str(e)}")
            raise

    @staticmethod
    def mark_as_read(notification_id):
        """
        Mark a notification as read.

        Args:
            notification_id (str): The ID of the notification.

        Returns:
            int: The number of modified documents.
        """
        try:
            result = Notification.collection.update_one(
                {"_id": ObjectId(notification_id)}, {"$set": {"is_read": True}}
            )
            logger.info(f"Notification marked as read: {notification_id}")
            return result.modified_count
        except Exception as e:
            logger.error(f"Failed to mark notification as read: {str(e)}")
            raise
