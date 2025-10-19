import re
import unicodedata
import spacy
from collections import Counter

# Charger le modèle français de spaCy
nlp = spacy.load("fr_core_news_lg")

# def normalize_text(text: str) -> str:
#     text = re.sub(r"([ﬁﬂﬃﬄﬀﬅﬆ])\b\s+([a-zàâçéèêëîïôûùüÿñæœ])", r"\1\2", text, flags=re.IGNORECASE)
#     text = unicodedata.normalize("NFKC", text)
#     text = re.sub(r"<[^>]+>", " ", text)
#     text = re.sub(r"[^\x20-\x7EÀ-ÖØ-öø-ÿœŒšŠžŽ]+", " ", text)
#     text = re.sub(r"http\S+|www\S+|@\S+", " ", text)
#     # text = re.sub(r"\b\w\b", " ", text)
#     text = re.sub(r"-\s*\n", "", text)
#     text = re.sub(r"\n", " ", text)
#     text = re.sub(r"\bpage\s*\d+\b", " ", text)
#     text = re.sub(r"([!?.,;:])\1+", r"\1", text)
#     text = text.replace("’", "'").replace("‘", "'")
#     text = text.replace("“", '"').replace("”", '"')
#     text = re.sub(r"[©®™✓§¶∆∞≈≠±×÷]", " ", text)
#     text = re.sub(r"œ", "oe", text)
#     text = re.sub(r"æ", "ae", text)
#     text = re.sub(r"\b(\w+)( \1\b)+", r"\1", text)
#     text = re.sub(r"\s+", " ", text).strip()

#     return text

def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)  # normalise le texte Unicode (unification des caractères équivalents)
    text = re.sub(r"/uni[0-9A-Fa-f]{4}\s*", " ", text) # supprime les séquences comme /uniXXXX (où XXXX est hexadécimal).
    text = re.sub(r"<[^>]+>", " ", text)  # supprime les balises HTML/XML
    text = re.sub(r"\[\s*\.\.\.\s*\]", "", text) # retrait de [...]
    text = text.replace("’", "'").replace("‘", "'")  # remplace les apostrophes typographiques par des apostrophes simples
    text = text.replace("“", '"').replace("”", '"')  # remplace les guillemets typographiques par des guillemets simples
    text = re.sub(r"[^\x20-\x7EÀ-ÖØ-öø-ÿœŒšŠžŽ]+", " ", text)  # supprime les caractères non imprimables ou hors alphabet latin étendu
    text = re.sub(r"http\S+|www\S+|@\S+", " ", text) # Supprime les URLs et les mentions Twitter
    text = re.sub(r"\s+", " ", text).strip() # # Remplace tous types d’espaces Unicode par un espace simple (ex : espaces insécables)
    #text = re.sub(r"\b\w\b", " ", text) # supprime les mots d'un caractère => commenté ici car il faut garder tous les mots pour le chunking. L'instruction est basculée das clustering_theme
    text = re.sub(r"-\s*\n", "", text) # supprime les coupures de mots en fin de ligne (- suivi de saut de ligne)
    text = re.sub(r"\n", " ", text)  # remplace les sauts de ligne par des espaces
    text = re.sub(r"\bpage\s*\d+\b", " ", text)  # supprime les mentions de pages
    text = re.sub(r"([!?.,;:])\1+", r"\1", text)  # réduit les ponctuations répétées
    #text = text.replace("’", "'").replace("‘", "'")  
    #text = text.replace("“", '"').replace("”", '"')
    text = re.sub(r"[©®™✓§¶∆∞≈≠±×÷]", " ", text)  # remplace des symboles non pertinents pour l’analyse par des espaces
    text = re.sub(r"([ﬁﬂﬃﬄﬀﬅﬆ])\b\s+([a-zàâçéèêëîïôûùüÿñæœ])", r"\1\2", text, flags=re.IGNORECASE)  # traite les ligatures suivies d'un mot
    text = re.sub(r"œ", "oe", text)
    text = re.sub(r"æ", "ae", text)
    text = re.sub(r"\b(\w+)( \1\b)+", r"\1", text)  # supprime les doublons consécutifs d’un même mot
    text = re.sub(r"\s+", " ", text).strip()  # nettoie les espaces

    return text

def normalize_keywords(keywords):
    """
    Supprime les redondances de mots, dans un groupe de mots, en fonction de leur forme lemmatisée
    Input : keywords (string)
    Ouput : set de keywords sans redondance
    """
    keywords_clean = {}
    for word in keywords:
        token = nlp(word)
        lemma = token[0].lemma_  # la forme lemmatisée du token
        if lemma not in keywords_clean:
            keywords_clean[lemma] = word  # ajouter le mot si c'est la première fois qu'on rencontre sa forme lemmatisée
    return set(keywords_clean.values())
    

def normalize_list_keywords(list_raw):
    """
    Supprime les redondances de mots, dans une liste de groupe de mots, en fonction de leur forme lemmatisée
    Input : list_raw (liste): liste de groupe de mots
    Output : liste de groupes de mots nettoyée
    """
    list_clean=[]
    for group in list_raw:
        words = [word.strip() for word in group.split(',')]
        words_normalized = normalize_keywords(words)
        words_chained = ", ".join(sorted(words_normalized))
        list_clean.append(words_chained)
    return list_clean