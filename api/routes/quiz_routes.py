from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from api.models.quiz_models import Quiz, QuizResponse
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
