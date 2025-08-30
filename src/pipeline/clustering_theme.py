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

#nettoyer le text des chunks
def clean_chunks_strings(chunks):
    nlp = fr_core_news_sm.load()
    chunks_df = pd.DataFrame(chunks, columns=['string'])

    chunks_df['string_clean'] = chunks_df['string'].str.replace(r"<[^>]*>", " ", regex=True)
    chunks_df['string_clean'] = chunks_df['string_clean'].str.replace(r"[^A-Za-zÀ-ÿ0-9\s ]+", " ", regex = True)
    chunks_df['string_clean'] = chunks_df['string_clean'].str.replace(r"\s+", " ", regex = True)
    chunks_df['string_clean'] = chunks_df['string_clean'].fillna('').apply(lambda x: x.lower())


    chunks_df['string_token_temp'] = chunks_df['string_clean'].apply(lambda x: [token.lemma_ for token in nlp(x) if token.text.lower() not in FR_STOPS])
    chunks_df['nlp_ready_temp'] = chunks_df['string_token_temp'].apply(lambda x: ' '.join(x))

    vectorizer_temp = TfidfVectorizer(stop_words=None)
    X_temp = vectorizer_temp.fit_transform(chunks_df['nlp_ready_temp'])
    feature_names = vectorizer_temp.get_feature_names_out()
    mean_tfidf = X_temp.mean(axis=0).A1

    vec = CountVectorizer()
    X_count = vec.fit_transform(chunks_df['nlp_ready_temp'])
    doc_freq = np.asarray(X_count.sum(axis=0)).ravel() / X_count.shape[0]
    words_high_freq = [word for word, freq in zip(vec.get_feature_names_out(), doc_freq) if freq > 0.7]

    threshold = 0.008
    low_info_words = [word for word, score in zip(feature_names, mean_tfidf) if score < threshold]

    combined_stopwords = STOP_WORDS.union(set(low_info_words)).union(set(words_high_freq))

    chunks_df['string_token'] = chunks_df['string_clean'].apply(
        lambda x: [token.lemma_ for token in nlp(x)
                if token.text.lower() not in combined_stopwords
                and token.lemma_.lower() not in combined_stopwords]
    )
    chunks_df['nlp_ready'] = chunks_df['string_token'].apply(lambda x: ' '.join(x))
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



#topic_df = pd.DataFrame(lsa, columns=["topic {}".format(i+1) for i in range(k)], index=df.index)
#topic_df['string'] = df['nlp_ready'].values


# Sortir le top 3 des mots par thème
def get_3_words_by_theme(cluster_list, dataframe_model):
    top_words_per_cluster = {}
    strings_array = []

    for cluster_id in cluster_list.unique():
        if cluster_id == -1:  # on ignore le bruit
            continue
        
        cluster_texts = dataframe_model[cluster_list == cluster_id]['nlp_ready']
        
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(cluster_texts)
        
        word_counts = X.sum(axis=0)
        words_freq = [(word, word_counts[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
        
        top_words = sorted(words_freq, key=lambda x: x[1], reverse=True)[:3]
        top_words_per_cluster[cluster_id] = [w for w, _ in top_words]

    for theme_id, words in top_words_per_cluster.items():
        string = ' '.join(words)
        strings_array.append(string)
    
    return strings_array

    


# Faire le clustering avec HDBSCAN
def hdbscan_clustering(chunks):
    string_clean = clean_chunks_strings(chunks)

    final_vectorizer = TfidfVectorizer(stop_words=None)
    X = final_vectorizer.fit_transform(string_clean['nlp_ready'])

    k = auto_svd_dim(X, target_var=0.7, min_dim=5, max_dim=300)
    svd = TruncatedSVD(n_components=k, random_state=42)
    svd.fit(X)

    svd_model = TruncatedSVD(n_components=k, algorithm='randomized', n_iter=100)
    lsa = svd_model.fit_transform(X)

    X = normalize(lsa)

    n = len(X)
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size = max(3, n//50),
        min_samples = 1,                    
        metric = 'euclidean',               
        cluster_selection_method='leaf',    
        cluster_selection_epsilon=0.05     
    )
    labels = clusterer.fit_predict(X)

    # Création d’un DataFrame avec résultats
    df_hdbscan = string_clean.copy()
    df_hdbscan = df_hdbscan.drop(
        columns=['string_clean', 'string_token_temp', 'nlp_ready_temp', 'string_token']
    )
    df_hdbscan['hdb_cluster'] = labels

    themes = get_3_words_by_theme(df_hdbscan['hdb_cluster'], df_hdbscan)

    return themes