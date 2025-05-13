# #!/usr/bin/env python3
# """
# Motia step to send webhook notifications and serve lesson notes files.
# """

# import logging
# import os
# from typing import Dict, Any
# from datetime import datetime
# from pydantic import BaseModel
# import requests
# from dotenv import load_dotenv

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger(__name__)

# # Load environment variables
# load_dotenv()
# WEBHOOK_URL = os.getenv("WEBHOOK_URL", "http://example.com/webhook")  # User-provided webhook URL
# MOTIA_API_BASE_URL = os.getenv("MOTIA_API_BASE_URL", "http://localhost:3000")  # Base URL for Motia API


# class FileLinkData(BaseModel):
#     download_link: str
#     file_path: str
#     subject: str
#     expires_at: str

# class InputModel(BaseModel):
#     download_link: str
#     file_path: str
#     subject: str
#     expires_at: str

# # Motia configuration
# config = {
#     "type": "event",
#     "name": "Webhook Notifier",
#     "description": "Sends webhook notifications and serves lesson notes files",
#     "subscribes": ["file-link-generated"],
#     "emits": [],
#     "input": InputModel.model_json_schema(),
#     "flows": ["default"],
# }



# async def handler(input: Any, context: Any) -> Dict[str, Any]:
#     """
#     Handle file-link-generated event or download-file API request.

#     Args:
#         input: Input data (either file-link-generated event or download-file request).
#         context: Motia context for emitting events and logging.

#     Returns:
#         Dict[str, Any]: Response with status and result.
#     """
#     logger.info("Processing input: %s", input)

#     # Handle file-link-generated event
#     if context.flow == "default":
#         try:
#             validated_input = InputModel.model_validate(input)
#             file_data = FileLinkData(**validated_input.dict())
#         except Exception as e:
#             context.logger.error(f"Input validation failed: {e}")
#             return {
#                 'status': 400,
#                 'body': {'error': f"Invalid input format: {str(e)}"}
#             }

#         # Send webhook notification
#         payload = {
#             "subject": file_data.subject,
#             "download_link": file_data.download_link,
#             "expires_at": file_data.expires_at,
#             "message": f"Lesson notes for {file_data.subject} are ready for download."
#         }
#         try:
#             response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
#             response.raise_for_status()
#             logger.info(f"Webhook notification sent to {WEBHOOK_URL} for {file_data.subject}")
#         except requests.RequestException as e:
#             context.logger.error(f"Failed to send webhook notification: {e}")
#             return {
#                 'status': 500,
#                 'body': {'error': f"Failed to send webhook notification: {str(e)}"}
#             }

#         return {
#             'status': 200,
#             'body': {'message': 'Webhook notification sent'}
#         }

#     # Handle download-file API request
#     elif context.flow == "download":
#         token = input.get("token")
#         if not token or not isinstance(token, str):
#             context.logger.error("Missing or invalid token")
#             return {
#                 'status': 400,
#                 'body': {'error': "Missing or invalid token"}
#             }

#         link_data = FILE_LINKS.get(token)
#         if not link_data:
#             context.logger.warning(f"Invalid or expired token: {token}")
#             return {
#                 'status': 404,
#                 'body': {'error': "File not found or link expired"}
#             }

#         # Check expiration
#         expires_at = datetime.fromisoformat(link_data["expires_at"])
#         if datetime.utcnow() > expires_at:
#             context.logger.warning(f"Expired token: {token}")
#             del FILE_LINKS[token]
#             return {
#                 'status': 403,
#                 'body': {'error': "Download link has expired"}
#             }

#         file_path = link_data["file_path"]
#         if not os.path.exists(file_path):
#             context.logger.error(f"File not found: {file_path}")
#             return {
#                 'status': 404,
#                 'body': {'error': "File not found"}
#             }

#         try:
#             # Serve file as a response
#             return {
#                 'status': 200,
#                 'body': {
#                     'file_path': file_path,
#                     'filename': os.path.basename(file_path),
#                     'mimetype': "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
#                 },
#                 'headers': {
#                     'Content-Disposition': f'attachment; filename="{os.path.basename(file_path)}"'
#                 }
#             }
#         except Exception as e:
#             context.logger.error(f"Error serving file {file_path}: {e}")
#             return {
#                 'status': 500,
#                 'body': {'error': f"Error serving file: {str(e)}"}
#             }