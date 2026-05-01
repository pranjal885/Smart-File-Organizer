from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

SCOPES = ['https://www.googleapis.com/auth/drive']


def get_drive_service():
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service


# 🔥 NEW FUNCTION: GET ALL FILES (IMPORTANT)
def get_all_files(service):
    all_files = []
    page_token = None

    while True:
        response = service.files().list(
            pageSize=100,  # fetch 100 at a time
            q="mimeType != 'application/vnd.google-apps.folder'",  # skip folders
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token
        ).execute()

        files = response.get("files", [])
        all_files.extend(files)

        page_token = response.get("nextPageToken")

        if not page_token:
            break

    print(f"[Drive] Total files fetched: {len(all_files)}")

    return all_files