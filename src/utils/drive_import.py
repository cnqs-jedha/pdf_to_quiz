import pickle, os, io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from src.pipeline.config import SCOPES
import json

def authenticate_google():
    creds = None
    if os.path.exists("token"):
        with open("token", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        cred_json = os.getenv("DRIVE_CREDENTIALS")
        if not cred_json:
            raise RuntimeError("Variable d'environnement DRIVE_CREDENTIALS absente")
        client_config = json.loads(cred_json)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(open_browser=False)
        with open("token", "wb") as token:
            pickle.dump(creds, token)

    return build("drive", "v3", credentials=creds)

def download_pdf_from_drive(file_id: str, output_path: str):
    """Télécharge un PDF depuis Google Drive et enregistre le dans le dossier /data"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    service = authenticate_google()
    request = service.files().get_media(fileId=file_id)
    #fh = io.FileIO(output_path, "wb")
     # Créer le fichier en mode binaire
    with io.FileIO(output_path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Téléchargement : {int(status.progress() * 100)}%")

    print(f"PDF téléchargé à : {output_path}")
