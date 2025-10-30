# :books: PDF to quiz

**pdf_to_quiz** est une application d’apprentissage automatisé qui transforme des documents pédagogiques (PDF) en **quiz interactifs**.  
Elle combine **traitement de texte, regroupement sémantique et génération LLM** pour offrir une expérience éducative intelligente et dynamique.

## :rocket: Objectif du projet

L'application a pour but de :

1. **Importer automatiquement** des fichiers pdf depuis un dossier Google Drive.
2. **Extraire et nettoyer le texte brut** des documents.
3. **Segmenter et regrouper** le contenu selon des thème cohérents
4. **Identifier les passages les plus pertinents** pour générer des explications
5. **Générer automatiquement des quiz** (QCM, vrai/faux).
6. **Envoyer les données** vers l'application pour permettre à l'utilisateur de jouer le quiz
7. **Evaluer les performances** du LLM utilisé (pertinence, cohérence).

## :brain: Pipeline de traitement

```text
Lien Google Drive
    ↓
Récupération des fichiers PDF
    ↓
Extraction du texte 
    ↓
Nettoyage et normalisation
    ↓
Découpage du texte en chunks
    ↓
Regroupement thématique
    ↓
Sélection des passages clés
    ↓
Génération du quiz par LLM
    ↓
Envoi des données à l'API
    ↓
Lancement du quiz
```

## :building_construction: Architecture

### Structure du projet

```text
pdf_to_quiz/
|   arborescence.md # Détail de la structure (dossiers/fichiers) et rôle de chaque élément
|   README.md # Documentation générale du projet, instructions d'installation et d'utilisation
|   
+---.devcontainer # Configuration du conteneur de développement (VS Code / Docker)
|       
+---api  # Configuration de l'API(FastAPI)
|   |   
|   +---models # Définit les modèles nécessaires pour gérer les questions, quiz, métadonnées et réponses d’API
|   |       
|   +---routes # Endpoints de l'API : génération de quiz, historisation, opérations admin, santé
|   |       
|   +---tests # Vérifie le bon fonctionnement des endpoints
|   |       
|   \---utils # Fonctions utilitaires liées à l'API
|           
+---app # Interface utilisateur (Gradio)
|   |   
|   +---core # Orchestration et mise en oeuvre du quiz
|   |       
|   \---ui # Composants interface utilisateur (UI)
|        |
|       \---img # Images rattachées à l'UI
|          
+---chroma_db # Base de données Chroma pour le stockage vectoriel/embeddins
|           
+---docker # Configuration des conteneurs Docker pour le pipeline, l'api, l'app, devlab
|       
+---notebooks
|   |   
|   +---chroma_db
|   |           
|   \---faiss_db
|           
+---requirements # Fichiers de dépendances Python
|       
\---src # Code source principal
    |   
    +---pipeline # Pipeline de traitement
    |           
    +---utils # Fonctions utilitaires générales pour le projet
    |   |   
    |   +---evaluate_model # Script pour évaluer la qualité des quiz générés
```

## :arrows_counterclockwise: Interactions

### Résumé des interactions

```text
Google Drive
   ↓
(run.py) → Extraction → Nettoyage → Chunking → Thématisation → ChromaDB
   ↓
LLM (Groq) → Génération du quiz
   ↓
API-FastAPI (stockage + endpoints)
   ↓
App-Gradio (UI / Interaction / Score)
```

### Description des interactions

Chaque étape du pipeline, de l’import des PDF à la génération du quiz, est orchestrée de manière modulaire.
Le tableau ci-dessous décrit la séquence complète des échanges entre les différents modules (pipeline, API, app).

