from flask import Flask, jsonify
from routes import routes
from logging_config import logger  
from pymongo import MongoClient
from config import DevelopmentConfig
from decouple import config  

app = Flask(__name__)

app.config.from_object(DevelopmentConfig)

try:
    mongo_uri = config("MONGO_URI","mongodb://localhost:27017/app_database")
    app.config["MONGO_URI"] = MONGO_URI
    client = MongoClient(mongo_uri)
    db = client.get_database()
    app.logger.info("Connected to Mongo")
except Exception as e:
    app.logger.error(f"Error connecting to Mongo: {e}")
    db = None

app.register_blueprint(routes)

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "resource not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"success": False, "error": "internal server error"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"success": True, "message": "API is running!"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
