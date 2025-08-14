import json
import time
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from prompt_template import build_prompt

load_dotenv()

def create_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.1-8b-instant",
        temperature=0.0,
        max_tokens=None,
        max_retries=2
    )

def generate_quiz_from_chunks(vector_db_data, difficulty="standard"):
    llm = create_llm()
    quiz = []
    total_duration = 0

    for i, doc in enumerate(vector_db_data["documents"]):
        print(doc)
        start = time.time()
        prompt = build_prompt(doc, difficulty)

        try:
            response = llm.invoke(prompt)
            parsed = json.loads(response.content)
            quiz.append(parsed)
        except Exception as e:
            print(f"Erreur chunk {i+1}: {e}")
            print(response.content[:200])
            continue

        end = time.time()
        print(f"{i+1}: {round(end - start, 2)}s")
        total_duration += (end - start)

    print("Durée totale :", round(total_duration, 2), "s")
    return quiz
