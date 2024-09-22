# import os
# import random
# from downloader import fetch_media, media_upload_to_gcs, clean_download_folder
# from analyze_video import analyze_video_with_vertex
# from analyze_audio import analyze_audio_with_vertex
# from analyze_image import analyze_image_with_vertex

# DOWNLOAD_FOLDER = './downloads'
# bucket_name = 'trascrizione-loghi'

# def analyze(url):
#     # Step 1: Download media content
#     result = fetch_media(url)
#     if isinstance(result, str):
#         return result
    
#     content_type, media_content, file_name = result
#     if not file_name:
#         rand_num = random.randint(10**11, 10**12 - 1)
#         file_name = f"adhoc{rand_num}"
    
#     if content_type == 'html':
#         return "HTML content is not supported in this context."

#     # Save the downloaded media to a file
#     file_path = os.path.join(DOWNLOAD_FOLDER, file_name)
#     with open(file_path, 'wb') as media_file:
#         media_file.write(media_content)
    
#     # Step 2: Upload the downloaded file to Google Cloud Storage
#     gcs_uri = media_upload_to_gcs(bucket_name, file_path, file_name)
    
#     # Step 3: Analyze the media using Vertex AI
#     if content_type.startswith('video/'):
#         analysis_result = analyze_video_with_vertex(gcs_uri)
#     elif content_type.startswith('audio/'):
#         analysis_result = analyze_audio_with_vertex(gcs_uri)
#     elif content_type.startswith('image/'):
#         analysis_result = analyze_image_with_vertex(gcs_uri)
#     else:
#         analysis_result = "Unsupported media type"

#     clean_download_folder(DOWNLOAD_FOLDER)

#     return analysis_result


# # # Example usage
# if __name__ == "__main__":
#     url = "https://adintel.it.nielsen.com/kreationserver/kreation/9/72470901?0000000000005CNEQHTlNMUnpRAw1YCgZ6X1BbUVZdLAVSWQ1aVX0CVVgIC1d4V1FORUwMK0RcTlheS31VUEJbXVFhV1BYU11Vf1ZEEQ**"
#     print(analyze(url))


import os
import random
import requests
import logging
from downloader import fetch_media, media_upload_to_gcs, clean_download_folder, file_exists_in_bucket, get_content_type_from_bucket, get_file_name_from_url
from analyze_video import analyze_video_with_vertex
from analyze_audio import analyze_audio_with_vertex
from analyze_image import analyze_image_with_vertex

DOWNLOAD_FOLDER = './downloads'
bucket_name = 'trascrizione-loghi'

def analyze(url, prompt_type):
    # Step 1: Determine the file name
    response = requests.head(url, verify=False, allow_redirects=True)
    if response.status_code != 200:
        return f"Error: Failed to fetch media. Status code: {response.status_code}"

    file_name = get_file_name_from_url(url, response)
    if not file_name:
        rand_num = random.randint(10**11, 10**12 - 1)
        file_name = f"adhoc{rand_num}"

    # Step 2: Check if the file already exists in the bucket
    if file_exists_in_bucket(bucket_name, file_name):
        logging.info(f"File {file_name} already exists in the bucket.")
        content_type = get_content_type_from_bucket(bucket_name, file_name)
        gcs_uri = f"gs://{bucket_name}/{file_name}"
    else:
        logging.info(f"File {file_name} does not exist in the bucket. Downloading from URL.")
        # Step 3: Download media content
        result = fetch_media(url)
        if isinstance(result, str):
            return result

        content_type, media_content, file_name = result
        if content_type == 'html':
            return "HTML content is not supported in this context."

        # Save the downloaded media to a file
        file_path = os.path.join(DOWNLOAD_FOLDER, file_name)
        with open(file_path, 'wb') as media_file:
            media_file.write(media_content)

        # Step 4: Upload the downloaded file to Google Cloud Storage with the correct content type
        gcs_uri = media_upload_to_gcs(bucket_name, file_path, file_name, content_type)

    # Step 5: Analyze the media using Vertex AI
    if content_type.startswith('video/'):
        analysis_result = analyze_video_with_vertex(gcs_uri, prompt_type)
    elif content_type.startswith('audio/'):
        analysis_result = analyze_audio_with_vertex(gcs_uri, prompt_type)
    elif content_type.startswith('image/'):
        analysis_result = analyze_image_with_vertex(gcs_uri, prompt_type)
    else:
        analysis_result = "Unsupported media type"

    clean_download_folder(DOWNLOAD_FOLDER)

    return analysis_result