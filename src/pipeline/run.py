from src.pipeline.config import PDF_PATH, DRIVE_FILE_ID, CHROMA_DB_PATH, EMBEDDING_MODEL_NAME, POST_TARGET_URL, DRIVE_FOLDER_URL
from src.utils.drive_import import authenticate_google, get_pdfs_ids
from src.utils.extractor import get_all_pdfs_data
from src.pipeline.tokenizer import chunk_text, count_tokens, chunk_with_metadata
from src.pipeline.embedder import get_embeddings
from src.pipeline.chroma_handler import save_to_chroma
from src.pipeline.clustering_theme import hdbscan_clustering, count_chunks_by_theme
from src.pipeline.collect_best_chunks_to_prompt import find_best_chunk_to_prompt
from src.pipeline.quiz_generator import generate_quiz_from_chunks
from src.utils.normalizer import normalize_text
from langchain_chroma import Chroma
#from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings



import requests
import time

def main(difficulty="standard"):
    
    timings = []
    total_start = time.time()  # début du chronomètre
    nbr_steps = 10
    
    # 1. S'identifier au drive
    start = time.time()

    service = authenticate_google()

    duration = time.time() - start
    timings.append({"Etape": "Authentification Google", "Durée (sec)": duration})
    print(f"Avancement : {(1/nbr_steps)*100} %")

    # 2. Obtenir les ids des pdf contenu dans le dossier du drive
    start = time.time()

    drive_ids = get_pdfs_ids(service, DRIVE_FOLDER_URL, pdf_only=True)
    #print(drive_ids)

    duration = time.time() - start
    timings.append({"Etape": "Récupération des IDs des PDF", "Durée (sec)": duration})
    print(f"Avancement : {(2/nbr_steps)*100} %")

    # 3. Récupère tous les textes de tous les pdfs en un seul texte
    start = time.time()

    pdfs_data = get_all_pdfs_data(service, drive_ids)

    duration = time.time() - start
    timings.append({"Etape": "Récupération de toutes les données des pdfs en un array", "Durée (sec)": duration})
    print(f"Avancement : {(3/nbr_steps)*100} %")

    # 4. Normalise le texte
    start = time.time()

    for pdf in pdfs_data:
        for page in pdf:
            page["text"] = normalize_text(page['text'])

    duration = time.time() - start
    timings.append({"Etape": "Normalisation du texte", "Durée (sec)": duration})
    print(f"Avancement : {(4/nbr_steps)*100} %")

    # 5. Chunker
    start = time.time()

    chunks = chunk_with_metadata(pdfs_data)
    #print(chunks)

    duration = time.time() - start
    timings.append({"Etape": "Chunk des données", "Durée (sec)": duration})
    print(f"Avancement : {(5/nbr_steps)*100} %")
    
    # 6. Clustering
    start = time.time()
    data_with_theme = hdbscan_clustering(chunks)
    print(data_with_theme)

    counts_themes = count_chunks_by_theme(data_with_theme)
    print(counts_themes)

    counts_themes.pop("other", None)
    list_themes= list(counts_themes.keys())
    print(list_themes)

    duration = time.time() - start
    timings.append({"Etape": "Thèmes créés", "Durée (sec)": duration})
    print(f"Avancement : {(6/nbr_steps)*100} %")


    # 7. Stockage Chroma
    start = time.time()

    chroma_db = save_to_chroma(data_with_theme, EMBEDDING_MODEL_NAME, CHROMA_DB_PATH)

    duration = time.time() - start
    timings.append({"Etape": "Création et stockage de la VectorDB", "Durée (sec)": duration})
    print(f"Avancement : {(7/nbr_steps)*100} %")


    #vector_data = chroma_db.get()
    #print("vector_data")
    #print(vector_data)
    #embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    #db = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embedding_model)

    # Récupérer le nombre de documents
    #print("Nombre de documents :", db._collection.count())

    # Exemple : chercher le premier chunk
    #results = db.similarity_search("Clovis", k=3)
    #print("Exemple de résultat :")
    #print("Texte :", results[0].page_content)
    #print("Metadata :", results[0].metadata)
    #print("Results :", results)

    # 8. Obtenir les meilleurs chunks pour le prompt
    start = time.time()
    chunks_by_theme = find_best_chunk_to_prompt(chroma_db, list_themes)

    duration = time.time() - start
    timings.append({"Etape": "Récupération des meilleurs chunks par thème", "Durée (sec)": duration})
    print(chunks_by_theme)
    print(f"Avancement : {(8/nbr_steps)*100} %")

    """
    # 9. Création du quizz avec les chunks par thèmes
    start = time.time()
    quiz = generate_quiz_from_chunks(chunks_by_theme, themes, difficulty)
    duration = time.time() - start
    timings.append({"Etape": "Création du quizz", "Durée (sec)": duration})
    print(quiz)

    # 10. Envoi à l'API 
    '''
    start = time.time()    
    response = requests.post(POST_TARGET_URL, json={"quiz":quiz})
    duration = time.time() - start
    timings.append({"Etape": "Envoi à l'API", "Durée (sec)": duration})
    print(f"Avancement : {(10/10)*100} %")

    if response.status_code == 200:
        print("Quiz envoyé avec succès !")
    else:
        print(f"Échec de l'envoi : {response.status_code} - {response.text}")
    """
    total_duration = time.time() - total_start
    timings.append({"Etape": "Durée totale", "Durée (sec)": total_duration})

    # --- Résumé final des temps d'exécution ---
    print("\nRésumé des temps d'exécution par étape :")
    
    for timing in timings:
        name = timing["Etape"]
        duration = timing["Durée (sec)"]
        print(name, " : ", round(duration, 2), " sec")

if __name__ == "__main__":
    main()