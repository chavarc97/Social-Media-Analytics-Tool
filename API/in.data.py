from pymongo import MongoClient, ASCENDING, DESCENDING
import logging
from bson.objectid import ObjectId

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("init_db")

#connection to mongo
MONGO_URI = "mongodb://localhost:27017/app_database"
client = MongoClient(MONGO_URI)
db = client.get_database()

def create_indexes():
    try:
        # users collection
        db["users"].create_index([("email", ASCENDING)], unique=True)
        db["users"].create_index([("username", ASCENDING)], unique=True)
        logger.info("Indexes created for 'users' collection")

        # password resets
        db["password_resets"].create_index([("reset_token", ASCENDING)])
        db["password_resets"].create_index([("expires_at", ASCENDING)])
        logger.info("Indexes created for 'password_resets' collection")

        # sessions
        db["sessions"].create_index([("session_token", ASCENDING)])
        db["sessions"].create_index([("expires_at", ASCENDING)])
        logger.info("Indexes created for 'sessions' collection")

        # activity logs
        db["activity_logs"].create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)])
        logger.info("Indexes created for 'activity_logs' collection")

        # content
        db["content"].create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
        db["content"].create_index([("tags", ASCENDING)])
        logger.info("Indexes created for 'content' collection")

        # connections
        db["connections"].create_index([("follower_id", ASCENDING), ("followed_id", ASCENDING)], unique=True)
        logger.info("Indexes created for 'connections' collection")

        # notifications
        db["notifications"].create_index([("user_id", ASCENDING), ("is_read", ASCENDING)])
        logger.info("Indexes created for 'notifications' collection")

    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

def seed_data():
    try:
        # seed an admin user
        if not db["users"].find_one({"username": "admin"}):
            db["users"].insert_one({
                "username": "admin",
                "email": "admin@example.com",
                "hashed_password": "hashed_admin_password",  
                "profile": {
                    "full_name": "Admin User",
                    "bio": "Administrator account",
                    "profilePicUrl": "",
                    "details": {}
                },
                "ui_preferences": {"theme": "dark", "accessibility_options": []},
                "two_factor_auth": {"enabled": False, "secret_key": None, "last_used": None},
                "privacy_settings": {"profile_visibility": "private", "content_visibility": []},
                "created_at": datetime.datetime.utcnow(),
                "updated_at": datetime.datetime.utcnow()
            })
            logger.info("Admin user seeded into 'users' collection")

        # seed a sample content post
        if not db["content"].find_one({"text": "Welcome to the platform!"}):
            db["content"].insert_one({
                "user_id": ObjectId("000000000000000000000001"),  
                "text": "Welcome to the platform!",
                "media_url": "",
                "tags": ["welcome"],
                "created_at": datetime.datetime.utcnow(),
                "updated_at": datetime.datetime.utcnow(),
                "visibility": "public"
            })
            logger.info("Sample content seeded into 'content' collection")

    except Exception as e:
        logger.error(f"Error seeding data: {e}")

if __name__ == "__main__":
    logger.info("Initializing database...")
    create_indexes()
    seed_data()
    logger.info("Database initialization complete.")
