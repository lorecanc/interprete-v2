# import os
# import logging
# import requests
# import shutil
# from google.oauth2 import service_account
# from google.cloud import storage
# from dotenv import load_dotenv
# from urllib.parse import urlparse
# from bs4 import BeautifulSoup

# # Load environment variables
# load_dotenv()

# # Configure logging
# log_file_path = os.getenv("LOG_FILE_PATH")
# logging.basicConfig(
#     filename=log_file_path,
#     filemode='w',
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     level=logging.DEBUG
# )

# # Google Cloud credentials
# client_file = os.getenv('GOOGLE_API_CREDENTIALS')
# credentials = service_account.Credentials.from_service_account_file(client_file)

# # Disable SSL certificate verification
# requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# def fetch_media(url):
#     """Fetch a media file or player page from a URL, handling different content types."""
#     try:
#         response = requests.get(url, verify=False)
#         if response.status_code != 200:
#             logging.error(f"Failed to fetch media. Status code: {response.status_code}")
#             return f"Error: Failed to fetch media. Status code: {response.status_code}", None

#         content_type = response.headers.get('Content-Type', '')

#         if 'text/html' in content_type:
#             logging.info("Fetched HTML content")
#             media_link = extract_media_link(response.content)
#             if not media_link.startswith("Error"):
#                 return fetch_media(media_link)
#             return 'html', response.content, None

#         elif any(ct in content_type for ct in ['audio/', 'video/', 'image/']):
#             logging.info(f"Fetched media content of type: {content_type}")
#             file_name = get_file_name_from_url(url, response)
#             return content_type, response.content, file_name

#         else:
#             logging.error(f"Unsupported media type: {content_type}")
#             return f"Error: Unsupported media type: {content_type}", None

#     except requests.exceptions.RequestException as e:
#         logging.error(f"Error fetching media: {e}")
#         return f"Error fetching media: {e}", None

# def extract_media_link(html_content):
#     """Extract the direct media link from the player's HTML."""
#     try:
#         soup = BeautifulSoup(html_content, 'html.parser')
#         media_link = soup.find('source', {'type': 'video/mp4'})
#         if media_link and 'src' in media_link.attrs:
#             logging.info(f"Found media link: {media_link['src']}")
#             return media_link['src']
#         logging.error("Error: Could not find the media link in the player page")
#         return "Error: Could not find the media link in the player page"
#     except Exception as e:
#         logging.error(f"Error extracting media link: {e}")
#         return f"Error extracting media link: {e}"

# def get_file_name_from_url(url, response):
#     """Extract file name from URL or Content-Disposition header."""
#     parsed_url = urlparse(url)
#     file_name = os.path.basename(parsed_url.path)

#     # Check if there's a Content-Disposition header
#     if 'Content-Disposition' in response.headers:
#         content_disposition = response.headers['Content-Disposition']
#         if 'filename=' in content_disposition:
#             file_name = content_disposition.split('filename=')[1].strip('\"')

#     return file_name


# def media_upload_to_gcs(bucket_name: str, source_file_name: str, destination_blob_name: str) -> str:
#     storage_client = storage.Client(credentials=credentials)
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(destination_blob_name)
# #   blob.upload_from_filename(source_file_name) # Vecchio metodo per upload, non in chunk
#     with open(source_file_name, 'rb') as f:
#         blob.upload_from_file(f)
#     logging.info(f"File {source_file_name} uploaded to {destination_blob_name}.")
#     return f"gs://{bucket_name}/{destination_blob_name}"


# def clean_download_folder(folder_path):
#     if not os.path.exists(folder_path):
#         print(f"La cartella {folder_path} non esiste.")
#         return
    
#     for filename in os.listdir(folder_path):
#         file_path = os.path.join(folder_path, filename)
#         if os.path.isfile(file_path):
#             os.remove(file_path)
#             print(f"Il file {file_path} è stato eliminato.")
    
import os
import logging
import requests
import shutil
from google.oauth2 import service_account
from google.cloud import storage
from dotenv import load_dotenv
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Load environment variables
load_dotenv()

# Configure logging
log_file_path = os.getenv("LOG_FILE_PATH")
logging.basicConfig(
    filename=log_file_path,
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

# Google Cloud credentials
client_file = os.getenv('GOOGLE_API_CREDENTIALS')
credentials = service_account.Credentials.from_service_account_file(client_file)

# Disable SSL certificate verification
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

def fetch_media(url):
    """Fetch a media file or player page from a URL, handling different content types."""
    try:
        response = requests.get(url, verify=False, allow_redirects=True)
        if response.status_code != 200:
            logging.error(f"Failed to fetch media. Status code: {response.status_code}")
            return f"Error: Failed to fetch media. Status code: {response.status_code}", None

        content_type = response.headers.get('Content-Type', '')

        if 'text/html' in content_type:
            logging.info("Fetched HTML content")
            media_link = extract_media_link(response.content)
            if not media_link.startswith("Error"):
                return fetch_media(media_link)
            return 'html', response.content, None

        elif any(ct in content_type for ct in ['audio/', 'video/', 'image/']):
            logging.info(f"Fetched media content of type: {content_type}")
            file_name = get_file_name_from_url(url, response)
            return content_type, response.content, file_name

        else:
            logging.error(f"Unsupported media type: {content_type}")
            return f"Error: Unsupported media type: {content_type}", None

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching media: {e}")
        return f"Error fetching media: {e}", None

def extract_media_link(html_content):
    """Extract the direct media link from the player's HTML."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        media_link = soup.find('source', {'type': 'video/mp4'})
        if media_link and 'src' in media_link.attrs:
            logging.info(f"Found media link: {media_link['src']}")
            return media_link['src']
        logging.error("Error: Could not find the media link in the player page")
        return "Error: Could not find the media link in the player page"
    except Exception as e:
        logging.error(f"Error extracting media link: {e}")
        return f"Error extracting media link: {e}"

def get_file_name_from_url(url, response):
    """Extract file name from URL or Content-Disposition header."""
    parsed_url = urlparse(url)
    file_name = os.path.basename(parsed_url.path)

    # Check if there's a Content-Disposition header
    if 'Content-Disposition' in response.headers:
        content_disposition = response.headers['Content-Disposition']
        if 'filename=' in content_disposition:
            file_name = content_disposition.split('filename=')[1].strip('\"')

    return file_name

def file_exists_in_bucket(bucket_name, file_name):
    """Check if a file exists in the Google Cloud Storage bucket."""
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    return blob.exists()

def get_content_type_from_bucket(bucket_name, file_name):
    """Get the content type of a file from the Google Cloud Storage bucket."""
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.reload()  # Reload the blob to get the latest metadata
    return blob.content_type

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10), retry=retry_if_exception_type(Exception))
def media_upload_to_gcs(bucket_name, file_path, file_name, content_type):
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_path, content_type=content_type)
    return f"gs://{bucket_name}/{file_name}"

def clean_download_folder(folder_path):
    """Clean the download folder."""
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            print(f"Il file {file_path} è stato eliminato.")
        except Exception as e:
            logging.error(f"Failed to delete {file_path}. Reason: {e}")

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10), retry=retry_if_exception_type(Exception))
def output_upload_to_gcs(output_bucket_name, file_path, file_name, content_type):
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(output_bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_path, content_type=content_type)
    return f"gs://{output_bucket_name}/{file_name}"
