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

def generate_quiz_from_chunks(strings_by_theme, themes, difficulty="standard"):
    llm = create_llm()
    quiz = []

    for i, (context_text, theme) in enumerate(zip(strings_by_theme, themes)):
        #print(string)
        prompt = build_prompt(context_text, theme, difficulty)

        try:
            response = llm.invoke(prompt)
            parsed = json.loads(response.content)
            quiz.append(parsed)
        except Exception as e:
            print(f"Erreur chunk {i+1}: {e}")
            print(response.content[:200])
            continue
    
    return quiz