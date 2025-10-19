from api.models.quiz_models import WeightedQuestion
import random

def update_user_performance(user_history, answer):
    """Met à jour les performances par question et par thème."""
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
    """Calcule une liste de questions pondérées selon la performance utilisateur."""
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
