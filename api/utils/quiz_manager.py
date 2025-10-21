from api.models.quiz_models import UserHistory

"""
===========================================================
UTILITAIRES DE GESTION DES QUIZ (quiz_manager)
===========================================================

Ce module contient les fonctions utilitaires utilisées pour gérer l’état interne de l’application.

Fonctions principales :
- add_quiz(app, quiz_data) : ajoute un quiz à l’historique et le définit comme dernier reçu.
- get_last_quiz(app) : retourne le dernier quiz enregistré.
- clear_quizzes(app) : réinitialise complètement l’état interne de l’API.
- get_history(app, limit) : renvoie les N derniers quiz enregistrés.

Ces fonctions manipulent les objets stockés dans `app.state`
et servent de couche d’abstraction entre les routes et la logique métier.
"""

def add_quiz(app, quiz_data: dict):
    """
    Ajoute un quiz à l'historique et le définit comme dernier reçu.

    Args:
        app (FastAPI): Instance de l'application FastAPI.
        quiz_data (dict): Données du quiz à enregistrer.
    """
    app.state.last_received_quiz = quiz_data
    app.state.quiz_history.append(quiz_data)

def get_last_quiz(app):
    """
    Retourne le dernier quiz enregistré.

    Args:
        app (FastAPI): Instance de l'application FastAPI.

    Returns:
        dict: Le dernier quiz enregistré, ou un quiz vide si aucun n'existe.
    """
    return app.state.last_received_quiz or {"quiz": []}

def clear_quizzes(app):
    """Réinitialise l'état de l'API."""
    app.state.last_received_quiz = None
    app.state.quiz_history = []

def get_history(app, limit: int = 10):
    """
    Retourne les N derniers quiz enregistrés.

    Args:
        app (FastAPI): Instance de l'application FastAPI.
        limit (int): Nombre maximum de quiz à retourner.

    Returns:
        list[dict]: Liste des derniers quiz.
    """
    return app.state.quiz_history[-limit:]

def get_or_create_user_history(app, user_id="default_user") -> UserHistory:
    """
    Récupère ou initialise l'historique d'un utilisateur.

    Args:
        app (FastAPI): Instance de l'application FastAPI.
        user_id (str, optional): Identifiant de l'utilisateur (par défaut "default_user").

    Returns:
        UserHistory: Historique de l'utilisateur.
    """
    if not hasattr(app.state, "user_history"):
        app.state.user_history = {}
    if user_id not in app.state.user_history:
        app.state.user_history[user_id] = UserHistory(
            user_id=user_id,
            quiz_sessions=[],
            question_performance={},
            theme_performance={}
        )
    return app.state.user_history[user_id]