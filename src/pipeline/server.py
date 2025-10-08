# src/pipeline/server.py
from fastapi import FastAPI, HTTPException
import subprocess

app = FastAPI(title="Pipeline Service")

@app.post("/execute")
def execute_pipeline(req: dict):
    drive_link = req.get("drive_link")
    if not drive_link:
        raise HTTPException(status_code=400, detail="drive_link manquant")

    print(f"🚀 Lancement du pipeline pour : {drive_link}")

    # Lance ton pipeline via run.py
    subprocess.run(
        ["python", "-m", "src.pipeline.run", "--drive_link", drive_link],
        check=True
    )

    return {"status": "ok", "message": "Pipeline exécuté"}
