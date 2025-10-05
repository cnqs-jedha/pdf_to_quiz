from fastapi import APIRouter, Request
from api.models.quiz_models import ClearResponse, HistoryResponse
from api.utils.quiz_manager import clear_quizzes, get_history

router = APIRouter(tags=["Admin"])

@router.post("/clear", response_model=ClearResponse)
def clear_quiz(request: Request):
    """Réinitialise l'API et efface les quiz enregistrés."""
    clear_quizzes(request.app)
    return {"message": "Quiz réinitialisé"}

@router.get("/history", response_model=HistoryResponse)
def get_quiz_history(request: Request, limit: int = 10):
    """Retourne l'historique des quiz récents."""
    return {"history": get_history(request.app, limit)}
