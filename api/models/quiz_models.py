from pydantic import BaseModel, Field
from typing import Dict, List, Optional

"""
===========================================================
DEFINITION DES MODELES Pydantic (quiz_models)
===========================================================

Ce module contient l’ensemble des modèles de données utilisés par l’API.
Les modèles Pydantic permettent la validation, la sérialisation et la documentation automatique.

Contenu principal :
- CorrectAnswer : représente la bonne réponse d’une question.
- LlmResponse : encapsule le texte de la question, les choix et la réponse correcte.
- Metadata : métadonnées associées à chaque question (page, thème, fichier...).
- Question / QuizItem / Quiz : structure hiérarchique complète d’un quiz.
- PipelineRequest : modèle de requête utilisé pour déclencher le pipeline.
- Différents modèles de réponses HTTP : HealthResponse, ReadyResponse, etc.

Chaque modèle est typé, documenté et intègre des exemples pour la documentation Swagger.
"""

# Model Pour le quiz, /send_quiz, /quiz
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

# Model de /health
class HealthResponse(BaseModel):
    status: str

# Model de /ready
class ReadyResponse(BaseModel):
    status: str
    quiz_count: Optional[int] = None
    reason: Optional[str] = None

# Model pour /clear
class ClearResponse(BaseModel):
    message: str

# Model pour /history
class HistoryResponse(BaseModel):
    history: List[Quiz]


# class PipelineRequest(BaseModel):
#     drive_link: str

# Model de /run_pipeline
class PipelineRequest(BaseModel):
    """
    Requête utilisée pour déclencher le pipeline de génération de quiz.

    Attributes:
        drive_link (str): Lien Google Drive du dossier contenant les PDF à analyser.
    """
    drive_link: str = Field(
        ...,
        title="Lien Google Drive",
        description="URL du dossier Google Drive contenant les documents sources pour le quiz.",
        example="https://drive.google.com/drive/folders/1ABCdEfGhIJkLmNopQrStUvWxYZ"
    )
