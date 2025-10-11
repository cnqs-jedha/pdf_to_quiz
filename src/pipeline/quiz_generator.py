import json
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from src.pipeline.prompt_template import build_prompt

load_dotenv()

def create_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.1-8b-instant",
        temperature=0.0,
        max_tokens=None,
        max_retries=2
    )

def generate_quiz_from_chunks(best_chunks, difficulty="standard"):
    llm = create_llm()
    quiz = []

    for chunk in best_chunks:
        prompt =  build_prompt(chunk['page_content'], difficulty)

        try:
            response = llm.invoke(prompt)
            # print(response)
            parsed = json.loads(response.content)

            quiz.append({"question":{
                "llm_response": parsed,
                "metadata": chunk["metadata"]
            }})

        except Exception as e:
            print("ERROR with chunk:", e)
            print(response.content)
            continue

    return quiz