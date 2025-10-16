from fastapi import FastAPI
from api.routes.quiz_routes import router as quiz_router
from api.routes.health_routes import router as health_router
from api.routes.admin_routes import router as admin_router

"""
===========================================================
FICHIER PRINCIPAL DE L’APPLICATION FASTAPI
===========================================================

Ce module initialise et configure l’application FastAPI servant d’API pour le projet de génération de quiz.

Fonctionnalités :
- Crée l’application FastAPI avec titre, version et contact.
- Initialise l’état global de l’application (`last_received_quiz`, `quiz_history`).
- Monte les différents routeurs :
    * quiz_routes → routes principales pour gérer les quiz
    * health_routes → vérification de l’état de l’API
    * admin_routes → gestion de l’historique et réinitialisation

Ce fichier sert de point d’entrée pour le serveur FastAPI.
Exemple d’exécution :
    uvicorn main:app --reload
"""

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
