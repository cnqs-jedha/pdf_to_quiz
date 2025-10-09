#  :books: PDF to quiz

**pdf_to_quiz** est une application d’apprentissage automatisé qui transforme des documents pédagogiques (PDF) en **quiz interactifs**.  
Elle combine **traitement de texte, regroupement sémantique et génération LLM** pour offrir une expérience éducative intelligente et dynamique.

---

## :rocket: Objectif du projet

L'application a pour but de :

1. **Importer automatiquement** des fichiers pdf depuis un dossier Google Drive.
2. **Extraire et nettoyer le texte brut** des documents.
3. **Segmenter et regrouper** le contenu selon des thème cohérents
4. **Identifier les passages les plus pertinents** pour générer des explications
5. **Générer automatiquement des quiz** (QCM, vrai/faux).
6. **Envoyer les données** vers l'application pour permettre à l'utlisateur de jouer le quiz
7. **Evaluer les performances** du LLM utilisé (pertinence, cohérence).

---

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
---

## Structure du projet

```
pdf_to_quiz/
|   .dockerignore
|   .env # Variables environnement
|   .gitignore
|   arborescence.md # Arboresence du projet
|   credentials3.json
|   docker-compose.yml
|   README.md # Documentation du projet
|   token
|   
+---.devcontainer #Configuration du conteneur de développement (VSCode/Docker)
|       
+---api
|       
+---app
|       
+---data
|       
+---docker
|       
+---notebooks
|   |   
|   +---chroma_db
|   |   |   
|   |           
|   \---faiss_db
|           
+---requirements # Bibliothèques nécessaires 
|       
\---src
    |   
    +---pipeline
    |   |              
    +---utils
    |   |   
```            

## Technologies principale





## Installation et Utilisation
### Prérequis
Avoir un fichier à la racine `.env` qui contient :

 - La clés api de Groq
 - Les credits de Google Drive

Il est nécéssaire d'avoir le token (fichier) du dossier à la racine du projet.

### Docker
Pour builder les images de l'api, de l'app, et du pipeline lancer la commande :
`docker compose build`

Pour lancer le projet:
`docker compose up`