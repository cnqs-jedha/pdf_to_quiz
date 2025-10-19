from fastapi import APIRouter, Request, HTTPException
import os
import subprocess
import requests
from fastapi.responses import JSONResponse
from api.models.quiz_models import Quiz, QuizResponse, PipelineRequest, UserAnswer, QuizSession, UserHistory, WeightedQuestion
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

@router.post("/save_answer")
async def save_user_answer(request: Request, answer: UserAnswer):
    """Sauvegarde une réponse utilisateur pour l'historique."""
    if not hasattr(request.app.state, 'user_history'):
        request.app.state.user_history = {}
    
    user_id = "default_user"  # Pour l'instant, on utilise un utilisateur par défaut
    if user_id not in request.app.state.user_history:
        request.app.state.user_history[user_id] = UserHistory(
            user_id=user_id,
            quiz_sessions=[],
            question_performance={},
            theme_performance={}
        )
    
    # Mettre à jour les performances par question
    question_id = answer.question_id
    if question_id not in request.app.state.user_history[user_id].question_performance:
        request.app.state.user_history[user_id].question_performance[question_id] = {"correct": 0, "incorrect": 0}
    
    if answer.is_correct:
        request.app.state.user_history[user_id].question_performance[question_id]["correct"] += 1
    else:
        request.app.state.user_history[user_id].question_performance[question_id]["incorrect"] += 1
    
    # Mettre à jour les performances par thème
    theme = answer.theme
    if theme not in request.app.state.user_history[user_id].theme_performance:
        request.app.state.user_history[user_id].theme_performance[theme] = {"correct": 0, "incorrect": 0}
    
    if answer.is_correct:
        request.app.state.user_history[user_id].theme_performance[theme]["correct"] += 1
    else:
        request.app.state.user_history[user_id].theme_performance[theme]["incorrect"] += 1
    
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
async def get_weighted_questions(request: Request, user_id: str = "default_user", max_questions: int = 10):
    """Retourne les questions avec des poids basés sur l'historique de l'utilisateur."""
    # Récupérer le dernier quiz
    last_quiz = get_last_quiz(request.app)
    if not last_quiz or "quiz" not in last_quiz:
        return {"questions": [], "message": "Aucun quiz disponible"}
    
    # Récupérer l'historique de l'utilisateur
    user_history = None
    if hasattr(request.app.state, 'user_history') and user_id in request.app.state.user_history:
        user_history = request.app.state.user_history[user_id]
    
    # Calculer les poids pour chaque question
    weighted_questions = []
    for quiz_item in last_quiz["quiz"]:
        question = quiz_item["question"]
        question_id = f"{question['metadata']['theme']}_{question['llm_response']['text'][:50]}"
        
        # Poids de base
        base_weight = 1.0
        
        # Ajuster le poids basé sur l'historique
        if user_history and question_id in user_history.question_performance:
            perf = user_history.question_performance[question_id]
            total_attempts = perf["correct"] + perf["incorrect"]
            
            if total_attempts > 0:
                success_rate = perf["correct"] / total_attempts
                # Plus le taux de réussite est faible, plus le poids est élevé
                weight = 2.0 - success_rate  # Poids entre 1.0 et 2.0
            else:
                weight = 1.5  # Poids par défaut pour les nouvelles questions
        else:
            weight = 1.2  # Légèrement plus de poids pour les questions jamais vues
        
        # Ajuster le poids selon le thème
        theme = question['metadata']['theme']
        if user_history and theme in user_history.theme_performance:
            theme_perf = user_history.theme_performance[theme]
            theme_total = theme_perf["correct"] + theme_perf["incorrect"]
            if theme_total > 0:
                theme_success_rate = theme_perf["correct"] / theme_total
                weight *= (2.0 - theme_success_rate)  # Multiplier par le facteur de difficulté du thème
        
        weighted_questions.append(WeightedQuestion(
            question=quiz_item,
            weight=weight,
            difficulty_score=weight
        ))
    
    # Trier par poids (les plus difficiles en premier)
    weighted_questions.sort(key=lambda x: x.weight, reverse=True)
    
    # Sélectionner les questions avec probabilité pondérée
    import random
    selected_questions = []
    
    # Stratégie de sélection améliorée :
    # 1. Prioriser les questions jamais vues
    # 2. Prioriser les questions mal répondues
    # 3. Éviter les questions bien répondues récemment
    
    # Séparer les questions par catégorie
    never_seen = []
    poorly_answered = []
    well_answered = []
    
    for wq in weighted_questions:
        question_id = f"{wq.question['question']['metadata']['theme']}_{wq.question['question']['llm_response']['text'][:50]}"
        
        if user_history and question_id in user_history.question_performance:
            perf = user_history.question_performance[question_id]
            total_attempts = perf["correct"] + perf["incorrect"]
            if total_attempts > 0:
                success_rate = perf["correct"] / total_attempts
                if success_rate < 0.5:  # Mal répondues
                    poorly_answered.append(wq)
                else:  # Bien répondues
                    well_answered.append(wq)
            else:
                never_seen.append(wq)
        else:
            never_seen.append(wq)
    
    # Stratégie améliorée : mélanger les questions avec leur poids
    random.shuffle(never_seen)
    random.shuffle(poorly_answered)
    random.shuffle(well_answered)

    # Construire un pool de candidats dans l'ordre de priorité
    all_candidates = never_seen + poorly_answered + well_answered

    # Sélectionner les N premières questions (garantit toujours max_questions si disponibles)
    for wq in all_candidates[:max_questions]:
        selected_questions.append(wq.question)
        if len(selected_questions) >= max_questions:
            break
    
    # Puis les questions mal répondues
    if len(selected_questions) < max_questions:
        for wq in poorly_answered:
            selected_questions.append(wq.question)
            if len(selected_questions) >= max_questions:
                break
    
    # Enfin, les questions bien répondues si nécessaire
    if len(selected_questions) < max_questions:
        for wq in well_answered:
            selected_questions.append(wq.question)
            if len(selected_questions) >= max_questions:
                break
    
    return {"questions": selected_questions, "message": f"{len(selected_questions)} questions sélectionnées avec poids"}
