from pydantic import BaseModel
from typing import Dict, List, Optional

class CorrectAnswer(BaseModel):
    lettre: str
    answer: str

class LlmResponse(BaseModel):
    text: str
    choices: Dict[str, str]
    correct_answer: CorrectAnswer
    correct_answer_long: str
    difficulty_level: str

class Metadata(BaseModel):
    theme: str
    page: Optional[int] = None
    chunk_id: Optional[int] = None
    file_id: Optional[str] = None
    file_name: Optional[str] = None

class Question(BaseModel):
    llm_response: LlmResponse
    metadata: Metadata

class QuizItem(BaseModel):
    question: Question

class Quiz(BaseModel):
    quiz: List[QuizItem]

    class Config:
        json_schema_extra = {
            "example": {
                "quiz": [
                    {
                        "question": {
                            "llm_response": {
                                "text": "Quel événement décrit dans l'extrait des Commentaires du chef catholique Montluc ?",
                                "choices": {
                                    "a": "La Saint-Barthélémy vue par Catherine de Médicis",
                                    "b": "L'exécution de 60 ou 70 personnes",
                                    "c": "La prise de la halle",
                                    "d": "La pendaison de tous les prisonniers"
                                },
                                "correct_answer": {
                                    "lettre": "b",
                                    "answer": "L'exécution de 60 ou 70 personnes"
                                },
                                "correct_answer_long": "L'extrait des Commentaires du chef catholique Montluc décrit l'exécution de 60 ou 70 personnes, qui ont été pendues aux piliers de la halle sans autre cérémonie. Cet événement est un exemple de violence et de répression qui a eu lieu pendant la période de la Saint-Barthélémy.",
                                "difficulty_level": "standard"
                                },
                                "metadata": {
                                    "theme": "guerre religion chrétien",
                                    "page": 3,
                                    "chunk_id": 122,
                                    "file_id": "1BEfalQaLb-8C7uJhH67W5cyhWYDq5NJp",
                                    "file_name": "edit_Nantes.pdf"
                                }
                        }
                    }
                ]
            }
        }

class QuizResponse(BaseModel):
    message: str
    total_quizzes: int

class HealthResponse(BaseModel):
    status: str

class ReadyResponse(BaseModel):
    status: str
    quiz_count: Optional[int] = None
    reason: Optional[str] = None

class ClearResponse(BaseModel):
    message: str

class HistoryResponse(BaseModel):
    history: List[Quiz]
