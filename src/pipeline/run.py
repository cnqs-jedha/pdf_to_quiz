from src.pipeline.config import PDF_PATH, DRIVE_FILE_ID, CHROMA_DB_PATH, EMBEDDING_MODEL_NAME, POST_TARGET_URL
from src.utils.drive_import import download_pdf_from_drive, authenticate_google
from src.utils.extractor import iter_texts_with_progress
from src.pipeline.tokenizer import chunk_text, count_tokens
from src.pipeline.embedder import get_embeddings
from src.pipeline.chroma_handler import save_to_chroma
from src.pipeline.clustering_theme import hdbscan_clustering
from src.pipeline.collect_best_chunks_to_prompt import find_best_chunk_to_prompt
from src.pipeline.quiz_generator import generate_quiz_from_chunks
from src.utils.normalizer import normalize_text
import requests

def main(difficulty="standard"):
    # 1. S'identifier au drive
    service = authenticate_google()
    print("Identifié à Google")

    # 2. Récupère tous les textes de tous les pdfs en un seul texte
    full_text = "\n\n".join(iter_texts_with_progress(service, DRIVE_FILE_ID))
    print("Textes Récupéré")

    # 3. Normalise le texte
    text_normalize = normalize_text(full_text)
    print("Textes Normalisé")

    # 4. Chunker
    chunks = chunk_text(text_normalize)
    token_counts = [count_tokens(c) for c in chunks]
    #print(f"{len(chunks)} chunks. Moy tokens: {round(sum(token_counts)/len(token_counts))}")
    print('CHUNKS: OK')

    # 5. Embeddings
    embeddings = get_embeddings(chunks, EMBEDDING_MODEL_NAME)
    #print(f"Embeddings shape: {embeddings.shape}")

    # Clustering
    themes = hdbscan_clustering(chunks)
    print("thèmes trouvé:", themes)
    print('THEMES: OK')

    # 5. Stockage Chroma
    chroma_db = save_to_chroma(chunks, EMBEDDING_MODEL_NAME, CHROMA_DB_PATH)
    print('SAVED TO CHROMA: OK')

    # Obtenir les meilleurs chunks pour le prompt
    chunks_by_theme = find_best_chunk_to_prompt(chroma_db, themes)
    print(chunks_by_theme)
    
    # 6. Récupération de la vector db
    #vector_data = chroma_db.get()
    # 6. Création du quizz avec les chunks par thèmes
    quiz = generate_quiz_from_chunks(chunks_by_theme, themes, difficulty)
    print(quiz)

    # 7. Envoie à l'API 
    response = requests.post(POST_TARGET_URL, json={"quiz":quiz})

    if response.status_code == 200:
        print("Quiz envoyé avec succès !")
    else:
        print(f"Échec de l'envoi : {response.status_code} - {response.text}")

if __name__ == "__main__":
    main()