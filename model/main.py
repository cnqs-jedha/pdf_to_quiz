from config import PDF_PATH, DRIVE_FILE_ID, CHROMA_DB_PATH, EMBEDDING_MODEL_NAME, POST_TARGET_URL
from drive_import import download_pdf_from_drive
from extractor import extract_text_from_pdf
from tokenizer import chunk_text, count_tokens
from embedder import get_embeddings
from chroma_handler import save_to_chroma
from clustering_theme import hdbscan_clustering
from collect_best_chunks_to_prompt import find_best_chunk_to_prompt
from quiz_generator import generate_quiz_from_chunks
import requests

def main(difficulty="standard"):
    # 1. Télécharger le PDF depuis Google Drive
    download_pdf_from_drive(DRIVE_FILE_ID, PDF_PATH)

    # 2. Extraction du texte
    text = extract_text_from_pdf(PDF_PATH)

    # 3. Chunker
    chunks = chunk_text(text)
    token_counts = [count_tokens(c) for c in chunks]
    #print(f"{len(chunks)} chunks. Moy tokens: {round(sum(token_counts)/len(token_counts))}")

    # 4. Embeddings
    embeddings = get_embeddings(chunks, EMBEDDING_MODEL_NAME)
    #print(f"Embeddings shape: {embeddings.shape}")

    # Clustering
    themes = hdbscan_clustering(chunks)
    #print("thèmes trouvé:", themes)

    # 5. Stockage Chroma
    chroma_db = save_to_chroma(chunks, EMBEDDING_MODEL_NAME, CHROMA_DB_PATH)

    # Obtenir les meilleurs chunks pour le prompt
    chunks_by_theme = find_best_chunk_to_prompt(chroma_db, themes)
    #print(chunks_by_theme)
    
    # 6. Récupération de la vector db
    #vector_data = chroma_db.get()

    quiz = generate_quiz_from_chunks(chunks_by_theme, themes, difficulty)
    #print(quiz)

    # 7. Envoie à l'API
    response = requests.post(POST_TARGET_URL, json={"quiz":quiz})

    if response.status_code == 200:
        print("Quiz envoyé avec succès !")
    else:
        print(f"Échec de l'envoi : {response.status_code} - {response.text}")

if __name__ == "__main__":
    main()