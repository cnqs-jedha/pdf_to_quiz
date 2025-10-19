from src.pipeline.config import CHROMA_DB_PATH, EMBEDDING_MODEL_NAME, POST_TARGET_URL
from src.utils.drive_import import authenticate_google, get_pdfs_ids
from src.utils.extractor import get_all_pdfs_data
from src.pipeline.tokenizer import chunk_with_metadata
# from src.pipeline.embedder import get_embeddings
from src.pipeline.chroma_handler import save_to_chroma
#from src.pipeline.clustering_latent_topics_simple import topic_detection
#from src.pipeline.clustering_chunks_hdbscan import topic_detection, count_chunks_by_theme
from src.pipeline.clustering_theme import topic_detection, count_chunks_by_theme
# from src.pipeline.clustering_theme import hdbscan_clustering, count_chunks_by_theme
#from src.pipeline.clustering_embedding import topic_detection, count_chunks_by_theme
from src.pipeline.collect_best_chunks_to_prompt import find_best_chunk_to_prompt
from src.pipeline.quiz_generator import generate_quiz_from_chunks
from src.utils.normalizer import normalize_text, normalize_list_keywords
# from langchain_chroma import Chroma
#from langchain_community.embeddings import HuggingFaceEmbeddings
#from langchain_huggingface import HuggingFaceEmbeddings
from src.utils.status_to_api import notify_stage

import requests
import time
import argparse


def main(drive_url, difficulty="standard"):
    
    timings = []
    total_start = time.time()  # début du chronomètre
    nbr_steps = 10
    
    # 1. S'identifier au drive
    start = time.time()

    notify_stage("Authentification Google Drive...")
    service = authenticate_google()

    duration = time.time() - start
    timings.append({"Etape": "Authentification Google", "Durée (sec)": duration})
    print(f"Avancement : {(1/nbr_steps)*100} %")

    # 2. Obtenir les ids des pdf contenu dans le dossier du drive
    start = time.time()

    notify_stage("Récupération des PDFs...")
    drive_ids = get_pdfs_ids(service, drive_url, pdf_only=True)
    #print(drive_ids)

    duration = time.time() - start
    timings.append({"Etape": "Récupération des IDs des PDF", "Durée (sec)": duration})
    print(f"Avancement : {(2/nbr_steps)*100} %")

    # 3. Récupère tous les textes de tous les pdfs en un seul texte
    start = time.time()

    notify_stage("Lecture des textes...")
    pdfs_data = get_all_pdfs_data(service, drive_ids)

    duration = time.time() - start
    timings.append({"Etape": "Récupération de toutes les données des pdfs en un array", "Durée (sec)": duration})
    print(f"Avancement : {(3/nbr_steps)*100} %")

    # 4. Normalise le texte
    start = time.time()

    notify_stage("Nettoyage des textes...")
    for pdf in pdfs_data:
        for page in pdf:
            page["text"] = normalize_text(page['text'])

    duration = time.time() - start
    timings.append({"Etape": "Normalisation du texte", "Durée (sec)": duration})
    print(f"Avancement : {(4/nbr_steps)*100} %")

    # 5. Chunker
    start = time.time()

    chunks = chunk_with_metadata(pdfs_data)

    duration = time.time() - start
    timings.append({"Etape": "Chunk des données", "Durée (sec)": duration})
    print(f"Avancement : {(5/nbr_steps)*100} %")
    
    # 6. Détection des thèmes
    start = time.time()
    
    notify_stage("Analyse des thèmes...")
    # Clustering non sémantique, qui n'utilise pas les embeddings
    target_topics = 5 # Nombre cible de topics à définir
    themes = topic_detection(chunks, n_topics=target_topics)

    # Clustering sémantique qui utilise les embeddings 
    '''
    all_texts = [c["text"] for c in chunks]
    embeddings = get_embeddings(all_texts, EMBEDDING_MODEL_NAME)
    themes = topic_detection(chunks, embeddings)
    '''
    #print(themes)
    counts_themes = count_chunks_by_theme(themes)
    print(counts_themes)

    list_themes_raw= list(counts_themes.keys())
    list_themes=normalize_list_keywords(list_themes_raw) # suppression des redondances dans les keywords si lemme commun
    print("Liste des thèmes bruts : ", list_themes_raw)
    print("Liste des thèmes nettoyés : ", list_themes)

    duration = time.time() - start
    timings.append({"Etape": "Thèmes créés", "Durée (sec)": duration})
    print(f"Avancement : {(6/nbr_steps)*100} %")

    # 7. Stockage Chroma
    start = time.time()

    chroma_db = save_to_chroma(themes, EMBEDDING_MODEL_NAME, CHROMA_DB_PATH)

    duration = time.time() - start
    timings.append({"Etape": "Création et stockage de la VectorDB", "Durée (sec)": duration})
    print(f"Avancement : {(7/nbr_steps)*100} %")


    # 8. Obtenir les meilleurs chunks pour le prompt
    start = time.time()
    chunks_by_theme = find_best_chunk_to_prompt(chroma_db, list_themes)

    duration = time.time() - start
    timings.append({"Etape": "Récupération des meilleurs chunks par thème", "Durée (sec)": duration})
    print(chunks_by_theme)
    print(f"Avancement : {(8/nbr_steps)*100} %")
    
    # 9. Création du quizz avec les chunks par thèmes
    start = time.time()

    notify_stage("Génération du quiz...")
    quiz = generate_quiz_from_chunks(chunks_by_theme, difficulty)
    print(quiz)

    duration = time.time() - start
    timings.append({"Etape": "Création du quizz", "Durée (sec)": duration})
    
    # 10. Envoi à l'API 
    start = time.time()    

    response = requests.post(POST_TARGET_URL, json={"quiz":quiz})

    duration = time.time() - start
    timings.append({"Etape": "Envoi à l'API", "Durée (sec)": duration})
    print(f"Avancement : {(10/10)*100} %")

    if response.status_code == 200:
        print("Quiz envoyé avec succès !")
        notify_stage("Quiz Prêt...")
    else:
        print(f"Échec de l'envoi : {response.status_code} - {response.text}")
    
    total_duration = time.time() - total_start
    timings.append({"Etape": "Durée totale", "Durée (sec)": total_duration})

    # --- Résumé final des temps d'exécution ---
    print("\nRésumé des temps d'exécution par étape :")
    
    for timing in timings:
        name = timing["Etape"]
        duration = timing["Durée (sec)"]
        print(name, " : ", round(duration, 2), " sec")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lancer le pipeline à partir d'un lien Google Drive")
    parser.add_argument("--drive_link", required=False, help="Lien Google Drive du dossier à traiter")
    # parser.add_argument("--difficulty", default="standard", help="Niveau de difficulté du quiz")
    args = parser.parse_args()
    print("args:", args)

    # Si un lien est fourni, exécution directe (utile en local)
    if args.drive_link:
        print('link:', args.drive_link)
        main(args.drive_link)
    else:
        print("⚠️ Aucun lien fourni — le pipeline est prêt mais en attente d'appel via l'API.")
