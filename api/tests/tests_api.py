from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

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
