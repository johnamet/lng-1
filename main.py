import logging
from flask import Flask, send_file, send_from_directory, jsonify, abort, request
import os
import redis
from werkzeug.utils import secure_filename
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import Blueprint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__, static_folder=None)

# Create a blueprint with prefix /v1
api_blueprint = Blueprint('lng', __name__, url_prefix='/lng/v1')

# Register the blueprint with the app
app.register_blueprint(api_blueprint)

# Security headers
# Talisman(app, content_security_policy=None)

# Rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per minute"]
)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = os.getenv("REDIS_DB", 0)

# Initialize Redis client
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=int(REDIS_PORT),
        password=REDIS_PASSWORD,
        db=int(REDIS_DB),
        decode_responses=True
    )
    redis_client.ping()
    logger.info("Successfully connected to Redis")
except redis.RedisError as e:
    logger.error(f"Failed to connect to Redis: {e}")
    raise

# Directory to serve files from
UPLOAD_FOLDER = 'files'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/files', methods=['GET'], strict_slashes=False)
@limiter.limit("10 per second")
def index():
    """Display a list of available files"""
    files = []
    for f in os.listdir(UPLOAD_FOLDER):
        if allowed_file(f):
            files.append(f)
    return jsonify({"files": files})


@app.route('/files/<token>', methods=['GET'], strict_slashes=False)
def serve_file(token):
    """
    Retrieve and serve a file based on the provided token.
    This function looks up file metadata in Redis using the token, validates
    its existence, and serves the associated file as an attachment.
    Args:
        token (str): The unique token identifying the file metadata in Redis
    Returns:
        Union[dict, Response]: Either a Flask Response object containing the file
        if successful, or a dictionary with error status and message if unsuccessful
    Raises:
        RedisError: Handled internally, returns error dict with status 500
    Note:
        The Redis key pattern used is "file_link:{token}"
        Errors are logged with appropriate severity levels
    """
    """Display the token for a file"""
    redis_key = f"file_link:{token}"
    try:
        link_data = redis_client.hgetall(redis_key)
        if not link_data:
            logger.warning(f"No metadata found in Redis for token: {token}")
            return {
                'status': 404,
                'body': {'error': "File metadata not found"}
            }
    except redis.RedisError as e:
        logger.error(f"Failed to retrieve metadata from Redis for token {token}: {e}")
        return {
            'status': 500,
            'body': {'error': f"Failed to retrieve file metadata: {str(e)}"}
        }
    
    return send_file(link_data['file_path'], as_attachment=True)

if __name__ == '__main__':
    FILE_SERVER_HOST = os.getenv("FILE_SERVER_HOST", "0.0.0.0")
    FILE_SERVER_PORT = int(os.getenv("FILE_SERVER_PORT", 5000))
    app.run(host=FILE_SERVER_HOST, port=FILE_SERVER_PORT, debug=os.getenv("DEBUG", "false").lower() == "true")