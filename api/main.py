from fastapi import FastAPI, Request
from pydantic import BaseModel
#from src.pipeline.run import main
import json

app = FastAPI()
app.state.last_received_quiz = None
app.state.quiz_history = []

# Send the quiz
@app.post("/send_quiz")
async def receive_quiz(request: Request):
    data = await request.json()
    app.state.last_received_quiz = data
    app.state.quiz_history.append(data)
    return {"message": "Quiz bien reçu", "total_quizzes": len(app.state.quiz_history)}

# The quiz
@app.get("/quiz")
def get_last_quiz():
    if app.state.last_received_quiz:
        return app.state.last_received_quiz
    return {"quiz": []}


"""@app.get("/quiz")
def get_last_quiz():
    if last_received_quiz and (
        ("quiz" in last_received_quiz) or isinstance(last_received_quiz, list)
    ):
        return last_received_quiz
    return {"quiz": []}"""

# Alive
@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}

# Quiz is ready to gradio ?
@app.get("/ready", include_in_schema=False)
def ready():
    if app.state.last_received_quiz and len(app.state.last_received_quiz.get("quiz", [])) > 0:
        return {
            "status": "ok",
            "quiz_count": len(app.state.last_received_quiz["quiz"])
        }
    return {"status": "error", "reason": "quiz vide"}, 500

# Clean the api quiz
@app.post("/clear")
def clear_quiz():
    app.state.last_received_quiz = None
    app.state.quiz_history = []
    return {"message": "Quiz réinitialisé"}

# Quiz history
@app.get("/history")
def get_history():
    return {"history": app.state.quiz_history[-10:]}