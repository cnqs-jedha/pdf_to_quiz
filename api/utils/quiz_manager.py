from api.models.quiz_models import UserHistory

def add_quiz(app, quiz_data: dict):
    """Ajoute un quiz à l'historique et le définit comme dernier reçu."""
    app.state.last_received_quiz = quiz_data
    app.state.quiz_history.append(quiz_data)

def get_last_quiz(app):
    """Retourne le dernier quiz reçu."""
    return app.state.last_received_quiz or {"quiz": []}

def clear_quizzes(app):
    """Réinitialise l'état de l'API."""
    app.state.last_received_quiz = None
    app.state.quiz_history = []

def get_history(app, limit: int = 10):
    """Retourne les derniers quiz enregistrés."""
    return app.state.quiz_history[-limit:]

def get_or_create_user_history(app, user_id="default_user") -> UserHistory:
    """Récupère ou initialise l'historique d'un utilisateur."""
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