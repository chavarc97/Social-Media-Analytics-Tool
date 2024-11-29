from flask import Flask, jsonify, request
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, OperationFailure
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

app = Flask(__name__)

class Config:
    MONGO_URI = 'mongodb://localhost:27017/app_database'
    JWT_SECRET_KEY = 'your-secret-key'
    SESSION_LIFETIME = 86400  # 24 hours
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    TESTING = True
    MONGO_URI = 'mongodb://localhost:27017/test_database'

# Setup logging
def setup_logging():
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler = RotatingFileHandler(
        'app.log', maxBytes=1024*1024, backupCount=10
    )
    file_handler.setFormatter(formatter)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

# Initialize MongoDB
def init_mongodb():
    try:
        client = MongoClient(app.config['MONGO_URI'])
        db = client.get_database()
        
        # Create indexes
        db.users.create_index([("username", ASCENDING)], unique=True)
        db.users.create_index([("email", ASCENDING)], unique=True)
        db.sessions.create_index([("session_token", ASCENDING)], unique=True)
        db.sessions.create_index([("expires_at", ASCENDING)])
        db.content.create_index([("text", "text"), ("tags", "text")])
        
        app.logger.info("Connected to MongoDB successfully")
        return db
    except ConnectionFailure as e:
        app.logger.error(f"MongoDB connection failed: {e}")
        raise
    except OperationFailure as e:
        app.logger.error(f"MongoDB operation failed: {e}")
        raise

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Not found",
        "message": "Resource not found"
    }), 404

@app.errorhandler(500)
def server_error(error):
    app.logger.error(f"Server error: {error}")
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

# Health check endpoint
@app.route('/health')
def health_check():
    try:
        app.db.command('ping')
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow()
        })
    except Exception as e:
        app.logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 500

def create_app(config_class=DevelopmentConfig):
    app.config.from_object(config_class)
    setup_logging()
    app.db = init_mongodb()
    
    from routes import routes
    app.register_blueprint(routes)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001)