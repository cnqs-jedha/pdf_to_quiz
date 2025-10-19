from fastapi import APIRouter, Request, HTTPException
import os
import subprocess
import requests
from fastapi.responses import JSONResponse
from api.models.quiz_models import Quiz, QuizResponse, PipelineRequest, UserAnswer, QuizSession, UserHistory, WeightedQuestion
from api.utils.quiz_manager import add_quiz, get_last_quiz
from api.utils.quiz_logic import update_user_performance, compute_weighted_questions
from api.utils.quiz_manager import get_or_create_user_history

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

@router.post("/save_answer")
async def save_user_answer(request: Request, answer: UserAnswer):
    user_history = get_or_create_user_history(request.app)
    update_user_performance(user_history, answer)
    return {"message": "Réponse sauvegardée avec succès"}

def cleanup_old_quiz_sessions(user_history: UserHistory, max_sessions: int = 5):
    """Nettoie l'historique pour ne garder que les N dernières sessions."""
    if len(user_history.quiz_sessions) > max_sessions:
        # Garder seulement les dernières sessions
        user_history.quiz_sessions = user_history.quiz_sessions[-max_sessions:]
        
        # Nettoyer aussi les performances par question et thème des sessions supprimées
        # (optionnel - on peut garder les performances même si la session est supprimée)
        print(f"🧹 Nettoyage automatique : {max_sessions} dernières sessions conservées")

@router.post("/save_quiz_session")
async def save_quiz_session(request: Request, session: QuizSession):
    """Sauvegarde une session de quiz complète."""
    if not hasattr(request.app.state, 'user_history'):
        request.app.state.user_history = {}
    
    user_id = "default_user"
    if user_id not in request.app.state.user_history:
        request.app.state.user_history[user_id] = UserHistory(
            user_id=user_id,
            quiz_sessions=[],
            question_performance={},
            theme_performance={}
        )
    
    # Ajouter la nouvelle session
    request.app.state.user_history[user_id].quiz_sessions.append(session)
    
    # Nettoyer automatiquement pour ne garder que les 5 dernières sessions
    cleanup_old_quiz_sessions(request.app.state.user_history[user_id], max_sessions=5)
    
    return {"message": "Session sauvegardée avec succès"}

@router.get("/user_history")
async def get_user_history(request: Request, user_id: str = "default_user"):
    """Récupère l'historique complet d'un utilisateur."""
    if not hasattr(request.app.state, 'user_history'):
        return UserHistory(user_id=user_id, quiz_sessions=[], question_performance={}, theme_performance={})
    
    if user_id not in request.app.state.user_history:
        return UserHistory(user_id=user_id, quiz_sessions=[], question_performance={}, theme_performance={})
    
    return request.app.state.user_history[user_id]

@router.post("/cleanup_history")
async def cleanup_user_history(request: Request, user_id: str = "default_user", max_sessions: int = 5):
    """Force le nettoyage de l'historique d'un utilisateur."""
    if not hasattr(request.app.state, 'user_history'):
        return {"message": "Aucun historique trouvé"}
    
    if user_id not in request.app.state.user_history:
        return {"message": "Utilisateur non trouvé"}
    
    old_count = len(request.app.state.user_history[user_id].quiz_sessions)
    cleanup_old_quiz_sessions(request.app.state.user_history[user_id], max_sessions)
    new_count = len(request.app.state.user_history[user_id].quiz_sessions)
    
    return {
        "message": f"Nettoyage effectué : {old_count} → {new_count} sessions",
        "sessions_removed": old_count - new_count
    }

@router.get("/history_stats")
async def get_history_stats(request: Request, user_id: str = "default_user"):
    """Récupère les statistiques de l'historique d'un utilisateur."""
    if not hasattr(request.app.state, 'user_history'):
        return {"quiz_sessions": 0, "question_performance": 0, "theme_performance": 0}
    
    if user_id not in request.app.state.user_history:
        return {"quiz_sessions": 0, "question_performance": 0, "theme_performance": 0}
    
    user_history = request.app.state.user_history[user_id]
    return {
        "quiz_sessions": len(user_history.quiz_sessions),
        "question_performance": len(user_history.question_performance),
        "theme_performance": len(user_history.theme_performance),
        "max_sessions": 5
    }


@router.get("/weighted_questions")
async def get_weighted_questions(request: Request, user_id="default_user", max_questions: int = 10):
    last_quiz = get_last_quiz(request.app)
    if not last_quiz or "quiz" not in last_quiz:
        return {"questions": [], "message": "Aucun quiz disponible"}

    user_history = get_or_create_user_history(request.app, user_id)
    selected = compute_weighted_questions(last_quiz, user_history, max_questions)
    return {"questions": selected, "message": f"{len(selected)} questions sélectionnées avec poids"}