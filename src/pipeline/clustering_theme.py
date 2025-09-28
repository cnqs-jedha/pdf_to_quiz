import fr_core_news_lg
import spacy
from spacy.lang.fr.stop_words import STOP_WORDS
from spacy.lang.fr.stop_words import STOP_WORDS as FR_STOPS

import seaborn as sns
import pandas as pd
import numpy as np

from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import hdbscan
from sklearn.preprocessing import normalize
from collections import Counter
import re

#from src.utils.normalizer import normalize_text

nlp = spacy.load("fr_core_news_lg", disable=["ner", "parser"])

def clean_chunks_strings(chunks, tfidf_threshold=0.008, high_freq_threshold=0.7):
    """
    Prépare les chunks pour HDBSCAN :
    - Nettoyage statistique (TF-IDF, haute fréquence, stopwords)
    - Lemmatisation linguistique
    - Filtrage POS (supprime les tokens peu informatifs)
    - Conservation des noms propres fréquents (PER, GPE, LOC)
    """
    df = pd.DataFrame(chunks)
    df["string"] = df["text"].astype(str)
    df["string"] = df["string"].fillna('').apply(lambda x: x.lower())

    # --- Étape 1 : stopwords simples
    df['desc_token_temp'] = df['string'].apply(
        lambda x: [token.lemma_ for token in nlp(x) if token.text.lower() not in STOP_WORDS]
    )
    df['nlp_ready_temp'] = df['desc_token_temp'].apply(lambda x: ' '.join(x))

    # --- Étape 2 : TF-IDF pour bas score
    vectorizer_temp = TfidfVectorizer(stop_words='english')
    X_temp = vectorizer_temp.fit_transform(df['nlp_ready_temp'])
    feature_names = vectorizer_temp.get_feature_names_out()
    mean_tfidf = X_temp.mean(axis=0).A1
    low_info_words = [word for word, score in zip(feature_names, mean_tfidf) if score < tfidf_threshold]

    # --- Étape 3 : fréquence documentaire pour mots trop fréquents
    vec = CountVectorizer()
    X_count = vec.fit_transform(df['nlp_ready_temp'])
    doc_freq = np.asarray(X_count.sum(axis=0)).ravel() / X_count.shape[0]
    words_high_freq = [word for word, freq in zip(vec.get_feature_names_out(), doc_freq) if freq > high_freq_threshold]

    # --- Étape 4 : stopwords combinés
    combined_stopwords = STOP_WORDS.union(set(low_info_words)).union(set(words_high_freq))

    # --- Étape 5 : extraire les noms propres PER/GPE/LOC avec spaCy
    all_entities = []
    for doc in nlp.pipe(df['nlp_ready_temp'], batch_size=20):
        ents = [ent.text for ent in doc.ents if ent.label_ in ["PER", "GPE", "LOC"]]
        all_entities.extend(ents)

    def clean_entity(ent):
        text = ent.strip()
        if len(text) <= 3 or len(text.split()) >= 10:
            return None
        text = re.sub(r"\s+", " ", text)
        return text

    entities_clean = [clean_entity(ent) for ent in all_entities if clean_entity(ent)]
    entity_counts = Counter(entities_clean)
    threshold_count = 3
    proper_nouns_final = {
        ent.lower() for ent, count in entity_counts.items() if count >= threshold_count
    }

    # --- Étape 6 : reconstruction finale
    df['desc_token'] = df['string'].apply(
        lambda x: [
            token.text if token.text.lower() in proper_nouns_final else token.lemma_.lower()
            for token in nlp(x)
            if token.is_alpha
            and token.text.lower() not in combined_stopwords
            and token.lemma_.lower() not in combined_stopwords
            and (token.pos_ in {"NOUN", "VERB", "ADJ"} or token.text.lower() in proper_nouns_final)
        ]
    )
    df['nlp_ready'] = df['desc_token'].apply(lambda x: ' '.join(x))

    return df

#Trouver automatiquement la dimension du svd
def auto_svd_dim(X, target_var=0.7, min_dim=5, max_dim=300):
    max_rank = min(X.shape[0]-1, X.shape[1]-1)
    probe = min(max_dim, max_rank)
    svd_probe = TruncatedSVD(n_components=max(2, probe), random_state=42)
    svd_probe.fit(X)
    cumvar = np.cumsum(svd_probe.explained_variance_ratio_)
    k = int(np.searchsorted(cumvar, target_var) + 1)
    k = max(min_dim, min(k, probe))
    return k

