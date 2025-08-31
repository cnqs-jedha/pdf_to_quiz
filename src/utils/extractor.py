import io
from pypdf import PdfReader
from googleapiclient.http import MediaIoBaseDownload

#    Télécharge le PDF Drive dans un buffer mémoire (BytesIO) sans le stocker sur disque.
def download_to_bytesio(service, file_id: str, chunk_size: int = 1 << 20) -> io.BytesIO:
    request = service.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request, chunksize=chunk_size)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    buf.seek(0)
    return buf

#    Lit le PDF directement depuis le BytesIO avec pypdf et renvoie le texte concaténé.
def extract_text_pypdf_in_memory(service, file_id: str) -> str:
    pdf_buf = download_to_bytesio(service, file_id)
    reader = PdfReader(pdf_buf)

    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts).strip()

# Iter sur la liste d'ids de paragraphe et retrourne le texte extrait du paragraphe courant
def iter_texts_with_progress(service, file_ids):
    total = len(file_ids)
    for i, file_id in enumerate(file_ids, 1):
        print(f"{i/total*100:.1f}%")
        yield extract_text_pypdf_in_memory(service, file_id)
