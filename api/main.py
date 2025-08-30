from fastapi import FastAPI, Request
from pydantic import BaseModel
#from src.pipeline.run import main
import json

app = FastAPI()
last_received_quiz = None

@app.post("/api/send_quiz")
async def receive_quiz(request: Request):
    global last_received_quiz
    data = await request.json()
    last_received_quiz = data
    #print("Quiz reçu :", data)
    return {"message": "Quiz bien reçu"}

@app.get("/api/quiz")
def get_last_quiz():
    if last_received_quiz:
        return last_received_quiz
    return {"message": "Aucun quiz reçu pour le moment"}
