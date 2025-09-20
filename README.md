# PDF to quiz
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