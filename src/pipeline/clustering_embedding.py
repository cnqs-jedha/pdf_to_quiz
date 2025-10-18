import fr_core_news_lg
import spacy
from spacy.lang.fr.stop_words import STOP_WORDS

import matplotlib
matplotlib.use('Agg') # Forcer matplotlib à utiliser un backend non interactif (Agg)
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances
from sklearn.metrics import silhouette_score
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import normalize, StandardScaler
from collections import Counter
import re
from sentence_transformers import SentenceTransformer
import umap
import hdbscan
from keybert import KeyBERT
from keyphrase_vectorizers import KeyphraseCountVectorizer
from src.pipeline.config import EMBEDDING_MODEL_NAME
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances


nlp = spacy.load("fr_core_news_lg", disable=["parser"])

embedding = SentenceTransformer(EMBEDDING_MODEL_NAME)


def extract_top_keywords(df, cluster_col="cluster", text_col='text', embedding_model=embedding, top_n=3):
    """
    Extrait les mots-clés les plus pertinents par cluster en utilisant KeyBERT et KeyphraseCountVectorizer
    """
    themes = {}
    
    # Instancier le modèle KeyBERT
    kw_model = KeyBERT(model=embedding_model)
    
    for cluster_id in df[cluster_col].unique():
        if cluster_id == -1:  # bruit
            themes[cluster_id] = "other"
            continue

        cluster_texts = df[df[cluster_col] == cluster_id][text_col]
        cluster_texts = [str(t).strip() for t in cluster_texts if t and str(t).strip()]
        
        if not cluster_texts:
            themes[cluster_id] = "(empty)"
            continue

        try:
            joined_text = " ".join(cluster_texts)
            
            top_words = kw_model.extract_keywords(
                joined_text, 
                keyphrase_ngram_range=(1, 1), 
                use_mmr=True,
                diversity=0.5,
                top_n=top_n
                )
            
            # Alternative avec KeyphraseCountVectorizer: ne fonctionne pas...
            '''
            top_words = kw_model.extract_keywords(
                joined_text, 
                vectorizer=KeyphraseCountVectorizer(spacy_pipeline='fr_core_news_lg'),
                use_mmr=True,
                top_n=top_n
            )
            '''
            print(f"Cluster {cluster_id}: top_words = {top_words}")
            themes[cluster_id] = ", ".join([w for w, s in top_words]) if top_words else "(empty)"
        except ValueError:
            themes[cluster_id] = "(empty)"

    return themes


def topic_detection(chunks, embeddings):

    # Création du dataframe contenant les chunks
    df_chunks = pd.DataFrame(chunks)
    df_chunks["text"] = df_chunks["text"].astype(str)
    
    # Réduction de dimension des embeddings vec UMAP
    umap_model = umap.UMAP(n_neighbors=5, n_components=5, min_dist=0.0, metric='cosine', random_state=0)
    embeddings_reduced = umap_model.fit_transform(embeddings)

    # Matrice de distances cosinus
    distance_matrix = cosine_distances(embeddings_reduced).astype('float64')

    # Clustering des embeddings réduits avec HDBSCAN
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=5, 
        min_samples=2,
        metric='precomputed',
        cluster_selection_method='eom'
        )
    cluster_labels = clusterer.fit_predict(distance_matrix)
    print(f"Nombre de clusters identifiés (hors bruit): {len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)}")
    noise_ratio = list(cluster_labels).count(-1) / len(cluster_labels)
    print(f"Proportion de bruit : {noise_ratio:.2%}")
    counts = Counter(cluster_labels)
    print(f"Nb de chunks par cluster : {counts}")
    
    # Ajouter les labels de cluster au df
    df_chunks["cluster"] = cluster_labels
    print(f"Clusters : {df_chunks["cluster"].unique()}")
    print(f"colonnes du df : {df_chunks.columns}")

    # Extraire les mots-clés
    themes = extract_top_keywords(
        df_chunks,
        cluster_col="cluster",
        text_col="text",
        embedding_model=embedding,
        top_n=3
    )
    
    df_chunks["theme"] = df_chunks["cluster"].map(themes)
    
    # Output JSON
    theme_to_json = df_chunks.to_dict(orient="records")
    
    return theme_to_json


def count_chunks_by_theme(data_with_theme):
        theme_list = [d["theme"] for d in data_with_theme]
        theme_counts = Counter(theme_list)
        return dict(theme_counts)