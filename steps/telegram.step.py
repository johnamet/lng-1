#!/usr/bin/env python3
"""
Motia step to send WhatsApp notifications for lesson notes files using Twilio.
"""

import logging
from typing import Dict, Any
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import redis
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
# Load environment variables
load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = os.getenv("REDIS_DB", 0)
BOT_TOKEN = os.getenv("BOT_TOKEN")
FILE_SERVER_URL = os.getenv('FILE_SERVER_URL', 'http://localhost:5000')


import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    response = requests.post(f"{API_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })
    return response.json()

def send_document(chat_id: str, file_path: str, caption: str = None) -> dict:
    """
    Sends a document to a Telegram chat via the Bot API.

    Args:
        chat_id (str): Telegram chat ID.
        file_path (str): Path to the file to send.
        caption (str, optional): Optional caption for the document.

    Returns:
        dict: Parsed JSON response from Telegram API.
    """
    if not os.path.exists(file_path):
        error_msg = f"File not found: {file_path}"
        logger.error(error_msg)
        return {"ok": False, "error": error_msg}

    try:
        with open(file_path, "rb") as doc:
            data = {"chat_id": chat_id}
            if caption:
                data["caption"] = caption

            response = requests.post(
                f"{API_URL}/sendDocument",
                data=data,
                files={"document": doc},
                timeout=15  # timeout to avoid hanging
            )

        if response.status_code != 200:
            logger.error(f"Telegram API returned error {response.status_code}: {response.text}")
            return {"ok": False, "error": response.text}

        return response.json()

    except requests.exceptions.RequestException as e:
        logger.exception("Network or request error while sending document")
        return {"ok": False, "error": str(e)}

    except Exception as e:
        logger.exception("Unexpected error while sending document")
        return {"ok": False, "error": str(e)}
        



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



class FileLinkData(BaseModel):
    download_link: str
    file_path: str
    subject: str
    expires_at: str

class InputModel(BaseModel):
    user_phone: str
    file_link_data: FileLinkData | Dict[str, Any]  # Accepts either a FileLinkData object or a dictionary


# Motia configuration
config = {
    "type": "event",
    "name": "Telegram Notifier",
    "description": "Sends generated file  to Telegram",
    "subscribes": ["file-link-generated"],
    "emits": [],
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
    Handle file-link-generated event, retrieve metadata from Redis, and send socket notification.

    Args:
        input: Input data containing download_link, file_path, subject, and expires_at.
        context: Motia context for logging.

    Returns:
        Dict[str, Any]: Response with status and result.
    """
    logger.info("Processing file-link-generated event: %s", input)

    # Validate input
    input_data = to_dict(input)
    try:
         validated_input = InputModel.model_validate(input_data)
         file_data = validated_input.file_link_data
    except Exception as e:
        logger.error(f"Input validation failed: {e}")
        return {
            'status': 400,
            'body': {'error': f"Invalid input format: {str(e)}"}
        }

    # Retrieve metadata from Redis
    token = file_data.download_link.split("/")[-1]  # Extract token from download_link
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

    # Verify metadata consistency
    # if (link_data.get("file_path") != file_data.file_path or
    #     link_data.get("subject") != file_data.subject or
    #     link_data.get("expires_at") != file_data.expires_at):
    #     logger.warning(f"Metadata mismatch for token: {token}")
    #     return {
    #         'status': 400,
    #         'body': {'error': "Metadata mismatch"}
    #     }
    
    

    # Send Telegram notification
    try:
        chat_id = redis_client.hgetall(f"user:{validated_input.user_phone}")["chat_id"]
        message = f"Lesson notes for {file_data.subject} are ready for download.The file will be sent to you.\n Or you can download link: {file_data.download_link}"       
        resp = send_message(chat_id, message)
        logger.info(f"Telegram message sent successfully: {resp}")
        send_document(chat_id, file_data.file_path)
        logger.info(f"Telegram notification sent successfully to chat ID: {chat_id}")
        
        return {
            'status': 200,
            'body': {'message': 'Telegram notification sent successfully'}
        }
   
    except redis.RedisError as e:
        logger.error(f"Failed to retrieve chat ID from Redis: {e}")
        return {
            'status': 500,
            'body': {'error': f"Failed to retrieve chat ID from Redis: {str(e)}"}
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            'status': 500,
            'body': {'error': f"Unexpected error: {str(e)}"}
        }
    
if __name__ == "__main__":
    import asyncio
    
    # Example usage
    input_data = {
        "user_phone": "+233551522177",
        "file_link_data": {
            "download_link": "http://example.com/download/f1355727-6e88-46bf-b2fe-a4a12bb2d584",
            "file_path": "/root/Projects/LNG-1/Basic Eight Lesson Notes Mathematics WEEK 3.docx",
            "subject": "Math",
            "expires_at": datetime.datetime.now().isoformat()
        }
    }
    context = None  # Replace with actual context if needed
    result = asyncio.run(handler(input_data, context))
    print(result)
