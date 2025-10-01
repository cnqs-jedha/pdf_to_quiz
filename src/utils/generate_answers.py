import json
import time
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from src.pipeline.quiz_generator import create_llm

# Charger les variables d'environnement
load_dotenv()

# Définir les chemins
UTILS_DIR = r"D:\Profils\NLefort\Desktop\JEDHA\pdf_to_quiz\src\utils"
REF_FILE = os.path.join(UTILS_DIR, "references.json")
GEN_FILE = os.path.join(UTILS_DIR, "generated.json")

# Créer l'instance du LLM
llm = create_llm()

# Charger les questions
with open(REF_FILE, "r", encoding="utf-8") as f:
    questions = json.load(f)

results = []
for q in questions:
    question_text = q["question"]

    # Construire le prompt
    prompt = ChatPromptTemplate.from_messages(
        [("system", "Tu es un professeur d'histoire d'une classe de CM1. Réponds de façon claire et concise."),
         ("human", question_text)]
    )

    # Appeler le modèle
    response = llm.invoke(prompt.format())
    answer = response.content if hasattr(response, "content") else str(response)

    print(f"Q{q['id']}: {question_text}")
    print(f" -> Réponse LLM: {answer}\n")

    results.append({"id": q["id"], "generated": answer})

    time.sleep(1)  # éviter de spammer l'API

# Sauvegarder les réponses
with open(GEN_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Réponses sauvegardées dans {GEN_FILE}")
