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
