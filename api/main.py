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
API complète pour **recevoir, gérer et analyser des quiz personnalisés**.  
Elle permet de stocker les quiz générés par un pipeline externe, de suivre les performances des utilisateurs,
et d’adapter dynamiquement la difficulté des questions.


### Routes principales (`/quiz_routes`)
- **POST `/send_quiz`** → Envoie un nouveau quiz au serveur et l’enregistre.  
- **GET `/quiz`** → Récupère le dernier quiz reçu.  
- **POST `/run_pipeline`** → Déclenche le pipeline externe pour générer un nouveau quiz à partir d’un lien Google Drive.  
- **POST `/save_answer`** → Sauvegarde une réponse utilisateur (pour le suivi de progression).  
- **POST `/save_quiz_session`** → Enregistre une session complète de quiz (score global, thèmes, etc.).  
- **GET `/user_history`** → Récupère l’historique complet d’un utilisateur.  
- **POST `/cleanup_history`** → Nettoie l’historique pour ne conserver que les N dernières sessions.  
- **GET `/history_stats`** → Retourne des statistiques de progression (questions, thèmes, sessions).  
- **GET `/weighted_questions`** → Renvoie une sélection de questions pondérées selon les performances passées.


### Routes d’administration (`/admin_routes`)
- **POST `/clear`** → Réinitialise complètement l’API et efface les quiz enregistrés.  
- **GET `/history`** → Consulte l’historique global des quiz (limité aux derniers enregistrements).


### Routes de santé (`/health_routes`)
- **GET `/health`** → Vérifie l’état de santé du service (API disponible).  
- **GET `/ready`** → Indique si l’API est prête à recevoir des quiz ou à être utilisée par un client externe.


### Notes techniques
- L’état de l’application (quiz reçus, historique utilisateur, sessions) est conservé **en mémoire** via `app.state`.  
- Pour des raisons de simplicité, un seul utilisateur par défaut (`default_user`) est géré dans cette version.  
- L’API communique avec un conteneur externe nommé **`pipeline`** pour la génération automatique de quiz.  
- Les modèles Pydantic assurent la validation stricte de toutes les données échangées.


### Auteurs
Projet réalisé par **Catherine Silavong, Nadège Lefort, Quentin Haentjens, Stephane Durig**
    """,
    version="1.0.0",
    contact={
        "name": ":  cnsq@gmail.com",
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