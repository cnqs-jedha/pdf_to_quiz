import json
import os
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics import precision_score
from scipy.stats import spearmanr
import nltk
from nltk.tokenize import sent_tokenize

# Télécharger les ressources NLTK si nécessaire
nltk.download("punkt")
nltk.download("punkt_tab")

# Définir les chemins
UTILS_DIR = r"D:\Profils\NLefort\Desktop\JEDHA\pdf_to_quiz\src\utils"
REF_FILE = os.path.join(UTILS_DIR, "references.json")
GEN_FILE = os.path.join(UTILS_DIR, "generated.json")
OUTPUT_CSV = os.path.join(UTILS_DIR, "evaluation_report.csv")

# Charger les données
with open(REF_FILE, "r", encoding="utf-8") as f:
    references = {item["id"]: item for item in json.load(f)}

with open(GEN_FILE, "r", encoding="utf-8") as f:
    generated = {item["id"]: item["generated"] for item in json.load(f)}

# Paramètres du modèle d'embeddings
MODEL_NAME = "all-MiniLM-L6-v2" # mini-BERT performant et rapide
model = SentenceTransformer(MODEL_NAME)
THRESHOLD = 0.63  # seuil de décision

def chunk_and_compare(gen_resp, ref_texts, model):
    """Découpe une réponse générée en phrases et prend la meilleure similarité avec les références."""
    chunks = sent_tokenize(gen_resp)
    if not chunks:  # fallback si rien
        chunks = [gen_resp]

    emb_refs = model.encode(ref_texts, convert_to_numpy=True, normalize_embeddings=True)

    best_score = 0
    best_chunk = None

    for chunk in chunks:
        emb_chunk = model.encode(chunk, convert_to_numpy=True, normalize_embeddings=True)
        cos_sims = np.dot(emb_refs, emb_chunk)
        score = float(np.max(cos_sims))
        if score > best_score:
            best_score = score
            best_chunk = chunk

    return best_score, best_chunk

# Calcul des similarités
rows, scores, true_labels, pred_labels, human_scores = [], [], [], [], []

for qid, ref in references.items():
    if qid not in generated:
        print(f"Pas de réponse générée pour la question {qid}")
        continue

    gen_resp = generated[qid]

    # Chunking + comparaison
    best_score, best_chunk = chunk_and_compare(gen_resp, ref["references"], model)
    scores.append(best_score)

    # Labels humains
    if "label" in ref:
        true_labels.append(ref["label"])
        pred_labels.append(int(best_score >= THRESHOLD))
        human_scores.append(ref["label"])

    # Ligne pour CSV
    rows.append({
        "id": qid,
        "question": ref["question"],
        "generated": gen_resp,
        "best_chunk": best_chunk,
        "cosine_score": round(best_score, 3),
        "correct_pred": int(best_score >= THRESHOLD)
    })

    print(f"Q{qid} | Généré: {gen_resp}")
    print(f"   -> Best chunk: {best_chunk}")
    print(f"   -> Similarité max = {best_score:.3f}\n")

# Statistiques globales
mean_cos = np.mean(scores)
print("\n=== Résultats globaux ===")
print(f"Mean cosine similarity : {mean_cos:.3f}")

if true_labels:
    accuracy = np.mean(np.array(pred_labels) == np.array(true_labels))
    precision = precision_score(true_labels, pred_labels, zero_division=0)
    print(f"Accuracy (seuil={THRESHOLD}): {accuracy:.3f}")
    print(f"Précision: {precision:.3f}")


# Sauvegarde CSV
df = pd.DataFrame(rows)
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
print(f"\n Rapport sauvegardé dans {OUTPUT_CSV}")
