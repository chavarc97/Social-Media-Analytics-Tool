from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from model import User, PasswordReset, Session, ActivityLog, Content, Connection, Notification
from bson.errors import InvalidId

# Create a Blueprint for the routes
routes = Blueprint('routes', __name__)

# User registration
@routes.route('/register', methods=['POST'])
def register_user():
    data = request.json
    if User.find_by_username(data['username']) or User.find_by_email(data['email']):
        return jsonify({"error": "Username or email already exists"}), 400

    hashed_password = generate_password_hash(data['password'])
    profile = {
        "full_name": data.get("full_name", ""),
        "bio": data.get("bio", ""),
        "profilePicUrl": data.get("profilePicUrl", ""),
        "details": data.get("details", {})
    }
    user = User.create_user(data['username'], data['email'], hashed_password, profile)
    return jsonify({"message": "User registered successfully", "user_id": str(user.inserted_id)}), 201

# User login
@routes.route('/login', methods=['POST'])
def login_user():
    data = request.json
    user = User.find_by_username(data['username'])
    if user and check_password_hash(user['hashed_password'], data['password']):
        session_token = str(uuid.uuid4())
        Session.create_session(user_id=user["_id"], session_token=session_token)
        return jsonify({"message": "Login successful", "session_token": session_token}), 200

    return jsonify({"error": "Invalid username or password"}), 401

# Password reset request
@routes.route('/password-reset', methods=['POST'])
def request_password_reset():
    data = request.json
    user = User.find_by_email(data['email'])
    if user:
        reset_token = str(uuid.uuid4())
        PasswordReset.create_request(user_id=user["_id"], reset_token=reset_token)
        return jsonify({"message": "Password reset token generated", "reset_token": reset_token}), 200
    return jsonify({"error": "Email not found"}), 404

# Reset password
@routes.route('/password-reset/<token>', methods=['POST'])
def reset_password(token):
    data = request.json
    reset_request = PasswordReset.find_valid_request(reset_token=token)
    if reset_request:
        hashed_password = generate_password_hash(data['new_password'])
        User.update_user(reset_request["user_id"], {"hashed_password": hashed_password})
        PasswordReset.mark_used(token)
        return jsonify({"message": "Password reset successfully"}), 200
    return jsonify({"error": "Invalid or expired token"}), 400

# Create content
@routes.route('/content', methods=['POST'])
def create_content():
    data = request.json
    content = Content.create_content(
        user_id=data['user_id'],
        text=data['text'],
        media_url=data.get('media_url', ''),
        tags=data.get('tags', []),
        visibility=data.get('visibility', 'public')
    )
    return jsonify({"message": "Content created successfully", "content_id": str(content.inserted_id)}), 201

# Follow or unfollow a user
@routes.route('/follow', methods=['POST'])
def follow_user():
    data = request.json
    if data['action'] == "follow":
        Connection.follow_user(data['follower_id'], data['followed_id'])
        return jsonify({"message": "Followed successfully"}), 201
    elif data['action'] == "unfollow":
        Connection.unfollow_user(data['follower_id'], data['followed_id'])
        return jsonify({"message": "Unfollowed successfully"}), 200
    return jsonify({"error": "Invalid action"}), 400

# Get unread notifications
@routes.route('/notifications/unread/<user_id>', methods=['GET'])
def get_unread_notifications(user_id):
    notifications = Notification.get_unread_notifications(user_id)
    return jsonify({"unread_notifications": notifications}), 200

# Mark notification as read
@routes.route('/notifications/read/<notification_id>', methods=['POST'])
def mark_notification_as_read(notification_id):
    Notification.mark_as_read(notification_id)
    return jsonify({"message": "Notification marked as read"}), 200

# Get recent activity logs
@routes.route('/activity/<user_id>', methods=['GET'])
def get_activity_logs(user_id):
    logs = ActivityLog.get_recent_logs(user_id, limit=10)
    return jsonify({"activity_logs": logs}), 200

#search
@routes.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    search_type = request.args.get('type', 'all')  # 'profiles', 'content', or 'all'

    if not query:
        return jsonify({"error": "Search query is required"}), 400

    results = {}
    if search_type in ['profiles', 'all']:
        profiles = User.collection.aggregate([
            {"$search": {"text": {"query": query, "path": ["username", "profile.full_name", "bio"]}}},
            {"$project": {"username": 1, "profile": 1, "score": {"$meta": "searchScore"}}},
            {"$sort": {"score": -1}},
            {"$limit": 10}
        ])
        results["profiles"] = list(profiles)

    if search_type in ['content', 'all']:
        content = Content.collection.aggregate([
            {"$search": {"text": {"query": query, "path": ["text", "tags"]}}},
            {"$project": {"text": 1, "tags": 1, "user_id": 1, "score": {"$meta": "searchScore"}}},
            {"$sort": {"score": -1}},
            {"$limit": 10}
        ])
        results["content"] = list(content)

    return jsonify(results), 200

@routes.route('/ui-preferences/<user_id>', methods=['GET', 'POST'])
def manage_ui_preferences(user_id):
    if request.method == 'GET':
        preferences = User.collection.find_one({"_id": ObjectId(user_id)}, {"ui_preferences": 1})
        return jsonify(preferences), 200

    elif request.method == 'POST':
        updates = request.json
        User.update_user(user_id, {"ui_preferences": updates})
        return jsonify({"message": "UI preferences updated"}), 200

