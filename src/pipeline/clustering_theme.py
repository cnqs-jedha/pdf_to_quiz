import fr_core_news_sm
import spacy
from spacy.lang.fr.stop_words import STOP_WORDS
from spacy.lang.fr.stop_words import STOP_WORDS as FR_STOPS

import seaborn as sns
import pandas as pd
import numpy as np

from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import confusion_matrix
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import hdbscan
from sklearn.preprocessing import normalize

from src.utils.normalizer import normalize_text  # on réutilise le normalize.py

def clean_chunks_strings(chunks):
    """
    Nettoyage des chunks pour le clustering, en utilisant le texte déjà normalisé.
    """
    # On suppose que les chunks sont déjà normalisés via normalize_text
    chunks_df = pd.DataFrame(chunks, columns=['string'])

    # Nettoyage léger spécifique au clustering
    chunks_df['string_clean'] = chunks_df['string'].str.replace(r"<[^>]*>", " ", regex=True)
    chunks_df['string_clean'] = chunks_df['string_clean'].str.replace(r"\s+", " ", regex=True)
    chunks_df['string_clean'] = chunks_df['string_clean'].fillna('').apply(lambda x: x.lower())

    # Stopwords + TF/IDF pour enlever mots peu informatifs
    chunks_df['nlp_ready'] = chunks_df['string_clean']

    # Vectorisation TF-IDF pour calculer mean_tfidf
    vectorizer_temp = TfidfVectorizer(stop_words=None)
    X_temp = vectorizer_temp.fit_transform(chunks_df['nlp_ready'])
    feature_names = vectorizer_temp.get_feature_names_out()
    mean_tfidf = X_temp.mean(axis=0).A1

    vec = CountVectorizer()
    X_count = vec.fit_transform(chunks_df['nlp_ready'])
    doc_freq = np.asarray(X_count.sum(axis=0)).ravel() / X_count.shape[0]
    words_high_freq = [word for word, freq in zip(vec.get_feature_names_out(), doc_freq) if freq > 0.7]

    threshold = 0.008
    low_info_words = [word for word, score in zip(feature_names, mean_tfidf) if score < threshold]

    combined_stopwords = STOP_WORDS.union(set(low_info_words)).union(set(words_high_freq))

    # Filtrage final pour nlp_ready
    chunks_df['nlp_ready'] = chunks_df['string_clean'].apply(
        lambda x: ' '.join([w for w in x.split() if w not in combined_stopwords])
    )

    return chunks_df


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

def get_3_words_by_theme(cluster_list, df_model):
    top_words_per_cluster = {}
    strings_array = []

    for cluster_id in cluster_list.unique():
        if cluster_id == -1:
            continue

        cluster_texts = df_model[cluster_list == cluster_id]['nlp_ready']
        cluster_texts = [t for t in cluster_texts if isinstance(t, str) and t.strip()]

        if not cluster_texts:
            top_words_per_cluster[cluster_id] = ["(aucun mot)"]
            continue

        vectorizer = CountVectorizer()
        try:
            X = vectorizer.fit_transform(cluster_texts)
        except ValueError:
            top_words_per_cluster[cluster_id] = ["(aucun mot)"]
            continue

        word_counts = X.sum(axis=0)
        words_freq = [(word, word_counts[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
        top_words = sorted(words_freq, key=lambda x: x[1], reverse=True)[:3]
        top_words_per_cluster[cluster_id] = [w for w, _ in top_words] if top_words else ["(aucun mot)"]

    for theme_id, words in top_words_per_cluster.items():
        strings_array.append(" ".join(words))

    return strings_array

def hdbscan_clustering(chunks):
    # Nettoyage et lemmatisation des chunks
    df_chunks = clean_chunks_strings(chunks)

    # TF-IDF pour la réduction de dimension
    vectorizer = TfidfVectorizer(stop_words=None)
    X = vectorizer.fit_transform(df_chunks['nlp_ready'])

    # Détermination automatique du nombre de dimensions pour SVD
    k = auto_svd_dim(X, target_var=0.7, min_dim=5, max_dim=300)
    svd_model = TruncatedSVD(n_components=k, algorithm='randomized', n_iter=100, random_state=42)
    lsa = svd_model.fit_transform(X)

    # Normalisation pour HDBSCAN
    X_norm = normalize(lsa)

    # Clustering
    n_samples = len(X_norm)
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=max(3, n_samples // 50),
        min_samples=1,
        metric='euclidean',
        cluster_selection_method='leaf',
        cluster_selection_epsilon=0.05
    )
    labels = clusterer.fit_predict(X_norm)

    # Création du DataFrame final
    df_result = df_chunks[['string', 'nlp_ready']].copy()
    df_result['hdb_cluster'] = labels

    # Extraction des 3 mots clés par thème
    themes = get_3_words_by_theme(df_result['hdb_cluster'], df_result)

    return themes