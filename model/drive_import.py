import pickle, os, io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import SCOPES

def authenticate_google():
    creds = None
    if os.path.exists("token"):
        with open("token", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials3.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token", "wb") as token:
            pickle.dump(creds, token)

    return build("drive", "v3", credentials=creds)

def download_pdf_from_drive(file_id: str, output_path: str):
    service = authenticate_google()
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(output_path, "wb")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Téléchargement : {int(status.progress() * 100)}%")
    print(f"PDF téléchargé à : {output_path}")
