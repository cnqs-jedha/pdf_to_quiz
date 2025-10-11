# src/pipeline/server.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
import subprocess

app = FastAPI(title="Pipeline Service")

def run_pipeline_task(drive_link: str):
    """Fonction exécutée en arrière-plan pour lancer le vrai pipeline"""
    print(f"🚀 Exécution du pipeline pour : {drive_link}", flush=True)
    subprocess.run(
        ["python", "-m", "src.pipeline.run", "--drive_link", drive_link],
        check=True
    )
    print("✅ Pipeline terminé", flush=True)


@app.post("/execute")
async def execute_pipeline(req: dict, background_tasks: BackgroundTasks):
    drive_link = req.get("drive_link")
    if not drive_link:
        raise HTTPException(status_code=400, detail="drive_link manquant")

    print(f"📩 Requête reçue pour le lien : {drive_link}", flush=True)

    # Lancer la tâche en arrière-plan (non bloquante)
    background_tasks.add_task(run_pipeline_task, drive_link)

    # Répondre immédiatement à l’API
    return {"status": "ok", "message": "Pipeline démarré"}