def extract_top_keywords(df, cluster_col="hdb_cluster", text_col="nlp_ready", top_n=3):
    """
    Extrait les mots-clés les plus pertinents par cluster en utilisant TF-IDF.
    """
    themes = {}
    for cluster_id in df[cluster_col].unique():
        if cluster_id == -1:  # bruit
            themes[cluster_id] = "other"
            continue

        cluster_texts = df[df[cluster_col] == cluster_id][text_col]
        cluster_texts = [t for t in cluster_texts if isinstance(t, str) and t.strip()]

        if not cluster_texts:
            themes[cluster_id] = "(empty)"
            continue

        try:
            vectorizer = TfidfVectorizer(max_features=500)
            X = vectorizer.fit_transform(cluster_texts)
            scores = X.mean(axis=0).A1
            words = vectorizer.get_feature_names_out()
            top_words = [w for w, _ in sorted(zip(words, scores), key=lambda x: x[1], reverse=True)[:top_n]]
            themes[cluster_id] = " ".join(top_words) if top_words else "(empty)"
        except ValueError:
            themes[cluster_id] = "(empty)"

    return themes

threshold = 0.2 # A automatiser si on veut un nombre minimum de clusters (si chiffre plus grand plus de clusters, si chiffre plus petit moins de clusters)
def merge_close_clusters(df, embeddings, cluster_col="hdb_cluster", sim_threshold=threshold):
    """
    Fusionne les clusters proches en utilisant la similarité cosinus de leurs centroïdes,
    dans l’espace des embeddings (SVD normalisés).
    """
    centroids = {}
    for cluster_id in df[cluster_col].unique():
        if cluster_id == -1:  # ignorer le bruit
            continue
        mask = (df[cluster_col] == cluster_id).values
        if mask.sum() == 0:
            continue
        centroid_vec = embeddings[mask].mean(axis=0)
        centroids[cluster_id] = centroid_vec

    if not centroids:
        return df, {}

    ids = list(centroids.keys())
    centroid_matrix = np.vstack([centroids[i] for i in ids])
    sims = cosine_similarity(centroid_matrix)

    # Union-find pour fusionner
    parent = {cid: cid for cid in ids}

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    for i, id1 in enumerate(ids):
        for j, id2 in enumerate(ids):
            if i < j and sims[i, j] > sim_threshold:
                p1, p2 = find(id1), find(id2)
                if p1 != p2:
                    parent[p2] = p1

    df["merged_cluster"] = df[cluster_col].apply(lambda c: find(c) if c in parent else c)
    return df, parent


def hdbscan_clustering(chunks, merge_clusters=True, sim_threshold=threshold):
    # Nettoyage
    df_chunks = clean_chunks_strings(chunks)

    # TF-IDF
    vectorizer = TfidfVectorizer(stop_words=None)
    X = vectorizer.fit_transform(df_chunks['nlp_ready'])

    # SVD
    k = auto_svd_dim(X, target_var=0.7, min_dim=5, max_dim=300)
    svd_model = TruncatedSVD(n_components=k, algorithm='randomized', n_iter=100, random_state=42)
    lsa = svd_model.fit_transform(X)

    # Normalisation
    X_norm = normalize(lsa)

    # Clustering
    n_samples = len(X_norm)
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=max(5, n_samples // 100),
        min_samples=1,
        metric='euclidean',
        cluster_selection_method='eom',
        cluster_selection_epsilon=0.03
    )
    labels = clusterer.fit_predict(X_norm)
    df_chunks['hdb_cluster'] = labels

    # Fusion optionnelle
    if merge_clusters:
        df_chunks, merged_map = merge_close_clusters(
            df_chunks,
            embeddings=X_norm,
            cluster_col="hdb_cluster",
            sim_threshold=sim_threshold
        )
        final_col = "merged_cluster"
    else:
        final_col = "hdb_cluster"


    # Extraction des thèmes
    themes = extract_top_keywords(df_chunks, cluster_col=final_col, text_col="nlp_ready", top_n=3)
    df_chunks['theme'] = df_chunks[final_col].map(themes)

    # Output JSON
    theme_to_json = df_chunks.drop(columns=["hdb_cluster", "nlp_ready", "merged_cluster", "desc_token_temp", "nlp_ready_temp", "string", "desc_token"]).to_dict(orient="records")
    return theme_to_json


def count_chunks_by_theme(data_with_theme):
        theme_list = [d["theme"] for d in data_with_theme]
        theme_counts = Counter(theme_list)
        return dict(theme_counts)