| Étape        | Module source         | Module cible                  | Description                                                                              | Script / Fichier concerné                                                       |
| ------------ | --------------------- | ----------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| 1        | **Utilisateur / CLI** | **Google Drive API**          | Authentification et connexion à Google Drive                                             | `src/utils/drive_import.py` → `authenticate_google()`                           |
| 2        | **Google Drive API**  | **Pipeline**                  | Récupération des IDs des fichiers PDF dans le dossier Drive                              | `src/utils/drive_import.py` → `get_pdfs_ids()`                                  |
| 3     | **Pipeline**          | **Extraction**                | Extraction du texte brut des PDF                                                         | `src/utils/extractor.py` → `get_all_pdfs_data()`                                |
| 4       | **Extraction**        | **Nettoyage / Normalisation** | Nettoyage du texte (caractères, espaces, ponctuation, etc.)                              | `src/utils/normalizer.py` → `normalize_text()`                                  |
| 5       | **Texte normalisé**   | **Chunking**                  | Découpage du texte + ajout des métadonnées (source, page, thème, etc.)                   | `src/pipeline/tokenizer.py` → `chunk_with_metadata()`                           |
| 6        | **Chunks**            | **Clustering thématique**     | Regroupement des chunks par thématique avec HDBSCAN                                      | `src/pipeline/clustering_theme.py` → `hdbscan_clustering()`                     |
| 7      | **Thèmes**            | **Base vectorielle**          | Stockage des embeddings dans ChromaDB                                                    | `src/pipeline/chroma_handler.py` → `save_to_chroma()`                           |
| 8      | **VectorDB**          | **Sélection des chunks clés** | Sélection des passages les plus pertinents pour le prompt du LLM                         | `src/pipeline/collect_best_chunks_to_prompt.py` → `find_best_chunk_to_prompt()` |
| 9       | **Chunks clés**       | **LLM (Groq)**                | Génération du quiz à partir des chunks                                                   | `src/pipeline/quiz_generator.py` → `generate_quiz_from_chunks()`                |
| 10 | **Pipeline**          | **API Backend**               | Envoi du quiz généré à l’API (POST `/send_quiz`)                                         | `run.py` → `requests.post(POST_TARGET_URL)`                                     |
| 11    | **API**               | **Mémoire interne**           | Stockage du quiz reçu en mémoire (`app.state.last_received_quiz`) + ajout à l’historique | `api/routes/quiz_routes.py`                                                     |
| 12     | **API**               | **Health route**              | Vérification de la disponibilité de l’API (endpoint `/ready`)                            | `api/routes/health_routes.py`                                                   |
| 13  | **API**               | **Admin route**               | Gestion administrative : `/history`, `/clear`                                            | `api/routes/admin_routes.py`                                                    |
| 14   | **App (Gradio)**      | **API**                       | Vérifie que l’API est prête à servir le quiz                                             | `core/check.py` → `check_ready_for_gradio()`                                    |
| 15    | **App (Gradio)**      | **UI utilisateur**            | Chargement du quiz, affichage des questions, score                            | `ui/ui_gradio.py` → `start_quiz()`, `check_answer()`, `next_question()`         |
| 16    | **Utilisateur**       | **App (Gradio)**              | Interaction : répondre aux questions, rejouer le quiz                          | `app/core/quiz_handler.py`                |
| 17  | **App (Gradio)**      | **API (FastAPI)**             | Envoi des résultats du quiz à l’API pour historisation                       | `core/helpers.py` (via `requests.post`)                                         |
| 18  | **App (Gradio)**      | **Utilisateur**               | Affichage final : score, bilan par thème                             | `ui/ui_gradio.py` (rendu final de l’interface)                                  |

* Module source : élément qui envoie une information, une requête ou un traitement
* Module cible : destinataire de l'action. Il reçoit, traite ou stocke les données

## :atom_symbol: Technologies principale

| Domaine                     | Outils                                                 |
| --------------------------- | ------------------------------------------------------ |
| **Déploiement**             | Docker + Devcontainer                                  |
| **Intégration Drive**       | Google Drive API                                       |
| **Traitement de texte**     | Pypdf/PdfReader, langchain                             |
| **Regroupement thématique** | Spacy, scikit-learn (HDBSCAN)                          |
| **Stockage**                | Langchain(Hugging Face)                                |
| **LLM/génération prompt**   | Langchain(Groq)                                        |
| **Backend API**             | FastAPI, pydantic                                      |
| **Frontend / UI**           | Gradio (quiz interactif)                               |

## :zap: Flux API

|  Méthode           | Endpoint          | Description                |
| ----------------- | ----------------- | -------------------------- |
| POST              | `/send_quiz`    | Envoi d’un quiz au serveur|
| GET  |`/quiz`| Récupération du dernier quiz |
| GET | `/health` | Vérifie le bon fonctiionnement de l'API |
| GET | `/ready` | Indique si un quiz est prêt à être lancé |
| POST | `/clear` | Réinitialise l'API et efface les quiz enregistrés |
| GET | `/history` | Retourne l'historique des quiz récents |

