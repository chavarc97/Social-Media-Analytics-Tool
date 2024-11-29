from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from model import User, Session, ActivityLog, Content, Connection, Notification
from bson.objectid import ObjectId
from functools import wraps
import jwt
import datetime

routes = Blueprint('routes', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            session = Session.collection.find_one({"session_token": token})
            if not session or session['expires_at'] < datetime.datetime.utcnow():
                return jsonify({'message': 'Token is invalid or expired'}), 401
            return f(*args, **kwargs)
        except Exception:
            return jsonify({'message': 'Token is invalid'}), 401
    return decorated

@routes.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.collection.find_one({"$or": [
        {"username": data['username']},
        {"email": data['email']}
    ]}):
        return jsonify({"error": "Username or email already exists"}), 400

    hashed_password = generate_password_hash(data['password'])
    profile = {
        "full_name": data.get("full_name", ""),
        "bio": data.get("bio", ""),
        "profilePicUrl": data.get("profilePicUrl", ""),
        "details": data.get("details", {})
    }
    
    try:
        result = User.create_user(data['username'], data['email'], hashed_password, profile)
        ActivityLog.log_activity(result.inserted_id, "user_registered")
        return jsonify({"message": "Registration successful", "user_id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.collection.find_one({"username": data['username']})
    
    if not user or not check_password_hash(user['hashed_password'], data['password']):
        return jsonify({"error": "Invalid credentials"}), 401

    if user['two_factor_auth']['enabled']:
        if 'two_factor_token' not in data:
            return jsonify({"message": "2FA required", "requires_2fa": True}), 200
        if not User.verify_2fa(user['_id'], data['two_factor_token']):
            return jsonify({"error": "Invalid 2FA token"}), 401

    session_token = str(uuid.uuid4())
    Session.create_session(
        user['_id'],
        session_token,
        remember_me=data.get('remember_me', False)
    )
    
    ActivityLog.log_activity(user['_id'], "user_login")
    
    return jsonify({
        "message": "Login successful",
        "session_token": session_token,
        "user": {
            "id": str(user['_id']),
            "username": user['username'],
            "ui_preferences": user['ui_preferences']
        }
    }), 200

@routes.route('/2fa/setup', methods=['POST'])
@token_required
def setup_2fa():
    user_id = request.json['user_id']
    secret = User.setup_2fa(user_id)
    return jsonify({"secret": secret}), 200

@routes.route('/profile/<user_id>', methods=['GET', 'PUT'])
@token_required
def manage_profile(user_id):
    if request.method == 'GET':
        user = User.collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify({
            "profile": user['profile'],
            "privacy_settings": user['privacy_settings']
        }), 200
    
    elif request.method == 'PUT':
        updates = request.json
        try:
            User.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "profile": updates.get('profile', {}),
                    "privacy_settings": updates.get('privacy_settings', {}),
                    "updated_at": datetime.datetime.utcnow()
                }}
            )
            ActivityLog.log_activity(user_id, "profile_updated")
            return jsonify({"message": "Profile updated successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@routes.route('/content', methods=['POST'])
@token_required
def create_content():
    data = request.json
    try:
        result = Content.create_content(
            user_id=data['user_id'],
            text=data['text'],
            media_url=data.get('media_url', ''),
            tags=data.get('tags', []),
            visibility=data.get('visibility', 'public')
        )
        ActivityLog.log_activity(data['user_id'], "content_created")
        return jsonify({"message": "Content created", "content_id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    search_type = request.args.get('type', 'all')
    
    if not query:
        return jsonify({"error": "Search query is required"}), 400
        
    results = {}
    if search_type in ['profiles', 'all']:
        profiles = User.collection.find(
            {"$text": {"$search": query}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})])
        results['profiles'] = list(profiles)
        
    if search_type in ['content', 'all']:
        content = Content.collection.find(
            {
                "$text": {"$search": query},
                "visibility": "public"
            },
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})])
        results['content'] = list(content)
        
    return jsonify({"results": results}), 200

@routes.route('/notifications', methods=['GET'])
@token_required
def get_notifications():
    user_id = request.args.get('user_id')
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    
    query = {"user_id": ObjectId(user_id)}
    if unread_only:
        query["is_read"] = False
        
    notifications = list(Notification.collection.find(query).sort("created_at", -1))
    return jsonify({"notifications": notifications}), 200

@routes.route('/ui-preferences/<user_id>', methods=['PUT'])
@token_required
def update_ui_preferences(user_id):
    preferences = request.json
    try:
        User.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "ui_preferences": preferences,
                "updated_at": datetime.datetime.utcnow()
            }}
        )
        return jsonify({"message": "UI preferences updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500