import pytest
from app import app  
from model import User, Content

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_search_profiles(client):
    # nsert a test user
    User.collection.insert_one({
        "username": "testuser",
        "profile": {"full_name": "Test User", "bio": "Testing profile"},
        "hashed_password": "hashed_password"
    })

    #make the search request
    response = client.get('/search', query_string={"query": "test", "type": "profiles"})
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert "profiles" in data["data"]

def test_search_content(client):
    #insert a test content
    Content.collection.insert_one({
        "user_id": "1234567890abcdef12345678",
        "text": "Test content for search",
        "tags": ["test", "content"]
    })

    #make the search request
    response = client.get('/search', query_string={"query": "test", "type": "content"})
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert "content" in data["data"]

def test_search_invalid_type(client):
    response = client.get('/search', query_string={"query": "test", "type": "invalid"})
    data = response.get_json()

    assert response.status_code == 400
    assert data["success"] is False
    assert "error" in data

def test_search_missing_query(client):
    response = client.get('/search')
    data = response.get_json()

    assert response.status_code == 400
    assert data["success"] is False
    assert "error" in data
def test_get_ui_preferences(client):
    #insert a test user with UI preferences
    user_id = User.collection.insert_one({
        "username": "testuser",
        "ui_preferences": {"theme": "dark", "accessibility_options": ["large_text"]}
    }).inserted_id

    response = client.get(f'/ui-preferences/{user_id}')
    data = response.get_json()

    assert response.status_code == 200
    assert "ui_preferences" in data
    assert data["ui_preferences"]["theme"] == "dark"

def test_update_ui_preferences(client):
    #insert a test user
    user_id = User.collection.insert_one({"username": "testuser"}).inserted_id

    new_preferences = {"theme": "light", "accessibility_options": ["high_contrast"]}
    response = client.post(f'/ui-preferences/{user_id}', json=new_preferences)
    data = response.get_json()

    assert response.status_code == 200
    assert data["message"] == "UI preferences updated"

    #verify the update in the database
    updated_user = User.collection.find_one({"_id": user_id})
    assert updated_user["ui_preferences"]["theme"] == "light"

def test_follow_user(client):
    # insert test users
    follower_id = str(User.collection.insert_one({"username": "follower"}).inserted_id)
    followed_id = str(User.collection.insert_one({"username": "followed"}).inserted_id)

    response = client.post('/follow', json={"action": "follow", "follower_id": follower_id, "followed_id": followed_id})
    data = response.get_json()

    assert response.status_code == 201
    assert data["message"] == "Followed successfully"

    # verify the connection in the database
    connection = Connection.collection.find_one({"follower_id": ObjectId(follower_id), "followed_id": ObjectId(followed_id)})
    assert connection is not None

def test_unfollow_user(client):
    # insert test users
    follower_id = str(User.collection.insert_one({"username": "follower"}).inserted_id)
    followed_id = str(User.collection.insert_one({"username": "followed"}).inserted_id)

    # insert a follow connection
    Connection.collection.insert_one({"follower_id": ObjectId(follower_id), "followed_id": ObjectId(followed_id)})

    response = client.post('/follow', json={"action": "unfollow", "follower_id": follower_id, "followed_id": followed_id})
    data = response.get_json()

    assert response.status_code == 200
    assert data["message"] == "Unfollowed successfully"

    # verify the connection no longer exists in the database
    connection = Connection.collection.find_one({"follower_id": ObjectId(follower_id), "followed_id": ObjectId(followed_id)})
    assert connection is None

def test_follow_invalid_action(client):
    response = client.post('/follow', json={"action": "invalid"})
    data = response.get_json()

    assert response.status_code == 400
    assert data["error"] == "Invalid action"

def test_get_unread_notifications(client):
    # insert a test notification
    user_id = str(User.collection.insert_one({"username": "testuser"}).inserted_id)
    Notification.collection.insert_one({
        "user_id": ObjectId(user_id),
        "message": "Test Notification",
        "action_link": "/test",
        "is_read": False
    })

    response = client.get(f'/notifications/unread/{user_id}')
    data = response.get_json()

    assert response.status_code == 200
    assert "unread_notifications" in data
    assert len(data["unread_notifications"]) == 1
    assert data["unread_notifications"][0]["message"] == "Test Notification"

def test_mark_notification_as_read(client):
    # insert a test notification
    user_id = str(User.collection.insert_one({"username": "testuser"}).inserted_id)
    notification_id = Notification.collection.insert_one({
        "user_id": ObjectId(user_id),
        "message": "Test Notification",
        "action_link": "/test",
        "is_read": False
    }).inserted_id

    response = client.post(f'/notifications/read/{notification_id}')
    data = response.get_json()

    assert response.status_code == 200
    assert data["message"] == "Notification marked as read"

    #verify the notification is marked as read
    notification = Notification.collection.find_one({"_id": ObjectId(notification_id)})
    assert notification["is_read"] is True
