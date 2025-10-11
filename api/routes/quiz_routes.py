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

# Contacter l'api pour lancer la pipeline
@router.post("/run_pipeline")
def run_pipeline(req: dict):
    drive_link = req.get("drive_link")
    if not drive_link:
        raise HTTPException(status_code=400, detail="drive_link manquant")

    print("🛰️ Appel du service pipeline...")

    try:
        # Appel rapide vers le conteneur pipeline
        r = requests.post(
            "http://pipeline:8001/execute",
            json={"drive_link": drive_link},
            timeout=10  # on limite le temps d’attente à 10s max
        )
        if r.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Erreur pipeline : {r.text}")
    except Exception as e:
        print(f"❌ Erreur pipeline : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur connexion pipeline : {e}")

    print("✅ Pipeline lancé avec succès")
    return {"status": "ok", "message": "Pipeline lancé"}
