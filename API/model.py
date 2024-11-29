from pymongo import MongoClient
from bson.objectid import ObjectId
from cerberus import Validator
import datetime
import logging

# Configuración del registro de eventos
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("model")

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["app_database"]

class User:
    collection = db["users"]

    @staticmethod
    def create_user(username, email, hashed_password, profile={}):
        try:
            schema = {
                "username": {"type": "string", "minlength": 3, "maxlength": 30},
                "email": {"type": "string", "regex": r".+@.+\..+"},
                "hashed_password": {"type": "string"},
                "profile": {"type": "dict", "default": {}}
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
            return User.collection.insert_one(user)
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise RuntimeError(f"Database operation failed: {str(e)}")

    @staticmethod
    def find_by_username(username):
        try:
            return User.collection.find_one({"username": username})
        except Exception as e:
            logger.error(f"Failed to find user by username: {str(e)}")
            raise

    @staticmethod
    def find_by_email(email):
        try:
            return User.collection.find_one({"email": email}, {"hashed_password": 0, "two_factor_auth.secret_key": 0})
        except Exception as e:
            logger.error(f"Failed to find user by email: {str(e)}")
            raise

    @staticmethod
    def update_user(user_id, updates):
        try:
            updates["updated_at"] = datetime.datetime.utcnow()
            return User.collection.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
        except Exception as e:
            logger.error(f"Failed to update user: {str(e)}")
            raise


class PasswordReset:
    collection = db["password_resets"]

    @staticmethod
    def create_request(user_id, reset_token):
        try:
            reset_request = {
                "user_id": ObjectId(user_id),
                "reset_token": reset_token,
                "expires_at": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
                "is_used": False,
            }
            return PasswordReset.collection.insert_one(reset_request)
        except Exception as e:
            logger.error(f"Failed to create password reset request: {str(e)}")
            raise

    @staticmethod
    def find_valid_request(reset_token):
        try:
            return PasswordReset.collection.find_one(
                {"reset_token": reset_token, "is_used": False, "expires_at": {"$gt": datetime.datetime.utcnow()}}
            )
        except Exception as e:
            logger.error(f"Failed to find valid password reset request: {str(e)}")
            raise

    @staticmethod
    def mark_used(reset_token):
        try:
            return PasswordReset.collection.update_one({"reset_token": reset_token}, {"$set": {"is_used": True}})
        except Exception as e:
            logger.error(f"Failed to mark password reset as used: {str(e)}")
            raise


class Session:
    collection = db["sessions"]

    @staticmethod
    def create_session(user_id, session_token):
        try:
            session = {
                "user_id": ObjectId(user_id),
                "session_token": session_token,
                "expires_at": datetime.datetime.utcnow() + datetime.timedelta(days=7),
            }
            return Session.collection.insert_one(session)
        except Exception as e:
            logger.error(f"Failed to create session: {str(e)}")
            raise

    @staticmethod
    def find_by_token(session_token):
        try:
            return Session.collection.find_one({"session_token": session_token})
        except Exception as e:
            logger.error(f"Failed to find session by token: {str(e)}")
            raise

    @staticmethod
    def delete_expired_sessions():
        try:
            return Session.collection.delete_many({"expires_at": {"$lt": datetime.datetime.utcnow()}})
        except Exception as e:
            logger.error(f"Failed to delete expired sessions: {str(e)}")
            raise


class ActivityLog:
    collection = db["activity_logs"]

    @staticmethod
    def log_action(user_id, action, metadata={}):
        try:
            log_entry = {
                "user_id": ObjectId(user_id),
                "action": action,
                "timestamp": datetime.datetime.utcnow(),
                "metadata": metadata,
            }
            return ActivityLog.collection.insert_one(log_entry)
        except Exception as e:
            logger.error(f"Failed to log action: {str(e)}")
            raise

    @staticmethod
    def get_recent_logs(user_id, limit=10, skip=0):
        try:
            return list(
                ActivityLog.collection.find({"user_id": ObjectId(user_id)})
                .sort("timestamp", -1)
                .skip(skip)
                .limit(limit)
            )
        except Exception as e:
            logger.error(f"Failed to get recent logs: {str(e)}")
            raise


class Content:
    collection = db["content"]

    @staticmethod
    def create_content(user_id, text, media_url="", tags=[], visibility="public"):
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
            return Content.collection.insert_one(content_item)
        except Exception as e:
            logger.error(f"Failed to create content: {str(e)}")
            raise

    @staticmethod
    def update_content(content_id, updates):
        try:
            updates["updated_at"] = datetime.datetime.utcnow()
            return Content.collection.update_one({"_id": ObjectId(content_id)}, {"$set": updates})
        except Exception as e:
            logger.error(f"Failed to update content: {str(e)}")
            raise

    @staticmethod
    def delete_content(content_id):
        try:
            return Content.collection.delete_one({"_id": ObjectId(content_id)})
        except Exception as e:
            logger.error(f"Failed to delete content: {str(e)}")
            raise


class Connection:
    collection = db["connections"]

    @staticmethod
    def follow_user(follower_id, followed_id):
        try:
            connection = {
                "follower_id": ObjectId(follower_id),
                "followed_id": ObjectId(followed_id),
                "timestamp": datetime.datetime.utcnow(),
            }
            return Connection.collection.insert_one(connection)
        except Exception as e:
            logger.error(f"Failed to follow user: {str(e)}")
            raise

    @staticmethod
    def unfollow_user(follower_id, followed_id):
        try:
            return Connection.collection.delete_one(
                {"follower_id": ObjectId(follower_id), "followed_id": ObjectId(followed_id)}
            )
        except Exception as e:
            logger.error(f"Failed to unfollow user: {str(e)}")
            raise


class Notification:
    collection = db["notifications"]

    @staticmethod
    def send_notification(user_id, message, action_link):
        try:
            notification = {
                "user_id": ObjectId(user_id),
                "message": message,
                "action_link": action_link,
                "created_at": datetime.datetime.utcnow(),
                "is_read": False,
            }
            return Notification.collection.insert_one(notification)
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            raise

    @staticmethod
    def get_unread_notifications(user_id):
        try:
            return list(Notification.collection.find({"user_id": ObjectId(user_id), "is_read": False}))
        except Exception as e:
            logger.error(f"Failed to retrieve unread notifications: {str(e)}")
            raise

    @staticmethod
    def mark_as_read(notification_id):
        try:
            return Notification.collection.update_one({"_id": ObjectId(notification_id)}, {"$set": {"is_read": True}})
        except Exception as e:
            logger.error(f"Failed to mark notification as read: {str(e)}")
            raise
