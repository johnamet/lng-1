#!usr/bin/env python3
import logging
import os
import uuid
from flask import Flask, jsonify, request, send_file, make_response
from flask_cors import CORS
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import Blueprint
import redis
import redis.exceptions
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)

# Flask app configuration
app = Flask(__name__, static_folder=None)


# API blueprint
api_blueprint = Blueprint('LNG-FILE-SERVER', __name__, url_prefix='/lng/v1')


CORS(app, resources={r"/lng/v1/*": {"origins": "http://localhost:3001"}})
Talisman(app, content_security_policy={
    'default-src': "'self'",
    'script-src': "'self'",
    'style-src': "'self' 'unsafe-inline'",
})

# Rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per minute"],
    storage_uri=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/{os.getenv('REDIS_DB', 0)}",
    storage_options={"password": os.getenv("REDIS_PASSWORD", None)}
)

# Configuration
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "generated_files")
ALLOWED_EXTENSIONS = {'docx'}
REDIS_EXPIRE_SECONDS = 86400  # 24 hours

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Redis connection with pooling
redis_pool = redis.ConnectionPool(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD", None),
    db=int(os.getenv("REDIS_DB", 0)),
    decode_responses=True,
    max_connections=10
)
redis_client = redis.Redis(connection_pool=redis_pool)

# Helper functions
def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_token(token):
    """Validate token format (UUID)."""
    try:
        uuid.UUID(token)
        return True
    except ValueError:
        return False

def sanitize_filepath(filepath):
    """Sanitize file path to prevent traversal attacks."""
    filepath = secure_filename(os.path.basename(filepath))
    return os.path.join(UPLOAD_FOLDER, filepath)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {request.url}")
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

# Routes
@api_blueprint.route('/files', methods=['GET'])
@limiter.limit("10 per second")
def list_files():
    """List available files in the upload folder."""
    try:
        files = [f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]
        logger.info(f"Listed {len(files)} files")
        return jsonify({"files": files})
    except OSError as e:
        logger.error(f"Failed to list files: {e}")
        return jsonify({"error": "Failed to list files"}), 500

@api_blueprint.route('/files/<token>', methods=['GET'])
@limiter.limit("10 per second")
def serve_file(token):
    """Serve a file based on a Redis token."""
    if not validate_token(token):
        logger.warning(f"Invalid token format: {token}")
        return jsonify({"error": "Invalid token format"}), 400

    redis_key = f"file_link:{token}"
    try:
        link_data = redis_client.hgetall(redis_key)
        if not link_data or 'file_path' not in link_data:
            logger.warning(f"No metadata found for token: {token}")
            return jsonify({"error": "File metadata not found"}), 404

        file_path = sanitize_filepath(link_data['file_path'])
        if not os.path.exists(file_path):
            logger.warning(f"File not found at path: {file_path}")
            return jsonify({"error": "File not found"}), 404

        logger.info(f"Serving file for token: {token}")
        return send_file(file_path, as_attachment=True)
    except redis.exceptions.RedisError as e:
        logger.error(f"Redis error for token {token}: {e}")
        return jsonify({"error": "Failed to retrieve file metadata"}), 500

app.register_blueprint(api_blueprint)

if __name__ == '__main__':
    FILE_SERVER_HOST = os.getenv("FILE_SERVER_HOST", "0.0.0.0")
    FILE_SERVER_PORT = int(os.getenv("FILE_SERVER_PORT", 3000))
    app.run(
        host=FILE_SERVER_HOST,
        port=FILE_SERVER_PORT,
        debug=os.getenv("DEBUG", "false").lower() == "true"
    )