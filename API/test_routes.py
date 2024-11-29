import pytest
from .app import create_app
from model import User, Content, Session, ActivityLog
import json
from bson import ObjectId
import datetime

@pytest.fixture
def app():
    app = create_app('TestingConfig')
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    return app.db

@pytest.fixture(autouse=True)
def cleanup(db):
    yield
    db.users.delete_many({})
    db.sessions.delete_many({})
    db.content.delete_many({})
    db.activity_logs.delete_many({})

def test_user_registration(client):
    response = client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    assert response.status_code == 201
    assert b'User registered successfully' in response.data

def test_user_login(client, db):
    # Create test user
    test_user = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    }
    client.post('/register', json=test_user)
    
    # Test login
    response = client.post('/login', json={
        'username': test_user['username'],
        'password': test_user['password']
    })
    assert response.status_code == 200
    assert 'token' in response.get_json()

def test_2fa_flow(client, db):
    # Register and enable 2FA
    client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    
    auth_response = client.post('/login', json={
        'username': 'testuser',
        'password': 'testpass123'
    })
    token = auth_response.get_json()['token']
    
    enable_2fa = client.post('/2fa/enable', 
        headers={'Authorization': token}
    )
    assert enable_2fa.status_code == 200
    assert 'secret' in enable_2fa.get_json()

def test_content_creation(client, db):
    # Register and login
    client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    
    login_response = client.post('/login', json={
        'username': 'testuser',
        'password': 'testpass123'
    })
    token = login_response.get_json()['token']
    
    # Create content
    response = client.post('/content', 
        headers={'Authorization': token},
        json={
            'text': 'Test content',
            'tags': ['test']
        }
    )
    assert response.status_code == 201
    assert 'content_id' in response.get_json()

def test_search_functionality(client, db):
    # Add test data
    client.post('/register', json={
        'username': 'searchuser',
        'email': 'search@example.com',
        'password': 'testpass123'
    })
    
    # Test search
    response = client.get('/search?q=searchuser&type=users')
    assert response.status_code == 200
    results = response.get_json()['results']
    assert len(results) > 0
    assert results[0]['username'] == 'searchuser'

def test_activity_logging(client, db):
    # Register user
    client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    
    # Check activity log
    logs = list(db.activity_logs.find({'action': 'user_registration'}))
    assert len(logs) > 0
    assert logs[0]['action'] == 'user_registration'

def test_privacy_settings(client, db):
    # Setup user
    client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    
    login_response = client.post('/login', json={
        'username': 'testuser',
        'password': 'testpass123'
    })
    token = login_response.get_json()['token']
    
    # Update privacy settings
    response = client.put('/privacy-settings',
        headers={'Authorization': token},
        json={
            'profile_visibility': 'private',
            'content_visibility': 'followers'
        }
    )
    assert response.status_code == 200

    # Verify settings
    user = db.users.find_one({'username': 'testuser'})
    assert user['privacy_settings']['profile_visibility'] == 'private'