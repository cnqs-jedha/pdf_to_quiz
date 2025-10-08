from fastapi import APIRouter, Request, HTTPException
import os
import subprocess
import requests
from fastapi.responses import JSONResponse
from api.models.quiz_models import Quiz, QuizResponse, PipelineRequest
from api.utils.quiz_manager import add_quiz, get_last_quiz

router = APIRouter(tags=["Quiz"])

@router.post("/send_quiz", response_model=QuizResponse)
async def receive_quiz(request: Request, quiz: Quiz):
    """Enregistre un quiz envoyé par un client."""
    add_quiz(request.app, quiz.dict())
    return {"message": "Quiz bien reçu", "total_quizzes": len(request.app.state.quiz_history)}

@router.get("/quiz", response_model=Quiz)
def get_quiz(request: Request):
    """Récupère le dernier quiz envoyé."""
    return get_last_quiz(request.app)

@router.post("/run_pipeline")
def run_pipeline(req: dict):
    drive_link = req.get("drive_link")
    if not drive_link:
        raise HTTPException(status_code=400, detail="drive_link manquant")

    print("📡 Appel du service pipeline...")
    r = requests.post("http://pipeline:8001/execute", json={"drive_link": drive_link})

    if r.status_code != 200:
        raise HTTPException(status_code=500, detail="Erreur d’exécution du pipeline")

    return {"status": "ok", "message": "Pipeline lancé"}
