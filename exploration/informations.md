# Docker
## Builder l'image docker
1. Aller dans le dossier exploration
2. Éxécuter la commande -> `docker build -t exploration-final-jedha-project .`

## Lancer l'image docker dans VS code
1. Aller dans le dossier exploration (y rester si vous y êtes déjà)
2. Éxécuter la comande -> `docker run -p 8888:8888 -v "$(pwd)":/exploration exploration-final-jedha-project`
3. Cliquer dans la zone de recherche, en haut au centre, et tapez -> `>Dev containers: Open Folder in Container...`
4. Selectionnez dans la fenêtre le dossier exploration