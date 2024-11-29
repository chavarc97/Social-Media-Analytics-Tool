# Social Media API

## Setup

1. Install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```



3. Run the server:
```bash
python app.py
```

## Testing Functional Requirements

### User Management

1. Register a new user:
```bash
curl -X POST http://localhost:5001/register \
-H "Content-Type: application/json" \
-d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "profile": {
        "full_name": "Test User",
        "bio": "Test bio",
        "profilePicUrl": "https://example.com/pic.jpg"
    }
}'
```

2. Login and save token:
```bash
TOKEN=$(curl -X POST http://localhost:5001/login \
-H "Content-Type: application/json" \
-d '{"username": "testuser", "password": "password123"}' | jq -r .token)
```

### Two-Factor Authentication

1. Enable 2FA:
```bash
curl -X POST http://localhost:5001/2fa/enable \
-H "Authorization: $TOKEN"
```

2. Login with 2FA:
```bash
curl -X POST http://localhost:5001/login \
-H "Content-Type: application/json" \
-d '{
    "username": "testuser",
    "password": "password123",
    "totp_token": "123456"
}'
```

### Password Reset

1. Request reset:
```bash
curl -X POST http://localhost:5001/password-reset \
-H "Content-Type: application/json" \
-d '{"email": "test@example.com"}'
```

2. Reset password using token:
```bash
curl -X POST http://localhost:5001/password-reset/{TOKEN} \
-H "Content-Type: application/json" \
-d '{"new_password": "newpassword123"}'
```

### UI Preferences

Update UI settings:
```bash
curl -X POST http://localhost:5001/ui-preferences/{USER_ID} \
-H "Authorization: $TOKEN" \
-d '{
    "theme": "dark",
    "accessibility_options": ["high_contrast", "large_text"]
}'
```

### Content Management

1. Create content:
```bash
curl -X POST http://localhost:5001/content \
-H "Authorization: $TOKEN" \
-d '{
    "text": "Test post",
    "media_url": "https://example.com/media.jpg",
    "tags": ["test"],
    "visibility": "public"
}'
```

### Follow/Unfollow

1. Follow user:
```bash
curl -X POST http://localhost:5001/follow \
-H "Authorization: $TOKEN" \
-d '{
    "action": "follow",
    "followed_id": "user_id_to_follow"
}'
```

### Notifications

1. Get unread notifications:
```bash
curl -X GET http://localhost:5001/notifications/unread/{USER_ID} \
-H "Authorization: $TOKEN"
```

2. Mark notification as read:
```bash
curl -X POST http://localhost:5001/notifications/read/{NOTIFICATION_ID} \
-H "Authorization: $TOKEN"
```

### Privacy Settings

Update privacy settings:
```bash
curl -X PUT http://localhost:5001/privacy-settings \
-H "Authorization: $TOKEN" \
-d '{
    "profile_visibility": "private",
    "content_visibility": "followers"
}'
```

### Search

Search for users or content:
```bash
curl -X GET "http://localhost:5001/search?q=test&type=profiles" \
-H "Authorization: $TOKEN"
```

## Running Tests

Run the test suite:
```bash
pytest test_routes.py -v
```

For coverage report:
```bash
pytest --cov=. tests/ --cov-report=term-missing
```

## Notes

- The server runs on http://localhost:5001
- All authenticated endpoints require the Authorization header with the token
- Review app.log for detailed logging information
