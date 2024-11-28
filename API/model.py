from pymongo import MongoClient
from bson.objectid import ObjectId
from cerberus import Validator
import datetime

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["app_database"]

class User:
    collection = db["users"]

@staticmethod
def create_user(username, email, hashed_password, profile={}):
    try:
        user = {
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "profile": profile,
            "ui_preferences": {"theme": "light", "accessibility_options": []},
            "two_factor_auth": {"enabled": False, "secret_key": None, "last_used": None},
            "privacy_settings": {"profile_visibility": "public", "content_visibility": []},
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow()
        }
        return User.collection.insert_one(user)
    except PyMongoError as e:
        raise RuntimeError(f"Database operation failed: {str(e)}")
    
@staticmethod
def find_by_username(username):
    return User.collection.find_one({"username": username})

@staticmethod
def find_by_email(email):
    user = User.collection.find_one({"email": email}, {"hashed_password": 0, "two_factor_auth.secret_key": 0})
    return user

@staticmethod
def update_user(user_id, updates):
    updates["updated_at"] = datetime.datetime.utcnow()
    return User.collection.update_one({"_id": ObjectId(user_id)}, {"$set": updates})


class PasswordReset:
    collection = db["password_resets"]

    @staticmethod
    def create_request(user_id, reset_token):
        reset_request = {
            "user_id": ObjectId(user_id),
            "reset_token": reset_token,
            "expires_at": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            "is_used": False
        }
        return PasswordReset.collection.insert_one(reset_request)

    @staticmethod
    def find_valid_request(reset_token):
        return PasswordReset.collection.find_one(
            {"reset_token": reset_token, "is_used": False, "expires_at": {"$gt": datetime.datetime.utcnow()}}
        )

    @staticmethod
    def mark_used(reset_token):
        return PasswordReset.collection.update_one({"reset_token": reset_token}, {"$set": {"is_used": True}})


class Session:
    collection = db["sessions"]

    @staticmethod
    def create_session(user_id, session_token):
        session = {
            "user_id": ObjectId(user_id),
            "session_token": session_token,
            "expires_at": datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }
        return Session.collection.insert_one(session)

    @staticmethod
    def find_by_token(session_token):
        return Session.collection.find_one({"session_token": session_token})

    @staticmethod
    def delete_expired_sessions():
        return Session.collection.delete_many({"expires_at": {"$lt": datetime.datetime.utcnow()}})


class ActivityLog:
    collection = db["activity_logs"]

    @staticmethod
    def log_action(user_id, action, metadata={}):
        log_entry = {
            "user_id": ObjectId(user_id),
            "action": action,
            "timestamp": datetime.datetime.utcnow(),
            "metadata": metadata
        }
        return ActivityLog.collection.insert_one(log_entry)

@staticmethod
def get_recent_logs(user_id, limit=10, skip=0):
    return list(
        ActivityLog.collection.find({"user_id": ObjectId(user_id)})
        .sort("timestamp", -1)
        .skip(skip)
        .limit(limit)
    )

class Content:
    collection = db["content"]

    @staticmethod
    def create_content(user_id, text, media_url="", tags=[], visibility="public"):
        content_item = {
            "user_id": ObjectId(user_id),
            "text": text,
            "media_url": media_url,
            "tags": tags,
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow(),
            "visibility": visibility
        }
        return Content.collection.insert_one(content_item)

    @staticmethod
    def update_content(content_id, updates):
        updates["updated_at"] = datetime.datetime.utcnow()
        return Content.collection.update_one({"_id": ObjectId(content_id)}, {"$set": updates})

    @staticmethod
    def delete_content(content_id):
        return Content.collection.delete_one({"_id": ObjectId(content_id)})


class Connection:
    collection = db["connections"]

    @staticmethod
    def follow_user(follower_id, followed_id):
        connection = {
            "follower_id": ObjectId(follower_id),
            "followed_id": ObjectId(followed_id),
            "timestamp": datetime.datetime.utcnow()
        }
        return Connection.collection.insert_one(connection)

    @staticmethod
    def unfollow_user(follower_id, followed_id):
        return Connection.collection.delete_one(
            {"follower_id": ObjectId(follower_id), "followed_id": ObjectId(followed_id)}
        )


class Notification:
    collection = db["notifications"]

@staticmethod
def send_notification(user_id, message, action_link):
    notification = {
        "user_id": ObjectId(user_id),
        "message": message,
        "action_link": action_link,
        "created_at": datetime.datetime.utcnow(),
        "is_read": False
    }
    return Notification.collection.insert_one(notification)

@staticmethod
def get_unread_notifications(user_id):
    return list(Notification.collection.find({"user_id": ObjectId(user_id), "is_read": False}))

@staticmethod
def mark_as_read(notification_id):
        return Notification.collection.update_one({"_id": ObjectId(notification_id)}, {"$set": {"is_read": True}})
    
@staticmethod
def invalidate_session(session_token):
    return Session.collection.delete_one({"session_token": session_token})

@staticmethod
def invalidate_all_sessions(user_id):
    return Session.collection.delete_many({"user_id": ObjectId(user_id)})

[
    {
        "_id": ObjectId("64d11111ac78912345678911"),
        "user_id": ObjectId("64d10f12ac789123456789ab"),
        "message": "Your post has been liked",
        "action_link": "/posts/64d10f88ac789123456789ef",
        "created_at": "2024-11-23T08:00:00Z",
        "is_read": false
    },
    {
        "_id": ObjectId("64d11122ac78912345678922"),
        "user_id": ObjectId("64d10f12ac789123456789ab"),
        "message": "Messi has followed you",
        "action_link": "/profile/64d10f44ac789123456789dd",
        "created_at": "2024-11-22T20:00:00Z",
        "is_read": false
    }
]



