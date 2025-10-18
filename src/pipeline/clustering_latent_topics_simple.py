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
from sklearn.preprocessing import normalize
from collections import Counter
import re


nlp = spacy.load("fr_core_news_lg", disable=["parser"])

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

    # Normalisation de texte avant clustering
    df['string'] = df['string'].apply(lambda text:re.sub(r"\b\w\b", " ", text)) # remplacement des mots d'un caractère par un espace
    df['string'] = df['string'].apply(lambda text: re.sub(r"\s+", " ", text).strip()) # retrait des espaces inutiles
    
    # Retrait de ponctuation
    def remove_punctuation(text):
        doc = nlp(text)
        return " ".join([token.text for token in doc if not token.is_punct])
    df['string'] = df['string'].apply(remove_punctuation) # retrait de la ponctuation
    
    # --- Étape 1 : stopwords simples
    df['desc_token_temp'] = df['string'].apply(
        lambda x: [token.lemma_ for token in nlp(x) if token.text.lower() not in STOP_WORDS]
    )
    df['nlp_ready_temp'] = df['desc_token_temp'].apply(lambda x: ' '.join(x))

    # --- Étape 2 : TF-IDF pour bas score
    vectorizer_temp = TfidfVectorizer(stop_words=list(STOP_WORDS))
    X_temp = vectorizer_temp.fit_transform(df['nlp_ready_temp'])
    feature_names = vectorizer_temp.get_feature_names_out()
    mean_tfidf = X_temp.mean(axis=0).A1
    low_info_words = [word for word, score in zip(feature_names, mean_tfidf) if score < tfidf_threshold]
    print(f"Nombre de mots peu informatifs, avec un score TF-IDF faible : {len(low_info_words)}")
    print(f"Mots peu informatifs, avec un score TF-IDF faible : {low_info_words}")
    
    # --- Étape 3 : fréquence documentaire pour mots trop fréquents
    vec = CountVectorizer()
    X_count = vec.fit_transform(df['nlp_ready_temp'])
    doc_freq = np.asarray(X_count.sum(axis=0)).ravel() / X_count.shape[0]
    words_high_freq = [word for word, freq in zip(vec.get_feature_names_out(), doc_freq) if freq > high_freq_threshold]
    print(f"Nombre de mots peu informatifs, avec un TF élevé : {len(words_high_freq)}")
    print(f"Mots peu informatifs, avec un TF élevé : {words_high_freq}")

    # Fréquence globale des mots
    text_all = " ".join(df["nlp_ready_temp"].dropna().astype(str))
    words = text_all.split()
    total_words = len(words)
    freq_count = Counter(words)
    freq_with_proportion = {word: (count, count / total_words) for word, count in freq_count.items()}
    sorted_items = sorted(freq_with_proportion.items(), key=lambda x: x[1][0], reverse=True)  # tri sur count décroissant
    
    # Affichage des mots avec proportion >= 0.5% ou count >= 10
    for word, (count, prop) in sorted_items:
        if prop >= 0.005 or count >= 10:
            print(f"{word}: {count} fois, {prop:.2%}")

    # --- Étape 4 : stopwords combinés
    combined_stopwords = STOP_WORDS.union(set(low_info_words)).union(set(words_high_freq))

    # --- Étape 5 : extraire les noms propres PER/GPE/LOC avec spaCy
    all_entities = []
    for doc in nlp.pipe(df['text'], batch_size=20):
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

    #print(f"Liste brute des noms propres: {all_entities}")
    #print(f"Entités nommées avec leurs occurrences : {entity_counts}")
    print(f"Liste nettoyée de noms propres: {proper_nouns_final}")
    print(f"Nombre de noms propres: {len(proper_nouns_final)}")
    
    # --- Étape 6 : reconstruction finale
    df['desc_token'] = df['string'].apply(
        lambda x: [
            token.text if token.text.lower() in proper_nouns_final else token.lemma_.lower()
            for token in nlp(x)
            if token.is_alpha
            and token.text.lower() not in combined_stopwords
            and token.lemma_.lower() not in combined_stopwords
            #and token.text.lower() not in STOP_WORDS
            #and token.lemma_.lower() not in STOP_WORDS
            and (token.pos_ in {"NOUN", "VERB", "ADJ"} or token.text.lower() in proper_nouns_final)
        ]
    )
    df['nlp_ready'] = df['desc_token'].apply(lambda x: ' '.join(x))

    return df


