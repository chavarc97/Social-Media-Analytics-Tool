from flask import Flask, jsonify
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from decouple import config
from routes import routes
from logging_config import logger
from config import DevelopmentConfig

app = Flask(__name__)

app.config.from_object(DevelopmentConfig)

try:
    mongo_uri = config("MONGO_URI", default="mongodb://localhost:27017/app_database")
    app.config["MONGO_URI"] = mongo_uri
    client = MongoClient(mongo_uri)
    db = client.get_database()
    logger.info("Connected to Mongo")
except ConnectionFailure as e:
    logger.error(f"MongoDB connection failed: {e}")
    db = None
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    db = None

app.register_blueprint(routes)

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Resource not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"success": False, "error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    try:
        if db is not None:
            db.list_collection_names()  
            return jsonify({"success": True, "message": "API is running and connected to Mongo!"}), 200
        else:
            return jsonify({"success": False, "message": "API is running but MongoDB connection failed."}), 500
    except Exception:
        return jsonify({"success": False, "message": "API is running but MongoDB connection failed."}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
