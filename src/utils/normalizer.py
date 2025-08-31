import re
import unicodedata
import spacy

# Charger le modèle français de spaCy
nlp = spacy.load("fr_core_news_sm")

def normalize_text(text: str) -> str:
    """
    Normalise le texte français pour NLP et embeddings :
    - minuscules
    - normalisation Unicode
    - suppression des caractères indésirables
    - réduction intelligente des répétitions >2
    - lemmatisation
    - nettoyage des espaces multiples
    """
    if not isinstance(text, str):
        return ""

    # Minuscules et normalisation Unicode
    text = text.lower()
    text = unicodedata.normalize("NFKC", text)

    # Supprimer tout caractère qui n'est pas lettre, chiffre ou espace
    text = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ0-9\s]", " ", text)

    # Réduire les répétitions de lettres >2 → 2
    # ex: "sooooolleil" -> "soolleil", "passé" reste "passé"
    def reduce_repetition(match):
        char = match.group(1)
        return char * 2
    text = re.sub(r"(.)\1{2,}", reduce_repetition, text)

    # Lemmatisation avec spaCy
    doc = nlp(text)
    lemmatized_tokens = [token.lemma_ for token in doc if not token.is_space]
    text = " ".join(lemmatized_tokens)

    # Supprimer les espaces multiples
    text = re.sub(r"\s+", " ", text).strip()

    return text