voir aussi <http://localhost:8000/docs>

## :test_tube: Evaluation du LLM

L’évaluation se base sur un score de pertinence thématique (similarité cosinus entre embeddings du texte source et du quiz)

Chaque génération de quiz est évalué selon :

* Pertinence du contenu : cohérence avec le thème du texte source.
* Cohérence linguistique.

Les scores sont stockés et visualisés dans un fichier d'évaluation.

## :mag: Points techniques

* Isolation entre le traitement (Core) et l'intferface (Gradio)
* Modularité : chaque étape du pipeline est testable séparemment
* Traçabilité : chaque chunk est lié à son texte source
* Reproductibilité : pipeline entièrement conteneurisé via Docker et Devcontainer
* Surveillance : endpoints de santé, logs d'évaluation

## :arrow_forward: Installation, exécution, tutlisation

### 0. Prérequis

Avoir un fichier à la racine `.env` qui contient :

La clé API de Groq
Les identifiants (credentials) de Google Drive

Il est nécéssaire d'avoir le token (fichier) du dossier à la racine du projet.

### 1. Cloner le dépôt

```bash
git clone https://github.com/ton-compte/pdf_to_quiz.git
cd pdf_to_quiz
```

### 2. Démarrer les conteneurs Docker

* Vérifier que Docker fonctionne :
`docker ps`

* Builder les images de l'api, de l'app et du pipeline :
`docker compose build`

* Lancer le projet:
`docker compose up`

* Lancer une composante du projet :
`docker compose up pipeline`

`docker compose up api`

`docker compose up app`

* Arrêter le conteneur Docker :
`docker compose down`

### 3. Lancer l'application

* Backend : <http://localhost:8000/docs>
* Interface quiz : <http://localhost:7860>

## :file_folder: Exemple de quiz généré

```json
{
  "quiz": [
    {
      "question": {
        "llm_response": {
          "choices": {
            "a": "La Saint-Barthélémy vue par Catherine de Médicis",
            "b": "L'exécution de 60 ou 70 personnes",
            "c": "La prise de la halle",
            "d": "La pendaison de tous les prisonniers"
          },
          "correct_answer": {
            "answer": "L'exécution de 60 ou 70 personnes",
            "lettre": "b"
          },
          "correct_answer_long": "L'extrait des Commentaires du chef catholique Montluc décrit l'exécution de 60 ou 70 personnes, qui ont été pendues aux piliers de la halle sans autre cérémonie. Cet événement est un exemple de violence et de répression qui a eu lieu pendant la période de la Saint-Barthélémy.",
          "difficulty_level": "standard",
          "text": "Quel événement décrit dans l'extrait des Commentaires du chef catholique Montluc ?"
        },
        "metadata": {
          "chunk_id": 122,
          "file_id": "1BEfalQaLb-8C7uJhH67W5cyhWYDq5NJp",
          "file_name": "edit_Nantes.pdf",
          "page": 3,
          "theme": "guerre religion chrétien"
        }
      }
    }
  ]
}
```

## :compass: Roadmap

* [x] Extraction PDF

* [x] Nettoyage du texte

* [x] Chunking, regroupement thématique

* [x] Génération de quiz

* [x] Evaluation automatique du LLM

* [x] Déploiement en local du quiz interactif

* [ ] Améliorer la classification automatique des thèmes

* [ ] Créer un processus d'identification

* [ ] Améliorer l'expérience utilisateur

## :busts_in_silhouette: Auteurs

Projet développé par [Stéphane Durig](https://github.com/StephaneDurig), [Quentin Haentjens](https://github.com/Quentin-qha), [Nadège Lefort](https://github.com/nlefort), [Catherine Silavong](https://github.com/csil08)

Sous la supervision de [Jedha](https://www.jedha.co/)

*La réalisation de ce projet s'inscrit dans le cadre de la [formation Data Scientist](https://www.jedha.co/formations/formation-data-scientist) développé par [Jedha](https://www.jedha.co/), en vue de l'obtention de la certification professionnelle de niveau 6 (bac+4) enregistrée au RNCP : [Concepteur développeur en science des données](https://www.francecompetences.fr/recherche/rncp/35288/).*