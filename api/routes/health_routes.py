from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from api.models.quiz_models import HealthResponse, ReadyResponse

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
def health():
    """Vérifie que l'API est en ligne."""
    return {"status": "ok"}

# @router.get("/ready", response_model=ReadyResponse)
# def ready(request: Request):
#     """Indique si un quiz est prêt à être utilisé."""
#     message = "En attente de génération ..."

#     last_quiz = request.app.state.last_received_quiz
#     if last_quiz and len(last_quiz.get("quiz", [])) > 0:
#         return {"status": "ok", "quiz_count": len(last_quiz["quiz"]), "message": message}
#     return JSONResponse(status_code=500, content={"status": "error", "quiz_count": "0", "message": ""})




###### POST ready
# def add_quiz(app, quiz_data: dict):
#     """Ajoute un quiz à l'historique et le définit comme dernier reçu."""
#     app.state.last_received_quiz = quiz_data
#     app.state.quiz_history.append(quiz_data)


# @router.post("/send_quiz", response_model=QuizResponse)
# async def receive_quiz(request: Request, quiz: Quiz):
#     """Enregistre un quiz envoyé par un client."""
#     add_quiz(request.app, quiz.dict())
#     return {"message": "Quiz bien reçu", "total_quizzes": len(request.app.state.quiz_history)}


# @router.get("/ready", response_model=ReadyResponse)
# def ready_post(request: Request, message):
#     message = req.get("message", None)
#     if message is None:
#             raise HTTPException(status_code=400, detail="Champ 'message' manquant")
    

#     return message




@router.post("/ready")
async def update_ready(request: Request, data: dict):
    """Mise à jour du message de progression envoyée par le pipeline."""
    message = data.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Champ 'message' manquant")
    
    # On stocke le message dans l'état global de l'app
    request.app.state.status_message = message
    print(f"📩 Nouveau message reçu du pipeline : {message}", flush=True)
    
    return {"status": "ok", "message": message}


@router.get("/ready")
def get_ready(request: Request):
    """Retourne l'état de readiness + message du pipeline."""
    message = getattr(request.app.state, "status_message", "En attente de génération...")

    last_quiz = getattr(request.app.state, "last_received_quiz", None)
    if last_quiz and len(last_quiz.get("quiz", [])) > 0:
        return {"status": "ok", "quiz_count": len(last_quiz["quiz"]), "message": message}

    return JSONResponse(
        status_code=200,
        content={"status": "pending", "quiz_count": 0, "message": message}
    )