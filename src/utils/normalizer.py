import re
import unicodedata
from collections import Counter

def normalize_text(text: str) -> str:
    text = re.sub(r"([ﬁﬂﬃﬄﬀﬅﬆ])\b\s+([a-zàâçéèêëîïôûùüÿñæœ])", r"\1\2", text, flags=re.IGNORECASE)
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"http\S+|www\S+|@\S+", " ", text)
    text = re.sub(r"\b(\w+)( \1\b)+", r"\1", text)
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = re.sub(r"œ", "oe", text)
    text = re.sub(r"æ", "ae", text)
    text = re.sub(r"([ﬁﬂﬃﬄﬀﬅﬆ])\b\s+([a-zàâçéèêëîïôûùüÿñæœ])", r"\1\2", text, flags=re.IGNORECASE)
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