from fastapi import APIRouter, Request, HTTPException
import os
import subprocess
import requests
from fastapi.responses import JSONResponse
from api.models.quiz_models import Quiz, QuizResponse, PipelineRequest, PipelineRequest
from api.utils.quiz_manager import add_quiz, get_last_quiz

"""
===========================================================
ROUTES PRINCIPALES - Quiz (quiz_routes)
===========================================================

Ce module gère toutes les routes principales relatives aux quiz :
- POST /send_quiz → reçoit un quiz depuis un service externe (ex : pipeline)
- GET /quiz → renvoie le dernier quiz reçu
- POST /run_pipeline → déclenche l’exécution du pipeline via un lien Google Drive

Les fonctions de ce module utilisent les modèles définis dans `quiz_models`
et les fonctions d’état global définies dans `utils/quiz_manager`.

Responsabilités :
- Valider les données entrantes avec Pydantic.
- Mettre à jour l’état global de l’application (dernier quiz, historique).
- Communiquer avec le conteneur pipeline externe pour lancer la génération de quiz.

Toutes les routes sont regroupées sous le tag "Quiz" pour la documentation Swagger.
"""

router = APIRouter(tags=["Quiz"])

# Envoie le quiz à l'api
@router.post("/send_quiz", response_model=QuizResponse)
async def receive_quiz(request: Request, quiz: Quiz):
    """"
    Reçoit un quiz depuis un service externe (comme le pipeline)
    et l'ajoute à l'historique de l'application.

    Args:
        request (Request): Contexte de la requête FastAPI.
        quiz (Quiz): Données du quiz envoyées par le client.

    Returns:
        QuizResponse: Confirmation de réception avec le nombre total de quiz enregistrés.
    """
    add_quiz(request.app, quiz.dict())
    return {"message": "Quiz bien reçu", "total_quizzes": len(request.app.state.quiz_history)}

# Lire le quiz
@router.get("/quiz", response_model=Quiz)
def get_quiz(request: Request):
    """
    Retourne le dernier quiz enregistré.

    Args:
        request (Request): Contexte de la requête FastAPI.

    Returns:
        Quiz: Le dernier quiz reçu, ou un quiz vide si aucun n'a été reçu.
    """
    return get_last_quiz(request.app)

# Contacter l'api pour lancer la pipeline
@router.post("/run_pipeline")
def run_pipeline(req: PipelineRequest):
    """
    Déclenche l'exécution du pipeline d'analyse à partir d'un lien Google Drive.

    Cette route envoie une requête HTTP vers le conteneur `pipeline`
    (par défaut : `http://pipeline:8001/execute`) pour lancer la génération du quiz.

    Args:
        req (PipelineRequest): Corps de la requête contenant le lien Google Drive.

    Returns:
        dict: Message de confirmation de lancement du pipeline.

    Raises:
        HTTPException: Si le champ `drive_link` est manquant ou si le pipeline ne répond pas.
    """
    drive_link = req.drive_link
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
