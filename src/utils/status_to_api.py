import requests

def notify_stage(stage: str):
    """Envoie un message d'avancement à l'API."""
    try:
        requests.post("http://api:8000/ready", json={"message": stage})
        print(f"🟡 Étape : {stage}", flush=True)
    except Exception as e:
        print(f"⚠️ Impossible de notifier l'API : {e}", flush=True)