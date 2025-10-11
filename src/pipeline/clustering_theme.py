import fr_core_news_lg
import spacy
from spacy.lang.fr.stop_words import STOP_WORDS
#from spacy.lang.fr.stop_words import STOP_WORDS as FR_STOPS

import matplotlib
matplotlib.use('Agg') # Forcer matplotlib à utiliser un backend non interactif (Agg)
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances, cosine_similarity
from sklearn.metrics import silhouette_score
from sklearn.cluster import AgglomerativeClustering
import hdbscan
from sklearn.preprocessing import normalize
from collections import Counter
import re

#from src.utils.normalizer import normalize_text

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
    print(f"Entités nommées avec leurs occurrences : {entity_counts}")
    print(f"Liste nettoyée de noms propres: {proper_nouns_final}")
    print(f"Nombre de noms propres: {len(proper_nouns_final)}")
    
    # --- Étape 6 : reconstruction finale
    df['desc_token'] = df['string'].apply(
        lambda x: [
            token.text if token.text.lower() in proper_nouns_final else token.lemma_.lower()
            for token in nlp(x)
            if token.is_alpha
            #and token.text.lower() not in combined_stopwords
            #and token.lemma_.lower() not in combined_stopwords
            and token.text.lower() not in STOP_WORDS
            and token.lemma_.lower() not in STOP_WORDS
            and (token.pos_ in {"NOUN", "VERB", "ADJ"} or token.text.lower() in proper_nouns_final)
        ]
    )
    df['nlp_ready'] = df['desc_token'].apply(lambda x: ' '.join(x))

    return df

#Trouver automatiquement la dimension du svd
'''
def auto_svd_dim(X, target_var=0.7, min_dim=5, max_dim=300):
    max_rank = min(X.shape[0]-1, X.shape[1]-1)
    probe = min(max_dim, max_rank)
    print(f"Nombre de composantes avant réduction de dimension : {X.shape[1]}")
    print(f"TruncatedSVD réalisée sur un nombre de composantes égal à : {max(2, probe)}")
    svd_probe = TruncatedSVD(n_components=max(2, probe), random_state=42)
    svd_probe.fit(X)
    cumvar = np.cumsum(svd_probe.explained_variance_ratio_)
    k = int(np.searchsorted(cumvar, target_var) + 1)
    print(f"Nombre k de composantes qui permet d'attendre une variance cumulée de 70%: {k}")
    print(f"Variance expliquée cumulée associée au nombre de composantes k: {cumvar[k]}")
    k = max(min_dim, min(k, probe))
    print(f"Nombre de composantes retenues : {k}")
    return k
'''
def auto_svd_dim(X, target_var=0.7):
    
    """
    Détermine le nombre de composantes réduites (Truncated SVD) associée à une variance expliquée cumulée prédéfinie (target_var)
    """
    max_rank = X.shape[1]-1
    svd = TruncatedSVD(n_components=max(2, max_rank), random_state=42)
    svd.fit(X)
    cumvar = np.cumsum(svd.explained_variance_ratio_)
    k = int(np.searchsorted(cumvar, target_var) + 1)
    print(f"Nombre de composantes avant réduction de dimension : {X.shape[1]}")
    print(f"Nombre de composantes après réduction de dimension : {k}")
    print(f"Variance expliquée cumulée associée au nombre de composantes k: {cumvar[k]}")
    print(f"Variance expliquée cumulée associée à chaque nombre de composantes : {cumvar}")
    
    # Chemin absolu vers le dossier /app/data
    data_dir = '/app/data'

    # Nom complet du fichier PNG à enregistrer
    file_path = os.path.join(data_dir, 'truncatedsvd_variance_cumulee.png')

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
            vectorizer = TfidfVectorizer(max_features=500, 
                                        ngram_range=(1, 2)
                                        )
            X = vectorizer.fit_transform(cluster_texts)
            scores = X.mean(axis=0).A1
            words = vectorizer.get_feature_names_out()
            top_words = [w for w, _ in sorted(zip(words, scores), key=lambda x: x[1], reverse=True)[:top_n]]
            themes[cluster_id] = ", ".join(top_words) if top_words else "(empty)"
        except ValueError:
            themes[cluster_id] = "(empty)"

    return themes


target_topics = 3
        
