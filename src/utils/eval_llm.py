import json
import time
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from src.pipeline.quiz_generator import create_llm
from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics import precision_score
from scipy.stats import spearmanr

load_dotenv()

# Créer l'instance du LLM
llm = create_llm()

# Définir les chemins des fichiers
# Définir les chemins une seule fois
UTILS_DIR = r"D:\Profils\NLefort\Desktop\JEDHA\pdf_to_quiz\src\utils"
REF_FILE = os.path.join(UTILS_DIR, "references.json")
GEN_FILE = os.path.join(UTILS_DIR, "generated.json")
OUTPUT_CSV = os.path.join(UTILS_DIR, "evaluation_report.csv")


# Charger les questions
## chemin absolu vers le dossier du script
script_dir = os.path.dirname(os.path.abspath(__file__))
REF_FILE = os.path.join(script_dir, "references.json")

with open(REF_FILE, "r", encoding="utf-8") as f:
    questions = json.load(f)


results = []
for q in questions:
    question_text = q["question"]

    # prompt simple (tu peux raffiner avec build_prompt si tu veux un format spécial)
    prompt = ChatPromptTemplate.from_messages(
        [("system", "Tu es un professeur d'histoire d'une classe de CM1. Réponds de façon claire et concise."),
         ("human", question_text)]
    )

    # exécution
    response = llm.invoke(prompt.format()) #invoke = appeler le modèle
    # voir si on peut limiter en taille ou autre
    """max_tokens = 1024
    if hasattr(response, "content"):
        response.content = response.content[:max_tokens]"""

    # récupérer le texte
    answer = response.content if hasattr(response, "content") else str(response)

    print(f"Q{q['id']}: {question_text}")
    print(f" -> Réponse LLM: {answer}\n")

    results.append({"id": q["id"], "generated": answer})

    time.sleep(1)  # éviter de spammer l’API


# chemin absolu vers le dossier du script
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "generated.json")
# Sauvegarder les réponses
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Réponses sauvegardées dans {file_path}")

# Evaluation des réponses
MODEL_NAME = "all-MiniLM-L6-v2"  # Sentence-BERT léger
THRESHOLD = 0.63  # seuil pour dire "correct" avec la similarité cosinus. (à ajuster selon besoin)


# Charger les données
with open(REF_FILE, "r", encoding="utf-8") as f:
    references = {item["id"]: item for item in json.load(f)}

with open(GEN_FILE, "r", encoding="utf-8") as f:
    generated = {item["id"]: item["generated"] for item in json.load(f)}


# Modèle d'embeddings
model = SentenceTransformer(MODEL_NAME)


# Calcul des similarités
rows = []
scores = []
true_labels = []
pred_labels = []
human_scores = []

for qid, ref in references.items():
    if qid not in generated:
        print(f"Pas de réponse générée pour la question {qid}")
        continue

    gen_resp = generated[qid]

    # embeddings
    emb_gen = model.encode(gen_resp, convert_to_numpy=True, normalize_embeddings=True)
    emb_refs = model.encode(ref["references"], convert_to_numpy=True, normalize_embeddings=True)

    # max cosinus entre réponse générée et toutes les références
    cos_sims = np.dot(emb_refs, emb_gen)
    best_score = float(np.max(cos_sims))
    scores.append(best_score)

    # utilisation des labels humains
    if "label" in ref:
        true_labels.append(ref["label"])
        pred_labels.append(int(best_score >= THRESHOLD))
        human_scores.append(ref["label"])

    # ligne pour CSV
    best_ref = ref["references"][int(np.argmax(cos_sims))]
    rows.append({
        "id": qid,
        "question": ref["question"],
        "generated": gen_resp,
        "best_reference": best_ref,
        "cosine_score": round(best_score, 3),
        "correct_pred": int(best_score >= THRESHOLD)
    })

    print(f"Q{qid} | Généré: {gen_resp}")
    print(f"   -> Best ref: {best_ref}")
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

    rho, pval = spearmanr(scores, human_scores)
    print(f"Spearman corr (avec labels humains): rho={rho:.3f}, p={pval:.3f}")

# Sauvegarde CSV
df = pd.DataFrame(rows)
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
print(f"\n Rapport sauvegardé dans {OUTPUT_CSV}")

## Reste à faire :
# - Enrichir le referencences.json
# - Tester sur un autre modèle
# - Chunker les réponses longues et comparer partie par partie
# - regex pour réponses numériques (dates, chiffres, etc.)
# - Rendre le script plus modulaire