from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from api.models.quiz_models import HealthResponse, ReadyResponse

"""
===========================================================
ROUTES DE SANTÉ ET DE READINESS (health_routes)
===========================================================

Ce module définit les routes de vérification de l’état de l’API.

Routes :
- GET /health → indique si l’API est en ligne (simple ping).
- GET /ready → retourne l’état de préparation du pipeline ou du quiz.
- POST /ready → met à jour le message d’état envoyé par le pipeline.

Ces endpoints permettent à un client
de vérifier la disponibilité et la progression du pipeline.
"""

router = APIRouter(tags=["Health"])

# Pour vérifier que l'api est en vie
@router.get("/health", response_model=HealthResponse)
def health():
    """Vérifie que l'API est en ligne."""
    return {"status": "ok"}

# Envoie des message d'information du traitement des données par pipeline et quand la génération du quiz est finie
@router.post("/ready")
async def update_ready(request: Request, data: dict):
    """Mise à jour du message de progression envoyée par le pipeline."""
    message = data.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Champ 'message' manquant")
    
    # On stocke le message dans l'état global de l'app
    request.app.state.status_message = message
    print(f"📩 Nouveau message reçu du pipeline : {message}", flush=True)
    
    return {"status": "ok", "message": message}

# Pour lire ready et pas jsute envoyer des infos
@router.get("/ready")
def get_ready(request: Request):
    """Retourne l'état de readiness + message du pipeline."""
    message = getattr(request.app.state, "status_message", "En attente de génération...")

    last_quiz = getattr(request.app.state, "last_received_quiz", None)
    if last_quiz and len(last_quiz.get("quiz", [])) > 0:
        return {"status": "ok", "quiz_count": len(last_quiz["quiz"]), "message": message}

    return JSONResponse(
        status_code=200,
        content={"status": "pending", "quiz_count": 0, "message": message}
    )