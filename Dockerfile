FROM python:3.11-slim

# Environnement python plus propre
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && curl -fsSL https://ollama.com/install.sh | sh \
    #&& curl -fsSL https://ollama.com/install.sh -o install.sh \
    #&& chmod +x install.sh \
    #&& ./install.sh \
    #&& rm install.sh \
    #&& ollama pull mistral \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
WORKDIR /project

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

# Exposer les ports
EXPOSE 8888 11434    

# Démarrage automatique
COPY start.sh /start.sh
RUN chmod +x /start.sh
CMD ["/start.sh"]