def auto_svd_dim(X, target_var=0.7):
    """
    Détermine le nombre de composantes réduites pour atteindre une variance expliquée cumulée prédéfinie (target_var).
    L'algorithme de réduction de dimensions utilisé est TruncatedSVD.
    """
    
    max_rank = X.shape[1]-1
    svd = TruncatedSVD(n_components=max(2, max_rank), random_state=42)
    svd.fit(X)
    cumvar = np.cumsum(svd.explained_variance_ratio_)
    k = int(np.searchsorted(cumvar, target_var) + 1)
    
    print(f"Nombre de composantes avant réduction de dimension : {X.shape[1]}")
    print(f"Nombre de composantes après réduction de dimension : {k}")
    print(f"Variance expliquée cumulée associée au nombre de composantes k: {cumvar[k]}")
    #print(f"Variance expliquée cumulée associée à chaque nombre de composantes : {cumvar}")

    # Nom complet du fichier PNG à enregistrer
    file_path = os.path.join('/app/data', 'truncatedsvd_variance_cumulee.png')

    # Création et sauvegarde du graphique représentant la variance expliquée cumulée
    plt.plot(cumvar, marker='o')
    plt.axhline(0.7, color='r', linestyle='--', label='70% variance cumulée')
    plt.xlabel('Nombre de composantes')
    plt.ylabel('Variance expliquée cumulée')
    plt.title('Variance cumulée expliquée en fonction du nombre de composantes')
    plt.legend()
    plt.grid(True)
    plt.savefig(file_path, dpi=300)
    plt.close()

    return k


def topic_detection(chunks, n_metatopics=3, n_topwords = 3):
    
    # Nettoyage des chunks
    df_chunks = clean_chunks_strings(chunks)

    # TF-IDF
    vectorizer = TfidfVectorizer(stop_words=None)
    X = vectorizer.fit_transform(df_chunks['nlp_ready'])
    print(f"Taille de la matrice TF-IDF : {X.shape}")

    # Réduction de dimension avec Truncated SVD
    k = auto_svd_dim(X, target_var=0.7)
    svd_model = TruncatedSVD(n_components=k, algorithm='randomized', n_iter=100, random_state=42)
    lsa = svd_model.fit_transform(X)

    # Mots du vocabulaire
    vocab = vectorizer.get_feature_names_out()
    
    # Topics (thèmes latents) dans l'espace du vocabulaire
    components = svd_model.components_

    # Matrice de distances cosine entre topics
    dist_matrix = cosine_distances(components)
    print(f"Matrice de distances cosine entre centroides : {dist_matrix}")
    
    # Clustering des topics
    # On applique l'algo de clustering hiérarchique à la matrice de distances cosine entre topics
    clusterer = AgglomerativeClustering(
			n_clusters=n_metatopics,
			metric='precomputed',   # Indique à l'algo d'utiliser une matrice de distances déjà calculée
			linkage='average'       # alternatives : 'average', 'single'
		)

	# Labels produits par le clustering hiérarchique
    cluster_labels = clusterer.fit_predict(dist_matrix)

    # Ajouter les labels de cluster au df
    df_chunks["cluster"] = cluster_labels
    
	# Statistiques sur les labels
    print(f"Nombre de clusters créés : {len(set(cluster_labels))}")
    print(f"Score de silhouette : {silhouette_score(dist_matrix, cluster_labels, metric='precomputed')}")
    
    # Affichage des k mots clés de chaque méta-topic
    themes = {}
    
    for cluster_id in np.unique(cluster_labels):
        cluster_topics = svd_model.components_[cluster_labels == cluster_id] # les vecteurs topics pour un cluster donné
        avg_topic = cluster_topics.mean(axis=0)  # le vecteur topic moyen
        top_indices = np.argsort(avg_topic)[::-1][:n_topwords]  # les indices des k mots clés
        top_words = [vocab[i] for i in top_indices] # liste des mots clés
        themes[cluster_id] = ", ".join(top_words) if top_words else "(empty)"

    df_chunks["theme"] = df_chunks["cluster"].map(themes)
    
    # Output JSON
    theme_to_json = df_chunks.to_dict(orient="records")
    
    return theme_to_json


def count_chunks_by_theme(data_with_theme):
        theme_list = [d["theme"] for d in data_with_theme]
        theme_counts = Counter(theme_list)
        return dict(theme_counts)