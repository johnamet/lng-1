# #!/usr/bin/env python3
# """
# Motia step to send WhatsApp notifications for lesson notes files using Twilio.
# """

# import logging
# from typing import Dict, Any
# from pydantic import BaseModel
# from dotenv import load_dotenv
# import os
# import redis
# from twilio.rest import Client
# from twilio.base.exceptions import TwilioRestException

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger(__name__)

# # Load environment variables
# load_dotenv()
# TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
# TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
# TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")  # Twilio sandbox number
# WHATSAPP_TO = os.getenv("WHATSAPP_TO")  # Recipient phone number (e.g., whatsapp:+1234567890)
# REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
# REDIS_PORT = os.getenv("REDIS_PORT", 6379)
# REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
# REDIS_DB = os.getenv("REDIS_DB", 0)

# # Initialize Redis client
# try:
#     redis_client = redis.Redis(
#         host=REDIS_HOST,
#         port=int(REDIS_PORT),
#         password=REDIS_PASSWORD,
#         db=int(REDIS_DB),
#         decode_responses=True
#     )
#     redis_client.ping()
#     logger.info("Successfully connected to Redis")
# except redis.RedisError as e:
#     logger.error(f"Failed to connect to Redis: {e}")
#     raise

# # Initialize Twilio client
# try:
#     twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
#     logger.info("Successfully initialized Twilio client")
# except Exception as e:
#     logger.error(f"Failed to initialize Twilio client: {e}")
#     raise

# class FileLinkData(BaseModel):
#     download_link: str
#     file_path: str
#     subject: str
#     expires_at: str

# class InputModel(BaseModel):
#     user_phone: str
#     file_link_data: FileLinkData | Dict[str, Any]  # Accepts either a FileLinkData object or a dictionary

# # Motia configuration
# config = {
#     "type": "event",
#     "name": "WhatsApp Notifier",
#     "description": "Sends WhatsApp notifications for lesson notes files",
#     "subscribes": ["file-link-generated"],
#     "emits": [],
#     "input": InputModel.model_json_schema(),
#     "flows": ["default"]
# }

# def to_dict(obj):
#     """
#     Convert object to dict if it has __dict__ attribute
#     """
#     if hasattr(obj, '__dict__'):
#         return {k: to_dict(v) for k, v in vars(obj).items()}
#     elif isinstance(obj, dict):
#         return {k: to_dict(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [to_dict(item) for item in obj]
#     else:
#         return obj

# async def handler(input: Any, context: Any) -> Dict[str, Any]:
#     """
#     Handle file-link-generated event, retrieve metadata from Redis, and send WhatsApp notification.

#     Args:
#         input: Input data containing download_link, file_path, subject, and expires_at.
#         context: Motia context for logging.

#     Returns:
#         Dict[str, Any]: Response with status and result.
#     """
#     logger.info("Processing file-link-generated event: %s", input)

#     # Validate input
#     input_data = to_dict(input)
#     try:
#         validated_input = InputModel.model_validate(input_data)
#         file_data = validated_input.file_link_data
#     except Exception as e:
#         logger.error(f"Input validation failed: {e}")
#         return {
#             'status': 400,
#             'body': {'error': f"Invalid input format: {str(e)}"}
#         }

#     # Retrieve metadata from Redis
#     token = file_data.download_link.split("/")[-1]  # Extract token from download_link
#     redis_key = f"file_link:{token}"
#     try:
#         link_data = redis_client.hgetall(redis_key)
#         if not link_data:
#             logger.warning(f"No metadata found in Redis for token: {token}")
#             return {
#                 'status': 404,
#                 'body': {'error': "File metadata not found"}
#             }
#     except redis.RedisError as e:
#         logger.error(f"Failed to retrieve metadata from Redis for token {token}: {e}")
#         return {
#             'status': 500,
#             'body': {'error': f"Failed to retrieve file metadata: {str(e)}"}
#         }

#     # Verify metadata consistency
#     if (link_data.get("file_path") != file_data.file_path or
#         link_data.get("subject") != file_data.subject or
#         link_data.get("expires_at") != file_data.expires_at):
#         logger.warning(f"Metadata mismatch for token {token}: Redis={link_data}, Input={file_data.model_dump()}")
#         return {
#             'status': 400,
#             'body': {'error': "Metadata mismatch"}
#         }

#     # Send WhatsApp notification
#     message_body = (
#         f"📚 New lesson notes for *{file_data.subject}* are ready!\n"
#         f"Download: {file_data.download_link}\n"
#         f"Expires: {file_data.expires_at}\n"
#         f"Generated by John Ametepe Agboku. Sharing is caring! 😊\n"
#         f"Note: Please do not reply."
#         f"To support this project, please consider donating to my Momo account: +233 55 1522 177"
#     )
#     try:
#         message = twilio_client.messages.create(
#             body=message_body,
#             from_=TWILIO_WHATSAPP_FROM,
#             to= f"whatsapp:{validated_input.user_phone}",
#         )
#         logger.info(f"WhatsApp notification sent to {validated_input.user_phone} for {file_data.subject}, SID: {message.sid}")
#         return {
#             'status': 200,
#             'body': {'message': 'WhatsApp notification sent', 'message_sid': message.sid}
#         }
#     except TwilioRestException as e:
#         logger.error(f"Failed to send WhatsApp notification: {e}")
#         return {
#             'status': 500,
#             'body': {'error': f"Failed to send WhatsApp notification: {str(e)}"}
#         }