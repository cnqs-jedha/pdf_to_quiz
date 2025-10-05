from fastapi import FastAPI
from api.routes.quiz_routes import router as quiz_router
from api.routes.health_routes import router as health_router
from api.routes.admin_routes import router as admin_router

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
)

# Initialiser les variables d'état
app.state.last_received_quiz = None
app.state.quiz_history = []

# Inclusion des routes
app.include_router(quiz_router)
app.include_router(health_router)
app.include_router(admin_router)
