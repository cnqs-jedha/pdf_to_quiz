from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict, List, Optional
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Quiz API",
    description="""
API pour recevoir, stocker et fournir des quiz.  
- **/send_quiz** : envoi d’un quiz au serveur  
- **/quiz** : récupération du dernier quiz  
- **/ready** : état de préparation (utile pour Gradio ou d’autres clients)  
- **/history** : consulter l’historique  
- **/clear** : réinitialiser l’API  
    """,
    version="1.0.0",
    contact={
        "name": "Catherine Silavong, Nadège Lefort, Quentin Haentjens, Stephane Durig",
        "email": "cnsq@gmail.com",
    },
    openapi_tags=[
        {"name": "Quiz", "description": "Endpoints pour envoyer et récupérer des quiz"},
        {"name": "Health", "description": "Endpoints pour vérifier l'état du serveur"},
        {"name": "Admin", "description": "Endpoints pour gérer l'historique et réinitialiser l'API"}
    ]
)
app.state.last_received_quiz = None
app.state.quiz_history = []

# Send quiz
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
        schema_extra = {
            "example": {
                "quiz": [
                    {
                        "question": {
                            "llm_response": {
                                "text": "Quel événement marque la fin de l'Empire romain occidental en 476 ?",
                                "choices": {
                                    "a": "La mort de l'empereur Romulus Augustule",
                                    "b": "La prise de Rome par les Germains"
                                },
                                "correct_answer": {"lettre": "b", "answer": "La prise de Rome par les Germains"},
                                "correct_answer_long": "La prise de Rome par les Germains en 476 marque la fin de l'Empire romain occidental.",
                                "difficulty_level": "standard"
                            },
                            "metadata": {
                                "theme": "empire romain gaulois",
                                "page": 2,
                                "file_name": "GrandesInvasionsII.pdf"
                            }
                        }
                    }
                ]
            }
        }

class QuizResponse(BaseModel):
    message: str
    total_quizzes: int

    class Config:
        schema_extra = {
            "example": {
                "message": "Quiz bien reçu",
                "total_quizzes": 3
            }
        }

@app.post("/send_quiz", tags=['Quiz'], response_model=QuizResponse)
async def receive_quiz(quiz: Quiz):
    app.state.last_received_quiz = quiz.dict()
    app.state.quiz_history.append(quiz.dict())
    return {"message": "Quiz bien reçu", "total_quizzes": len(app.state.quiz_history)}

# The quiz
@app.get("/quiz", tags=['Quiz'], response_model=Quiz)
def get_last_quiz():
    """
    Récupère le dernier quiz envoyé.  
    Retourne `{ "quiz": [...] }` ou un quiz vide si aucun n'a été reçu.
    """
    if app.state.last_received_quiz:
        return app.state.last_received_quiz
    return {"quiz": []}

# Alive
class HealthResponse(BaseModel):
    status: str

    class Config:
        schema_extra = {"example": {"status": "ok"}}

@app.get("/health", tags=['Health'])
def health():
    return {"status": "ok"}

# Quiz is ready to gradio ?
class ReadyResponse(BaseModel):
    status: str
    quiz_count: Optional[int] = None
    reason: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "status": "ok",
                "quiz_count": 5
            }
        }
@app.get("/ready", tags=['Health'], response_model=ReadyResponse)
def ready():
    if app.state.last_received_quiz and len(app.state.last_received_quiz.get("quiz", [])) > 0:
        return {"status": "ok", "quiz_count": len(app.state.last_received_quiz["quiz"])}
    
    return JSONResponse(
        status_code=500,
        content={"status": "error", "reason": "quiz vide"}
    )

# Clean the api quiz
class ClearResponse(BaseModel):
    message: str

    class Config:
        schema_extra = {"example": {"message": "Quiz réinitialisé"}}

@app.post("/clear", tags=['Admin'], response_model=ClearResponse)
def clear_quiz():
    app.state.last_received_quiz = None
    app.state.quiz_history = []
    return {"message": "Quiz réinitialisé"}

# Quiz history
class HistoryResponse(BaseModel):
    history: List[Quiz]

@app.get("/history", tags=['Admin'], response_model=HistoryResponse)
def get_history():
    return {"history": app.state.quiz_history[-10:]}