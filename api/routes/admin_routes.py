from fastapi import APIRouter, Request
from api.models.quiz_models import ClearResponse, HistoryResponse
from api.utils.quiz_manager import clear_quizzes, get_history

"""
===========================================================
ROUTES D’ADMINISTRATION (admin_routes)
===========================================================

Ce module regroupe les routes destinées à la maintenance et à la gestion interne de l’API.

Routes :
- POST /clear → réinitialise l’état global (supprime les quiz enregistrés)
- GET /history → retourne l’historique des derniers quiz reçus

Ces routes utilisent les utilitaires définis dans `utils/quiz_manager`.
Elles sont regroupées sous le tag "Admin" dans la documentation FastAPI.
"""

router = APIRouter(tags=["Admin"])

# Nettoie/vide l'api
@router.post("/clear", response_model=ClearResponse)
def clear_quiz(request: Request):
    """Réinitialise l'API et efface les quiz enregistrés."""
    clear_quizzes(request.app)
    return {"message": "Quiz réinitialisé"}

# Enregistre les quiz précédent dans un historique
@router.get("/history", response_model=HistoryResponse)
def get_quiz_history(request: Request, limit: int = 10):
    """Retourne l'historique des quiz récents."""
    return {"history": get_history(request.app, limit)}
