from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from api.models.quiz_models import HealthResponse, ReadyResponse

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
def health():
    """Vérifie que l'API est en ligne."""
    return {"status": "ok"}

@router.get("/ready", response_model=ReadyResponse)
def ready(request: Request):
    """Indique si un quiz est prêt à être utilisé."""
    last_quiz = request.app.state.last_received_quiz
    if last_quiz and len(last_quiz.get("quiz", [])) > 0:
        return {"status": "ok", "quiz_count": len(last_quiz["quiz"])}
    return JSONResponse(status_code=500, content={"status": "error", "reason": "quiz vide"})
