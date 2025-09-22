from src.pipeline.config import PDF_PATH, DRIVE_FILE_ID, CHROMA_DB_PATH, EMBEDDING_MODEL_NAME, POST_TARGET_URL, DRIVE_FOLDER_URL
from src.utils.drive_import import authenticate_google, get_pdfs_ids
from src.utils.extractor import get_all_pdfs_data
from src.pipeline.tokenizer import chunk_text, count_tokens, chunk_with_metadata
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
    print((1/10)*100, '%')

    # 2. Obtenir les ids des pdf contenu dans le dossier du drive
    drive_ids = get_pdfs_ids(service, DRIVE_FOLDER_URL, pdf_only=True)
    print(drive_ids)
    print((2/10)*100, '%')

    # 3. Obtenir toutes les datas de tous les pdfs (par page)
    pdfs_data = get_all_pdfs_data(service, drive_ids)

    # 4. Normalise le texte
    for pdf in pdfs_data:
        for page in pdf:
            page["text"] = normalize_text(page['text'])

    print("Textes Normalisé")
    print((4/10)*100, '%')

    # 5. Chunker
    chunks = chunk_with_metadata(pdfs_data)
    print(chunks)
    

"""
    chunks = chunk_text(text_normalize)
    token_counts = [count_tokens(c) for c in chunks]
    #print(f"{len(chunks)} chunks. Moy tokens: {round(sum(token_counts)/len(token_counts))}")
    print('CHUNKS: OK')
    print((5/10)*100, '%')

    # 6. Embeddings
    #embeddings = get_embeddings(chunks, EMBEDDING_MODEL_NAME)
    #print(f"Embeddings shape: {embeddings.shape}")

    # 6. Clustering
    themes = hdbscan_clustering(chunks)
    print("thèmes trouvé:", themes)
    print('THEMES: OK')
    print((6/10)*100, '%')

    # 7. Stockage Chroma
    chroma_db = save_to_chroma(chunks, EMBEDDING_MODEL_NAME, CHROMA_DB_PATH)
    print('SAVED TO CHROMA: OK')
    print((7/10)*100, '%')

    # 8. Obtenir les meilleurs chunks pour le prompt
    chunks_by_theme = find_best_chunk_to_prompt(chroma_db, themes)
    print(chunks_by_theme)
    print((8/10)*100, '%')
    
    # 6. Récupération de la vector db
    vector_data = chroma_db.get()

    # 9. Création du quizz avec les chunks par thèmes
    quiz = generate_quiz_from_chunks(chunks_by_theme, themes, difficulty)
    print(quiz)

    # 10. Envoie à l'API 
    response = requests.post(POST_TARGET_URL, json={"quiz":quiz})
    print((10/10)*100, '%')

    if response.status_code == 200:
        print("Quiz envoyé avec succès !")
    else:
        print(f"Échec de l'envoi : {response.status_code} - {response.text}")"""

if __name__ == "__main__":
    main()