from fastapi.testclient import TestClient
from main import app

"""
===========================================================
TESTS UNITAIRES DE L’API (tests_api)
===========================================================

Ce module contient des tests automatisés pour valider le bon fonctionnement de l’API FastAPI.

Tests existants :
- test_health : vérifie que l’endpoint /health répond correctement.
- test_send_and_get_quiz : vérifie la création et la récupération d’un quiz.

Ces tests utilisent le `TestClient` de FastAPI pour simuler des requêtes HTTP
et assurer la cohérence du comportement entre envoi et lecture de quiz.

À étendre :
- test_clear : vérifier que /clear réinitialise bien l’état
- test_history : vérifier la cohérence de l’historique
- test_ready : simuler les différents états de readiness
"""

client = TestClient(app)

# Teste si l'api est en vie
def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

# Teste si l'envoie de quiz foncctionne
def test_send_and_get_quiz():
    quiz_data = {
        "quiz": [
            {
                "question": {
                    "llm_response": {
                        "text": "Exemple de question",
                        "choices": {"a": "Oui", "b": "Non"},
                        "correct_answer": {"lettre": "a", "answer": "Oui"},
                        "correct_answer_long": "Oui est la bonne réponse",
                        "difficulty_level": "standard"
                    },
                    "metadata": {"theme": "test"}
                }
            }
        ]
    }
    res = client.post("/send_quiz", json=quiz_data)
    assert res.status_code == 200
    assert "total_quizzes" in res.json()

    res_get = client.get("/quiz")
    assert res_get.status_code == 200
    assert len(res_get.json()["quiz"]) == 1
