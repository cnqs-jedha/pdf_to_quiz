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
