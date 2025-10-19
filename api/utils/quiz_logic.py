from api.models.quiz_models import WeightedQuestion
import random

"""
===========================================================
LOGIQUE MÉTIER DU QUIZ (quiz_logic)
===========================================================

Ce module contient la logique principale du quiz :
- Suivi des performances utilisateur (mises à jour)
- Calcul des poids et priorités des questions
"""

def update_user_performance(user_history, answer):
    """
    Met à jour les performances d’un utilisateur après une réponse.

    Incrémente les compteurs 'correct' ou 'incorrect' pour la question et le thème concernés.

    Args:
        user_history (UserHistory): Historique utilisateur à mettre à jour.
        answer (UserAnswer): Réponse utilisateur (inclut question_id, thème et statut correct/incorrect).
    """
    qid = answer.question_id
    theme = answer.theme

    # Initialiser les compteurs si besoin
    if qid not in user_history.question_performance:
        user_history.question_performance[qid] = {"correct": 0, "incorrect": 0}
    if theme not in user_history.theme_performance:
        user_history.theme_performance[theme] = {"correct": 0, "incorrect": 0}

    # Incrémenter les compteurs
    key = "correct" if answer.is_correct else "incorrect"
    user_history.question_performance[qid][key] += 1
    user_history.theme_performance[theme][key] += 1


def compute_weighted_questions(last_quiz, user_history=None, max_questions=10):
    """
    Calcule une liste de questions pondérées selon les performances utilisateur.

    Le poids d’une question dépend :
    - du taux de réussite de l’utilisateur sur cette question ;
    - du taux de réussite sur son thème ;
    - d’un facteur aléatoire pour varier la sélection.

    Args:
        last_quiz (dict): Dernier quiz reçu.
        user_history (UserHistory, optional): Historique utilisateur.
        max_questions (int): Nombre maximum de questions à retourner.

    Returns:
        list[dict]: Liste de questions sélectionnées, triées par priorité décroissante.
    """
    weighted_questions = []
    for quiz_item in last_quiz["quiz"]:
        question = quiz_item["question"]
        qid = f"{question['metadata']['theme']}_{question['llm_response']['text'][:50]}"
        theme = question['metadata']['theme']

        # Poids de base
        weight = 1.0
        if user_history and qid in user_history.question_performance:
            perf = user_history.question_performance[qid]
            total = perf["correct"] + perf["incorrect"]
            if total > 0:
                success = perf["correct"] / total
                weight = 2.0 - success
        if user_history and theme in user_history.theme_performance:
            tperf = user_history.theme_performance[theme]
            total = tperf["correct"] + tperf["incorrect"]
            if total > 0:
                theme_success = tperf["correct"] / total
                weight *= (2.0 - theme_success)

        weighted_questions.append(WeightedQuestion(
            question=quiz_item,
            weight=weight,
            difficulty_score=weight
        ))

    # Trier et sélectionner
    weighted_questions.sort(key=lambda x: x.weight, reverse=True)
    random.shuffle(weighted_questions)
    return [wq.question for wq in weighted_questions[:max_questions]]
