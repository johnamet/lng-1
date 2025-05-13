#!/usr/bin/env python3
"""
Motia step to generate a downloadable link for a generated lesson notes file, using Redis for metadata storage.
"""

import logging
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime, timedelta
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import redis
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
MOTIA_API_BASE_URL = os.getenv("MOTIA_API_BASE_URL", "http://localhost:3000")
FILE_SERVER_URL = os.getenv('FILE_SERVER_URL', 'http://localhost:5000')
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
        decode_responses=True  # Automatically decode strings
    )
    # Test connection
    redis_client.ping()
    logger.info("Successfully connected to Redis")
except redis.RedisError as e:
    logger.error(f"Failed to connect to Redis: {e}")
    raise

class FileLinkData(BaseModel):
    file_path: str
    subject: str
    expires_at: str  # ISO format string for expiration

class InputModel(BaseModel):
    file_path: str
    user_phone: str
    subject: str
    email: str

# Motia configuration
config = {
    "type": "event",
    "name": "File Link Generator",
    "description": "Generates a downloadable link for lesson notes files",
    "subscribes": ["file-generated"],
    "emits": ["file-link-generated"],
    "input": InputModel.model_json_schema(),
    "flows": ["default"]
}

def to_dict(obj):
    """
    Convert object to dict if it has __dict__ attribute
    """
    if hasattr(obj, '__dict__'):
        return {k: to_dict(v) for k, v in vars(obj).items()}
    elif isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_dict(item) for item in obj]
    else:
        return obj

async def handler(input: Any, context: Any) -> Dict[str, Any]:
    """
    Handle file-generated event, generate a download link, store metadata in Redis, and emit file-link-generated event.

    Args:
        input: Input data containing file_path and subject.
        context: Motia context for emitting events.

    Returns:
        Dict[str, Any]: Response with status and link information.
    """
    logger.info("Processing file-generated event: %s", input)

    # Validate input
    input_data = to_dict(input)
    try:
        validated_input = InputModel.model_validate(input_data)
        file_data = FileLinkData(
            file_path=validated_input.file_path,
            subject=validated_input.subject,
            expires_at=(datetime.utcnow() + timedelta(hours=24)).isoformat()
        )
    except Exception as e:
        logger.error(f"Input validation failed: {e}")
        return {
            'status': 400,
            'body': {'error': f"Invalid input format: {str(e)}"}
        }

    # Generate unique token for download link
    token = str(uuid4())

    # Store metadata in Redis
    try:
        redis_key = f"file_link:{token}"
        redis_client.hset(
            redis_key,
            mapping={
                "file_path": file_data.file_path,
                "subject": file_data.subject,
                "expires_at": file_data.expires_at
            }
        )
        # Set expiration (24 hours = 86400 seconds)
        redis_client.expire(redis_key, 86400)
        logger.debug(f"Stored metadata in Redis for token: {token}")
    except redis.RedisError as e:
        logger.error(f"Failed to store metadata in Redis: {e}")
        return {
            'status': 500,
            'body': {'error': f"Failed to store file metadata: {str(e)}"}
        }

    # Construct download link
    download_link = f"{FILE_SERVER_URL}/files/{token}"

    # Emit file-link-generated event
    try:
        await context.emit({
            "topic": "file-link-generated",
            "data": {
                "file_link_data":{"download_link": download_link,
                "file_path": file_data.file_path,
                "subject": file_data.subject,
                "expires_at": file_data.expires_at},
                'user_phone': validated_input.user_phone,
                'email': validated_input.email
            }
        })
        logger.info(f"Emitted file-link-generated event for {file_data.subject}")
        return {
            'status': 200,
            'body': {'download_link': download_link, 'user_phone': validated_input.user_phone, 'email': validated_input.email}
        }
    except Exception as e:
        logger.error(f"Failed to emit file-link-generated event: {e}")
        return {
            'status': 500,
            'body': {'error': f"Failed to generate download link: {str(e)}"}
        }