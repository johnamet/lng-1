#!/usr/bin/env python3
"""
Motia AI Agent for Lesson Notes Generator
"""

from typing import Any, Dict, Callable
from datetime import datetime
import time
import json
import logging
from pydantic import BaseModel


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Define a Pydantic model for request body validation
class RequestBody(BaseModel):
    subject: str

# Request modification middleware
async def request_modifier_middleware(data: Dict[str, Any], ctx: Any, next_fn: Callable):
    # Modify the request before passing it to the next middleware
    data['headers']['x-modified-by'] = 'middleware'
    data['body']['timestamp'] = int(time.time() * 1000)

    # Call the next middleware in the chain
    return await next_fn()

# Response modification middleware
async def response_modifier_middleware(data: Dict[str, Any], ctx: Any, next_fn: Callable):
    # Call the next middleware in the chain
    response = await next_fn()

    # Modify the response before returning it
    response['headers'] = {
        **response.get('headers', {}),
        'x-powered-by': 'Motia'
    }

    return response

# Error handling middleware
async def error_handling_middleware(data: Dict[str, Any], ctx: Any, next_fn: Callable):
    try:
        # Call the next middleware in the chain
        return await next_fn()
    except Exception as error:
        ctx.logger.error('Error in handler', {'error': str(error)})
        return {
            'status': 500,
            'body': {'error': 'Internal server error'}
        }

# Rate limiter middleware with state using a closure
def create_rate_limiter_middleware():
    # Closure to maintain state between requests
    requests: Dict[str, list] = {}
    limit = 100
    window_ms = 60000  # 1 minute

    async def rate_limiter_middleware(data: Dict[str, Any], ctx: Any, next_fn: Callable):
        ip = data['headers'].get('x-forwarded-for', ['unknown-ip'])
        ip_str = ip[0] if isinstance(ip, list) else ip

        now = int(time.time() * 1000)
        if ip_str not in requests:
            requests[ip_str] = []

        # Remove old requests outside the time window
        requests[ip_str] = [t for t in requests[ip_str] if now - t < window_ms]

        if len(requests[ip_str]) >= limit:
            return {
                'status': 429,
                'body': {'error': 'Too many requests, please try again later'}
            }

        # Add current request
        requests[ip_str].append(now)

        return await next_fn()

    return rate_limiter_middleware

config = {
    'type': 'api',
    'name': 'Lesson Notes Generator',
    'description': 'Generates lesson notes customized for Morning Star School',
    'path': '/generate-note',
    'method': 'POST',
    'emits': ['generate-note'],
    'flows': ['default'],
    'bodySchema': RequestBody.model_json_schema(),
}

async def handler(req, context):
    # Validate request body
    try:
        # Access req.body as a SimpleNamespace attribute
        body_data = req.body
        # If body_data is already a dict, use it; otherwise, assume it's a JSON string
        if isinstance(body_data, dict):
            body_json = json.dumps(body_data)
        else:
            body_json = body_data
        body = RequestBody.model_validate_json(body_json)
    except Exception as e:
        logger.error(f"Invalid request body: {e}")
        return {
            'status': 400,
            'body': {'error': f"Invalid request body: {str(e)}"}
        }

    # Extract data from request
    input_data = body.dict()
    logger.info(f"Received input data: {input_data}")


    context.logger.info('Processing input:', input_data)

    
    # Emit lesson note event
    try:
        await context.emit({
            'topic': 'generate-note',
            'data': input_data
        })
    except Exception as e:
        logger.error(f"Failed to emit event: {e}")
        # Log but don't fail the request
        pass

    return {
        'status': 200,
        'body': {'message': 'Lesson note generated successfully'},
        'headers': {'Content-Type': 'application/json'}
    }