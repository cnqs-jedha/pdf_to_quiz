#!/bin/bash

# Démarrer Ollama en arrière-plan
#ollama serve &

# Attendre que le serveur soit prêt
#until curl -s http://localhost:11434 > /dev/null; do
#  echo "⏳ Attente que Ollama démarre..."
#  sleep 2
#done

# Tirer le modèle (si pas déjà téléchargé)
#ollama pull mistral

# Lancer JupyterLab
jupyter lab --ip=0.0.0.0 --allow-root --no-browser
