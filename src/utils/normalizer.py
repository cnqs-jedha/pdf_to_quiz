import re
import unicodedata
import spacy
from collections import Counter

# Charger le modèle français de spaCy
nlp = spacy.load("fr_core_news_lg")


def normalize_clusters(text: str) -> str:
    """
    Normalise le texte français pour NLP et embeddings :
    - normalisation Unicode
    - remplacement les 'œ' et 'æ' par 'oe' et 'ae'
    - suppression des URLs
    - remplacement des apostrophes typographiques par des apostrophes simples
    - remplacement des sauts de lignes
    - suppression des caractères indésirables
    - nettoyage des espaces multiples
    - réduction intelligente des répétitions >2
    - identification d'une liste de noms propres
    - lemmatisation et conversion en minuscules, en fonction du type de mot (nom propre vs nom commun)
    """
    
    if not isinstance(text, str):
        return ""
    
    # Normalisation Unicode
    text = unicodedata.normalize("NFKC", text)

    # Remplacer 'œ' par 'oe' et 'æ' par 'ae'
    text = re.sub(r"œ", "oe", text)
    text = re.sub(r"æ", "ae", text)
    
    # Supprimer les URLs
    url_pattern = r'https?://\S+|www\.\S+'
    text = re.sub(url_pattern, "", text)
    
    # Remplacer les apostrophes typographiques (’) par une apostrophe simple (')
    text = text.replace("’", "'")

    # Remplacer les sauts de ligne par un espace simple
    text = re.sub(r"\n+", " ", text)

    # Supprimer tout caractère qui n'est pas lettre, chiffre ou espace
    text = re.sub(r"[^a-zA-ZàâçéèêëîïôûùüÿñÀÂÇÉÈÊËÎÏÔÛÙÜÑ0-9\s]", " ", text)

    # Remplacer les caractères Unicode mal interprétés (ex: "uni25C6") par un espace simple
    text = re.sub(r"uni([0-9A-Fa-f]{4})", " ", text)

    # Remplacer tous types d’espaces Unicode par un espace simple
    text = re.sub(r"\s+", " ", text).strip()
    
    # Réduire les répétitions de lettres >2 → 2
    # ex: "sooooolleil" -> "soolleil", "passé" reste "passé"
    def reduce_repetition(match):
        char = match.group(1)
        return char * 2
    text = re.sub(r"(.)\1{2,}", reduce_repetition, text)
    
    # Définir la liste des entités nommées : noms propres (PER), entités géopolitiques (GPE), lieux géographiques (LOC)
    doc = nlp(text)
    
    list_proper_noun_raw = [
        ent.text for ent in doc.ents 
        if ent.label_ in ["PER", "GPE", "LOC"]
        and ent[0].pos_ != "DET"  # le 1er élément n'est pas un déterminant
    ]

    #print(f"Liste des noms propres brute : {list_proper_noun_raw}")

    # Comptage des occurrences des entités extraites dans le texte
    entity_counts = Counter(list_proper_noun_raw) 
    
    # Fonction qui nettoie la liste brute des noms propres
    def clean_entity(ent):
        text = ent.strip()
        
        # Exclure répétitions excessives (3 fois le même mot ou plus)
        words = text.split()
        if any(words.count(w) > 3 for w in words):
            return None
        
        # Exclure entités trop courtes (sélection sur le nombre de caractères) ou trop longues (sélection sur le nombre de mots) 
        if len(text) <= 3 or len(words) >= 10:
            return None
        
        # Nettoyer espaces multiples
        text = re.sub(r"\s+", " ", text)

        return text

    list_proper_noun = []
    
    for ent in list_proper_noun_raw:
        cleaned = clean_entity(ent)
        if cleaned:
            list_proper_noun.append(cleaned)

    # Comptage des occurrences des entités extraites dans le texte
    entity_counts = Counter(list_proper_noun)
    #print(f"Entités nommées avec leurs occurrences : {entity_counts}")

    # Seuil de sélection : fixé arbitrairement à 5 pour le moment
    threshold_count = 5

    # Filtrer les entités qui ont un nombre d'occurrences supérieur au seuil fixé
    list_proper_noun_final = [
        ent.lower() for ent, count in entity_counts.items() 
        if count >= threshold_count
    ]

    #print(f"Nombre de noms propres retenus : {len(list_proper_noun_final)}")
    #print(f"Liste des noms propres nettoyée (convertis en minuscule): {list_proper_noun_final}")
    
    # Lemmatisation avec spaCy

    lemmatized_tokens = []
    
    for token in doc:
        # Vérifier que le token n'est pas un espace et n'est pas dans la liste des noms propres
        if not token.is_space:
            if token.text.lower() in list_proper_noun_final:
                # Si le token est un nom propre, on le garde tel quel
                lemmatized_tokens.append(token.text)
            else:
                # Sinon, on lemmatise le mot
                lemmatized_tokens.append(token.lemma_.lower())
            
    text = " ".join(lemmatized_tokens)  
    
    return text


def normalize_text(text: str) -> str:
    text = re.sub(r"([ﬁﬂﬃﬄﬀﬅﬆ])\b\s+([a-zàâçéèêëîïôûùüÿñæœ])", r"\1\2", text, flags=re.IGNORECASE)
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^\x20-\x7EÀ-ÖØ-öø-ÿœŒšŠžŽ]+", " ", text)
    text = re.sub(r"http\S+|www\S+|@\S+", " ", text)
    text = re.sub(r"\b\w\b", " ", text)
    text = re.sub(r"-\s*\n", "", text)
    text = re.sub(r"\n", " ", text)
    text = re.sub(r"\bpage\s*\d+\b", " ", text)
    text = re.sub(r"([!?.,;:])\1+", r"\1", text)
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = re.sub(r"[©®™✓§¶∆∞≈≠±×÷]", " ", text)
    text = re.sub(r"œ", "oe", text)
    text = re.sub(r"æ", "ae", text)
    text = re.sub(r"\b(\w+)( \1\b)+", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text