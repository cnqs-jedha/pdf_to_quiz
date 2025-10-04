from src.pipeline.config import DRIVE_FOLDER_URL, SCOPES, SHORTCUT_MIME, FOLDER_MIME
import pickle, os, io
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from typing import List, Dict, Optional
import re
from urllib.parse import urlparse, parse_qs
from googleapiclient.errors import HttpError
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

id_re = re.compile(r"[A-Za-z0-9_-]{10,}")

# Transforme l'url du drive en id de dossier
def get_folder_drive_id(folder_url):
    url_stripe = folder_url.strip()
    if id_re.fullmatch(url_stripe):
        return url_stripe
    
    url_parse = urlparse(url_stripe)
    url_id = re.search(r"/folders/([A-Za-z0-9_-]{10,})", url_parse.path)

    if url_id:
        return url_id.group(1)
    
    url_qs = parse_qs(url_parse)
    if "id" in url_qs and url_qs["id"]:
        return url_qs["id"][0]
    
    url_id = id_re.search(url_stripe)
    if url_id:
        return url_id.group(0)
    
    raise ValueError("Impossible d'extraire l'ID du dossier depuis l'URL.")

# Vérifie que l'id soit bien un id de dossier drive et qu'il soit accessible
def get_folder_meta(service, folder_id: str) -> dict:
    meta = service.files().get(
        fileId=folder_id,
        fields="id,name,mimeType,driveId,trashed,shortcutDetails,webViewLink",
        supportsAllDrives=True,
    ).execute()

    if meta.get("trashed"):
        raise ValueError("Le dossier est dans la corbeille.")

    meta_mimetype = meta.get("mimeType")

    if meta_mimetype == SHORTCUT_MIME:
        details = meta.get("shortcutDetails") or {}
        target_id   = details.get("targetId")
        target_mime = details.get("targetMimeType")
        if target_mime != FOLDER_MIME:
            raise ValueError("Le raccourci ne pointe pas vers un dossier.")
        return get_folder_meta(service, target_id)  # revalide la cible et récupère son driveId

    if meta_mimetype != FOLDER_MIME:
        raise ValueError(f"L'ID fourni n'est pas un dossier Google Drive (mime={meta_mimetype}).")
    return meta

# Iter sur les enfants du dossier
def iter_children(service, folder_id: str):
    page_token = None
    while True:
        resp = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="nextPageToken, files(id,name,mimeType,shortcutDetails)",
            pageSize=1000,
            spaces="drive",
            corpora="allDrives",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            pageToken=page_token,
        ).execute()
        for f in resp.get("files", []):
            yield f
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

# Vérifie les lien ét les métadatas
def documents_in_folder(service, folder_meta, recursive=False):
    drive_id = folder_meta.get("driveId")  # None si My Drive

    out, queue = [], [folder_meta["id"]]
    while queue:
        current = queue.pop(0)
        for item in iter_children(service, current, drive_id):
            mt = item.get("mimeType")
            # suivre les raccourcis
            if mt == SHORTCUT_MIME:
                det = item.get("shortcutDetails") or {}
                item = {"id": det.get("targetId"), "mimeType": det.get("targetMimeType")}

            if item["mimeType"] == FOLDER_MIME:
                if recursive:
                    queue.append(item["id"])
            else:
                out.append(item["id"])
    return out


FOLDER_MIME   = "application/vnd.google-apps.folder"
SHORTCUT_MIME = "application/vnd.google-apps.shortcut"
PDF_MIME      = "application/pdf"  # si tu veux filtrer plus tard

def list_document_ids_shallow(service, folder_id: str, pdf_only: bool = False) -> list[str]:
    ids = []
    for item in iter_children(service, folder_id):
        mt = item.get("mimeType")

        # Raccourci -> on bascule sur la cible
        if mt == SHORTCUT_MIME:
            det = item.get("shortcutDetails") or {}
            tgt_id   = det.get("targetId")
            tgt_mime = det.get("targetMimeType")
            if tgt_mime == FOLDER_MIME:
                continue  # ici on ne descend pas, c'est la version "shallow"
            if pdf_only and tgt_mime != PDF_MIME:
                continue
            if tgt_id:
                ids.append(tgt_id)
            continue

        if mt == FOLDER_MIME:
            continue

        if pdf_only and mt != PDF_MIME:
            continue
        ids.append(item["id"])
    return ids

# Fonction globale pour obtenir les ids de tous les enfants pdfs de mon folder drive
def get_pdfs_ids(service, drive_folder_url: str, pdf_only: bool = False) -> list[str]:
    ids = []
    folder_id = get_folder_drive_id(drive_folder_url)
    get_folder_meta(service, folder_id)

    for item in iter_children(service, folder_id):
        mt = item.get("mimeType")

        if mt == SHORTCUT_MIME:
            det = item.get("shortcutDetails") or {}
            tgt_id   = det.get("targetId")
            tgt_mime = det.get("targetMimeType")
            if tgt_mime == FOLDER_MIME:
                continue  # ici on ne descend pas, c'est la version "shallow"
            if pdf_only and tgt_mime != PDF_MIME:
                continue
            if tgt_id:
                ids.append(tgt_id)
            continue

        if mt == FOLDER_MIME:
            continue

        if pdf_only and mt != PDF_MIME:
            continue
        ids.append(item["id"])

    return ids