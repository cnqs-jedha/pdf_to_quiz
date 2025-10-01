import requests
import gradio as gr
from core.config import API_BASE_URL, API_QUESTIONS_PATH, USE_API, REQUIRE_API, BASE_DIR, json_path


def check_ready_api():
    try:
        r = requests.get(f"{API_BASE_URL}/ready", timeout=5)
        if r.status_code == 200:
            data = r.json()
            return data.get("status") == "ok", data                           
    except Exception as e:
        print(f"[WARN] API non prête : {e}")
    return False, {"status": "error", "reason": "Quiz vide"}

# ok, info = check_ready()
def check_ready_for_gradio():
    quiz_ready, info = check_ready_api()
    if quiz_ready:
        return gr.update(visible=False), gr.update(visible=True)
    else:
        return gr.update(visible=True), gr.update(visible=False)