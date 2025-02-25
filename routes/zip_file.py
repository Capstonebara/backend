from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dotenv import load_dotenv
import os
import zipfile
from datetime import datetime
import pytz

# Load environment variables
load_dotenv()

# Get credentials from the .env file
VALID_USERNAME = os.getenv("VALID_USERNAME")
VALID_PASSWORD = os.getenv("VALID_PASSWORD")

zip_router = APIRouter()

# # Basic Authentication setup
# security = HTTPBasic()

# def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
#     if credentials.username != VALID_USERNAME or credentials.password != VALID_PASSWORD:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     return credentials.username  # Return username if authentication is successful


# @zip_router.get("/zip")
# def zip_embedded_and_download(username: str = Depends(authenticate)):
#     try:
#         # Define paths
#         base_folder = "/home/capybara/data"
#         embed_folder = os.path.join(base_folder, "embed")
#         zip_folder = os.path.join(base_folder, "zip")

#         # Ensure the embed folder exists
#         if not os.path.exists(embed_folder):
#             raise HTTPException(status_code=404, detail="Embed folder does not exist.")

#         # Ensure the zip folder exists, create if not
#         if not os.path.exists(zip_folder):
#             os.makedirs(zip_folder)

#         # Create a timestamped zip file name
#         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#         zip_file_path = os.path.join(zip_folder, f"embed_backup_{timestamp}.zip")

#         # Create the zip file
#         with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
#             for root, dirs, files in os.walk(embed_folder):
#                 for file in files:
#                     file_path = os.path.join(root, file)
#                     arcname = os.path.relpath(file_path, embed_folder)  # Relative path inside the zip
#                     zipf.write(file_path, arcname)

#         # Ensure the zip file was created
#         if not os.path.exists(zip_file_path):
#             raise HTTPException(status_code=500, detail="Failed to create the zip file.")
        
#             # Get the current time in UTC
#         utc_now = datetime.now(pytz.utc)

#         # Convert to Vietnam timezone
#         vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
#         vietnam_time = utc_now.astimezone(vietnam_tz)     

#         print("ZIP IN", vietnam_time.strftime('%Y-%m-%d %H:%M:%S'))

#         # Return the zip file as a downloadable response
#         return FileResponse(
#             zip_file_path,
#             media_type="application/zip",
#             filename=f"embed_backup_{timestamp}.zip"
#         )
#     except Exception as e:
#         # Log the exception for debugging
#         error_message = f"An error occurred: {str(e)}"
#         print(error_message)  # Log to server console (or use a proper logger)
#         raise HTTPException(status_code=500, detail=error_message)

# @zip_router.get("/zip/pics")
# def zip_pics_and_download(username: str = Depends(authenticate)):
#     try:
#         # Define paths
#         base_folder = "/home/capybara/data"
#         pics_folder = os.path.join(base_folder, "pics")
#         zip_folder = os.path.join(base_folder, "zip_pics")

#         # Ensure the pics folder exists
#         if not os.path.exists(pics_folder):
#             raise HTTPException(status_code=404, detail="Pics folder does not exist.")

#         # Ensure the zip folder exists, create if not
#         if not os.path.exists(zip_folder):
#             os.makedirs(zip_folder)

#         # Create a timestamped zip file name
#         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#         zip_file_path = os.path.join(zip_folder, f"pics_backup_{timestamp}.zip")

#         # Create the zip file
#         with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
#             for root, dirs, files in os.walk(pics_folder):
#                 for file in files:
#                     file_path = os.path.join(root, file)
#                     arcname = os.path.relpath(file_path, pics_folder)  # Relative path inside the zip
#                     zipf.write(file_path, arcname)

#         # Ensure the zip file was created
#         if not os.path.exists(zip_file_path):
#             raise HTTPException(status_code=500, detail="Failed to create the zip file.")

#         # Get the current time in UTC
#         utc_now = datetime.now(pytz.utc)

#         # Convert to Vietnam timezone
#         vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
#         vietnam_time = utc_now.astimezone(vietnam_tz)     

#         print("ZIP IN", vietnam_time.strftime('%Y-%m-%d %H:%M:%S'))

#         # Return the zip file as a downloadable response
#         return FileResponse(
#             zip_file_path,
#             media_type="application/zip",
#             filename=f"pics_backup_{timestamp}.zip"
#         )
#     except Exception as e:
#         # Log the exception for debugging
#         error_message = f"An error occurred: {str(e)}"
#         print(error_message)