from pymongo import MongoClient, ASCENDING, DESCENDING
import logging
from bson.objectid import ObjectId
import datetime

# Configuración del registro de eventos
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("init_db")

# Conexión a MongoDB
MONGO_URI = "mongodb://localhost:27017/app_database"
client = MongoClient(MONGO_URI)
db = client.get_database()

def create_indexes():
    try:
        # users collection
        db["users"].create_index([("email", ASCENDING)], unique=True)
        db["users"].create_index([("username", ASCENDING)], unique=True)
        logger.info("Indexes created for 'users' collection")

        # Otros índices...

    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        raise

def seed_data():
    try:
        # Sembrar usuario admin
        if not db["users"].find_one({"username": "admin"}):
            admin_id = db["users"].insert_one({
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
            }).inserted_id
            logger.info(f"Admin user seeded into 'users' collection with ID {admin_id}")
        else:
            logger.info("Admin user already exists")

        # Verificar usuario para contenido
        user_id = ObjectId("000000000000000000000001")
        if not db["users"].find_one({"_id": user_id}):
            logger.error(f"Cannot seed content. User with ID {user_id} does not exist.")
        else:
            if not db["content"].find_one({"text": "Welcome to the platform!"}):
                db["content"].insert_one({
                    "user_id": user_id,
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
        raise

if __name__ == "__main__":
    logger.info("Initializing database...")
    create_indexes()
    seed_data()
    logger.info("Database initialization complete.")
