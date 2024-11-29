from pymongo import MongoClient
from bson.objectid import ObjectId
from cerberus import Validator
import datetime
import logging
import pyotp
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
    def create_user(username, email, hashed_password, profile=None):
        profile = profile or {}
        user = {
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "profile": {
                "full_name": profile.get("full_name", ""),
                "bio": profile.get("bio", ""),
                "profilePicUrl": profile.get("profilePicUrl", ""),
                "details": profile.get("details", {})
            },
            "ui_preferences": {
                "theme": "light",
                "accessibility_options": []
            },
            "two_factor_auth": {
                "enabled": False,
                "secret_key": None,
                "backup_codes": [],
                "last_used": None
            },
            "privacy_settings": {
                "profile_visibility": "public",
                "content_visibility": "public",
                "following_list_visibility": "public"
            },
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow()
        }
        return User.collection.insert_one(user)

    @staticmethod
    def setup_2fa(user_id):
        secret = pyotp.random_base32()
        User.collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "two_factor_auth.secret_key": secret,
                    "two_factor_auth.enabled": True,
                    "updated_at": datetime.datetime.utcnow()
                }
            }
        )
        return secret

    @staticmethod
    def verify_2fa(user_id, token):
        user = User.collection.find_one({"_id": ObjectId(user_id)})
        if not user or not user["two_factor_auth"]["enabled"]:
            return False
        totp = pyotp.TOTP(user["two_factor_auth"]["secret_key"])
        return totp.verify(token)


class Session:
    collection = db["sessions"]
    
    @staticmethod
    def create_session(user_id, session_token, remember_me=False):
        expiry = datetime.datetime.utcnow() + datetime.timedelta(days=30 if remember_me else 1)
        session = {
            "user_id": ObjectId(user_id),
            "session_token": session_token,
            "expires_at": expiry,
            "created_at": datetime.datetime.utcnow()
        }
        return Session.collection.insert_one(session)

class ActivityLog:
    collection = db["activity_logs"]
    
    @staticmethod
    def log_activity(user_id, action, metadata=None):
        log = {
            "user_id": ObjectId(user_id),
            "action": action,
            "metadata": metadata or {},
            "timestamp": datetime.datetime.utcnow()
        }
        return ActivityLog.collection.insert_one(log)

class Content:
    collection = db["content"]
    
    @staticmethod
    def create_content(user_id, text, media_url="", tags=None, visibility="public"):
        content = {
            "user_id": ObjectId(user_id),
            "text": text,
            "media_url": media_url,
            "tags": tags or [],
            "visibility": visibility,
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow()
        }
        return Content.collection.insert_one(content)

class Connection:
    collection = db["connections"]
    
    @staticmethod
    def follow_user(follower_id, followed_id):
        if Connection.collection.find_one({
            "follower_id": ObjectId(follower_id),
            "followed_id": ObjectId(followed_id)
        }):
            return False
        
        connection = {
            "follower_id": ObjectId(follower_id),
            "followed_id": ObjectId(followed_id),
            "created_at": datetime.datetime.utcnow()
        }
        return Connection.collection.insert_one(connection)

class Notification:
    collection = db["notifications"]
    
    @staticmethod
    def create_notification(user_id, message, action_link=None):
        notification = {
            "user_id": ObjectId(user_id),
            "message": message,
            "action_link": action_link,
            "is_read": False,
            "created_at": datetime.datetime.utcnow()
        }
        return Notification.collection.insert_one(notification)

    @staticmethod
    def mark_as_read(notification_id):
        return Notification.collection.update_one(
            {"_id": ObjectId(notification_id)},
            {"$set": {"is_read": True}}
        )