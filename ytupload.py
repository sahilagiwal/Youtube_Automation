from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json',
        scopes=['https://www.googleapis.com/auth/youtube.upload']
    )
    credentials = flow.run_local_server(port=0)
    return build('youtube', 'v3', credentials=credentials)

def upload_video(filename, title, description, category_id, tags, privacy):
    youtube = get_authenticated_service()
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': privacy
        }
    }

    media = MediaFileUpload(filename, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )
    response = request.execute()
    print(f'Video id {response["id"]} was uploaded successfully.')

# Example Usage
upload_video('output_video.mp4', 'Your Video Title', 'This is a description.',
             '22', ['tag1', 'tag2'], 'public')