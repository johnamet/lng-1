#!/usr/bin/env python3
"""
Motia step to generate a downloadable link for a generated lesson notes file.
"""

import logging
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime, timedelta
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
MOTIA_API_BASE_URL = os.getenv("MOTIA_API_BASE_URL", "http://localhost:3000")  # Base URL for Motia API

# In-memory store for file links (replace with a database in production)
FILE_LINKS = {}

class FileLinkData(BaseModel):
    file_path: str
    subject: str

class InputModel(BaseModel):
    file_path: str
    subject: str

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
    Handle file-generated event, generate a download link, and emit file-link-generated event.

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
        file_data = FileLinkData.model_validate(validated_input)
    except Exception as e:
        context.logger.error(f"Input validation failed: {e}")
        return {
            'status': 400,
            'body': {'error': f"Invalid input format: {str(e)}"}
        }

    # Generate unique token for download link
    token = str(uuid4())
    expires_at = datetime.utcnow() + timedelta(hours=24)  # Link expires in 24 hours

    # Store link metadata
    FILE_LINKS[token] = {
        "file_path": file_data.file_path,
        "subject": file_data.subject,
        "expires_at": expires_at
    }

    # Construct download link using Motia API endpoint
    download_link = f"{MOTIA_API_BASE_URL}/download-file/{token}"

    # Emit file-link-generated event
    try:
        await context.emit({
            "topic": "file-link-generated",
            "data": {
                "download_link": download_link,
                "file_path": file_data.file_path,
                "subject": file_data.subject,
                "expires_at": expires_at.isoformat()
            }
        })
        logger.info(f"Emitted file-link-generated event for {file_data.subject}")
        return {
            'status': 200,
            'body': {'download_link': download_link}
        }
    except Exception as e:
        context.logger.error(f"Failed to emit file-link-generated event: {e}")
        return {
            'status': 500,
            'body': {'error': f"Failed to generate download link: {str(e)}"}
        }