def merge_close_clusters(df, embeddings, cluster_col="hdb_cluster", target_topics=target_topics):
    """
    Fusionne les clusters proches en utilisant la similarité cosinus de leurs centroïdes (non normalisés),
    dans l'espace des embeddings (SVD normalisés).
    Fusion réalisée par clustering hiérarchique, qui agrège les centroïdes les plus proches, jusqu'à atteindre
    le nombre cible de clusters (target_topics)
    """

	#Calculer les centroïdes des clusters HDBSCAN, hors cluster qui contient du bruit
    centroids = []
    cluster_ids = []

    for cluster_id in df[cluster_col].unique():

		# Exclut le cluster contenant du bruit
        if cluster_id == -1:
            continue
			
        mask = df[cluster_col] == cluster_id
		
		# Exclut les clusters avec des embeddings nuls
        if mask.sum() == 0:
            continue
			
		# Coordonnées moyennes d'un cluster : Numpy array de taille égale au nb de dimensions réduites par TruncatedSVD
        centroid_vec = embeddings[mask].mean(axis=0) 
		
		# Ajoute le vecteur et l'id du cluster traité aux listes de centroids et d'id
        centroids.append(centroid_vec)
        cluster_ids.append(cluster_id)
		
	# Numpy array qui empile les coordonnées moyennes de tous les clusters
    centroids = np.vstack(centroids)
    print(f"Centroides des clusters HDBSCAN : {centroids}")

	# Calcule la matrice de distances cosine entre centroïdes 
	# Matrice qui mesure la dissimilarité entre vecteurs. Mmatrice carrée de taille égale au nb de clusters HDBSCAN
    dist_matrix = cosine_distances(centroids)
    print(f"Matrice de distances cosine entre centroides : {dist_matrix}")

	# Appliquer l'algorithme de clustering hiérarchique sur la matrice de distances cosine
	# L'algorithme attend en entrée un nombre défini de clusters ; on lui passe le nombre cible de clusters (target_k)
    hierarchical_clusterer = AgglomerativeClustering(
			n_clusters=target_topics,
			metric='precomputed',  # Indique à l'algo d'utiliser une matrice déjà calculée.
			linkage='complete'       # alternatives : 'average', 'single'
		)

	# Labels produits par le clustering hiérarchique (valeurs comprises entre 0 et target_k - 1)
    labels_hierarchical_clusterer = hierarchical_clusterer.fit_predict(dist_matrix)

	# Correspondance entre les anciens labels définis par HDBSCAN et les nouveaux labels définis par clustering hiérarchique
    correspondance_labels = {label_hdbscan: labels_hierarchical_clusterer[i] for i, label_hdbscan in enumerate(cluster_ids)}
    print(f"Correspondance entre labels HDBSCAN et labels de clustering hiérarchique : {correspondance_labels}")

	# Créer une nouvelle colonne 'cluster_merge' en utilisant cette correspondance
	# On attribue le label -1 aux labels HDBSCAN absents du dictionnaire de correspondances
    df['merged_cluster'] = df[cluster_col].map(lambda c: correspondance_labels.get(c, -1))

	# Vérifier les valeurs de cluster_merge
    print(f"Valeurs prises par 'merged_cluster' : df['merged_cluster'].unique()")
    print(f"merged_cluster contient {df['merged_cluster'].isna().sum()} valeurs manquantes")
    
    return df

'''
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
        print(f"type centroid : {type(centroids[cluster_id])}")
        print(f"dimension du centroid : {len(centroids[cluster_id])}")

    if not centroids:
        return df, {}

    ids = list(centroids.keys())
    print(f"ids : {ids}")
    centroid_matrix = np.vstack([centroids[i] for i in ids])
    sims = cosine_similarity(centroid_matrix)
    print(f"Matrice de similarité entre centroides :\n{sims}")

    # Union-find pour fusionner
    parent = {cid: cid for cid in ids}
    print(f"Affectation clusters avant regroupement : {parent}")

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
    print(f"Affectation clusters après regroupement : {parent}")
    df["merged_cluster"] = df[cluster_col].apply(lambda c: find(c) if c in parent else c)
    return df, parent
'''

#def hdbscan_clustering(chunks, merge_clusters=True, sim_threshold=threshold):
def hdbscan_clustering(chunks, merge_clusters=True):
    
    # Nettoyage
    df_chunks = clean_chunks_strings(chunks)

    # TF-IDF
    vectorizer = TfidfVectorizer(stop_words=None)
    X = vectorizer.fit_transform(df_chunks['nlp_ready'])
    print(f"Taille de la matrice TF-IDF : {X.shape}")

    # SVD
    #k = auto_svd_dim(X, target_var=0.7, min_dim=5, max_dim=300)
    k = auto_svd_dim(X, target_var=0.7)
    svd_model = TruncatedSVD(n_components=k, algorithm='randomized', n_iter=100, random_state=42)
    lsa = svd_model.fit_transform(X)

    # Normalisation
    X_norm = normalize(lsa)

    # Clustering
    n_samples = len(X_norm)
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=max(5, n_samples // 100), # à quoi sert n_samples // 100 ? n_samples correspond au nb de chunks
        min_samples=1,
        metric='euclidean',
        cluster_selection_method='eom',
        cluster_selection_epsilon=0.03
    )
    labels = clusterer.fit_predict(X_norm)
    df_chunks['hdb_cluster'] = labels
    
    print(f"min_cluster_size : {max(5, n_samples // 100)}")
    print(f"Nombre de clusters créés sans le bruit : {len(set(labels)) - (1 if -1 in labels else 0)}")
    mask = labels != -1
    X_norm_without_noise = X_norm[mask]
    labels_without_noise = labels[mask]
    print(f"Score de silhouette : {silhouette_score(X_norm_without_noise, labels_without_noise, metric='cosine')}")
    print(f"Nb chunks dans le cluster outliers : {np.sum(labels == -1)}")    
    print(f"Prct d'outliers : {np.sum(labels == -1)/len(labels)*100} %")
    print(f"Nb chunks dans chaque cluster: {df_chunks['hdb_cluster'].value_counts()}")


    # Fusion optionnelle
    if merge_clusters:
        df_chunks, merged_map = merge_close_clusters(
            df_chunks,
            embeddings=X_norm,
            cluster_col="hdb_cluster",
            target_topics = target_topics
            #sim_threshold=sim_threshold
        )
        final_col = "merged_cluster"
    else:
        final_col = "hdb_cluster"


    # Extraction des thèmes
    themes = extract_top_keywords(df_chunks, cluster_col=final_col, text_col="nlp_ready", top_n=3)
    df_chunks['theme'] = df_chunks[final_col].map(themes)

    # Output JSON
    theme_to_json = df_chunks.drop(columns=["hdb_cluster", "nlp_ready", 
                                            "merged_cluster", 
                                            "desc_token_temp", "nlp_ready_temp", "string", "desc_token"]).to_dict(orient="records")
    return theme_to_json


def count_chunks_by_theme(data_with_theme):
        theme_list = [d["theme"] for d in data_with_theme]
        theme_counts = Counter(theme_list)
        return dict(theme_counts)