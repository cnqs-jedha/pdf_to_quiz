import os
import json
import random
from pathlib import Path

import gradio as gr
import pandas as pd
import requests


# =========================
# Config & utilitaires
# =========================

def _env_flag(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return str(v).strip().lower() in {"1", "true", "yes", "on"}

# Par défaut pour Docker Compose : API joignable via le nom de service "api"
API_BASE_URL       = os.getenv("API_BASE_URL", "http://api:8000")
API_QUESTIONS_PATH = os.getenv("API_QUESTIONS_PATH", "/api/quiz")
USE_API            = _env_flag("USE_API", True)
REQUIRE_API        = _env_flag("REQUIRE_API", True)

BASE_DIR = Path(__file__).parent
json_path = BASE_DIR / "questions_llm.json"  # seulement si fallback autorisé


# =========================
# Data helpers
# =========================

def build_resume_tables(resume):
    """Construit (1) le bilan par thème et (2) le tableau détaillé trié par thème."""
    df = pd.DataFrame(resume)
    if df.empty:
        per_theme = pd.DataFrame(columns=["Thème", "Bonnes réponses", "Questions", "% Réussite"])
        detailed = pd.DataFrame(columns=["Thème", "Question", "Ta réponse", "Bonne réponse", "Résultat"])
        return per_theme, detailed

    per_theme = (
        df.groupby("Thème")["Correct"]
        .agg([("Bonnes réponses", "sum"), ("Questions", "count")])
        .assign(**{"% Réussite": lambda d: (d["Bonnes réponses"] / d["Questions"] * 100).round(0)})
        .sort_values("% Réussite", ascending=True)
        .reset_index()
    )

    detailed = (
        df[["Thème", "Question", "Ta réponse", "Bonne réponse", "Résultat"]]
        .sort_values(["Thème", "Question"], ascending=[True, True])
        .reset_index(drop=True)
    )
    return per_theme, detailed


def _normalize_questions(items):
    """Transforme la liste d'items -> liste de questions pour l'UI."""
    questions = []
    for item in items:
        question_text = item["question"]
        options_dict = item["choices"]
        # certaines API renvoient correct_answer: {answer: "..."} ou simplement answer
        correct_answer = (item.get("correct_answer", {}).get("answer")
                          or item.get("answer"))
        options = list(options_dict.values())
        random.shuffle(options)
        questions.append({
            "question": question_text,
            "options": options,
            "réponse": correct_answer,
            "theme": item.get("_theme", "Sans thème"),
        })
    return questions


def load_questions_from_json(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = []
    if isinstance(data, dict) and "quiz" in data:  # format {quiz: [ {Thème, questions:[...]} ]}
        for bloc in data["quiz"]:
            theme = bloc.get("Thème", "Sans thème")
            for q in bloc.get("questions", []):
                qq = q.copy()
                qq["_theme"] = theme
                items.append(qq)
    elif isinstance(data, list):  # ancien format à plat
        for q in data:
            qq = q.copy()
            qq["_theme"] = qq.get("_theme", "Sans thème")
            items.append(qq)
    else:
        raise ValueError("Format JSON inattendu (ni liste, ni dict avec 'quiz').")

    return _normalize_questions(items)


# -------- API parsing robust --------

def _extract_quiz_payload(data):
    """Cherche récursivement une clé 'quiz' contenant une liste."""
    if isinstance(data, dict):
        if "quiz" in data and isinstance(data["quiz"], list):
            return data["quiz"]
        for v in data.values():
            out = _extract_quiz_payload(v)
            if out is not None:
                return out
    elif isinstance(data, list):
        for el in data:
            out = _extract_quiz_payload(el)
            if out is not None:
                return out
    return None


def load_questions_from_api():
    url = f"{API_BASE_URL.rstrip('/')}/{API_QUESTIONS_PATH.lstrip('/')}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()

    # 1) Essayer JSON direct
    try:
        data = r.json()
    except ValueError:
        # 2) Parfois l’API renvoie un JSON "stringifié"
        txt = r.text.strip()
        try:
            data = json.loads(txt)
        except Exception as e:
            raise RuntimeError(
                f"Réponse non-JSON depuis {url} (content-type={r.headers.get('content-type')}), "
                f"extrait='{txt[:120]}...'"
            ) from e

    # 3) Si c’est encore une chaîne JSON-encodée, re-parser
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            pass

    # 4) Accepter plusieurs formes: {quiz:[...]}, liste brute, ou quiz imbriqué
    if isinstance(data, dict) and "quiz" in data and isinstance(data["quiz"], list):
        payload = data["quiz"]
    elif isinstance(data, list):
        payload = data
    else:
        payload = _extract_quiz_payload(data)
        if payload is None:
            raise ValueError("Réponse API inattendue: ni liste, ni objet contenant 'quiz'.")

    # 5) Aplatir -> liste d'items 'question' avec _theme
    items = []
    for bloc in payload:
        if isinstance(bloc, dict) and isinstance(bloc.get("questions"), list):
            theme = bloc.get("Thème") or bloc.get("theme") or bloc.get("title") or "Sans thème"
            for q in bloc["questions"]:
                qq = dict(q)
                qq["_theme"] = theme
                items.append(qq)
        else:
            # déjà une question isolée
            qq = dict(bloc)
            qq["_theme"] = qq.get("_theme", "Sans thème")
            items.append(qq)

    return _normalize_questions(items)


def load_questions():
    if USE_API:
        try:
            return load_questions_from_api()
        except Exception as e:
            if REQUIRE_API:
                raise SystemExit(f"[ERREUR API] {e}")
            else:
                print(f"[WARN] API indisponible ({e}). Bascule sur le JSON local.")
    # Fallback JSON autorisé uniquement si REQUIRE_API=0
    if not json_path.exists():
        raise SystemExit(
            f"[ERREUR] JSON local introuvable : {json_path}. "
            "Active REQUIRE_API=1 pour forcer l’API ou remets questions_llm.json."
        )
    return load_questions_from_json(json_path)


# =========================
# Chargement des questions
# =========================

niveau_1 = load_questions()


# =========================
# UI (Gradio)
# =========================

custom_css = """
body, .gradio-container { 
    background-color: #f8fafc !important; 
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
}
.block { 
    background: #ffffff !important; 
    border-radius: 16px !important; 
    padding: 24px !important; 
    margin: 16px 0 !important;
    box-shadow: 0 8px 25px rgba(15, 23, 42, 0.08) !important; 
    border: 1px solid rgba(226, 232, 240, 0.8) !important;
}
.markdown h1 {
    color: #1e293b !important;
    text-align: center !important;
    margin-bottom: 20px !important;
    font-weight: 700 !important;
}
.markdown h3 { 
    margin: 16px 0 12px 0 !important; 
    color: #334155 !important;
    font-weight: 600 !important;
}
.markdown p { line-height: 1.6 !important; color: #475569 !important; }
.score-excellent{background:linear-gradient(135deg,#059669 0%,#047857 100%)!important;color:#fff!important;padding:24px!important;border-radius:16px!important;text-align:center!important;margin:16px 0!important;font-size:1.5rem!important;font-weight:700!important;box-shadow:0 8px 32px rgba(5,150,105,.3)!important}
.score-tres-bien{background:linear-gradient(135deg,#3b82f6 0%,#1d4ed8 100%)!important;color:#fff!important;padding:24px!important;border-radius:16px!important;text-align:center!important;margin:16px 0!important;font-size:1.5rem!important;font-weight:700!important;box-shadow:0 8px 32px rgba(59,130,246,.3)!important}
.score-pas-mal{background:linear-gradient(135deg,#f59e0b 0%,#d97706 100%)!important;color:#fff!important;padding:24px!important;border-radius:16px!important;text-align:center!important;margin:16px 0!important;font-size:1.5rem!important;font-weight:700!important;box-shadow:0 8px 32px rgba(245,158,11,.3)!important}
.score-a-ameliorer{background:linear-gradient(135deg,#ef4444 0%,#dc2626 100%)!important;color:#fff!important;padding:24px!important;border-radius:16px!important;text-align:center!important;margin:16px 0!important;font-size:1.5rem!important;font-weight:700!important;box-shadow:0 8px 32px rgba(239,68,68,.3)!important}
.score-final h3 { margin: 0 0 12px 0 !important; font-size: 1.8rem !important; }
.score-final p { margin: 8px 0 0 0 !important; font-size: 1.2rem !important; opacity: .95 !important; }
.bilan-theme { background:#fefefe!important;border:1px solid #e2e8f0!important;border-radius:8px!important;padding:20px!important;margin:16px 0!important; }
.dataframe { border-radius: 8px!important; overflow: hidden!important; border: 1px solid #e2e8f0!important; }
.dataframe th { background-color:#f8fafc!important; color:#374151!important; font-weight:600!important; padding:12px 8px!important; border-bottom:2px solid #e5e7eb!important; }
.dataframe td { padding:10px 8px!important; border-bottom:1px solid #f3f4f6!important; vertical-align:top!important; }
.primary-btn { background:linear-gradient(135deg,#3b82f6 0%,#2563eb 100%)!important; border:none!important; border-radius:8px!important; padding:12px 24px!important; font-weight:600!important; transition:all .2s ease!important; }
.primary-btn:hover { transform: translateY(-1px)!important; box-shadow:0 6px 20px rgba(59,130,246,.3)!important; }
"""

def start_quiz():
    qs = random.sample(niveau_1, min(10, len(niveau_1)))  # 10 questions si possible
    resume = []
    question_out, choix_out, feedback_out, score_out, *states = update_ui(qs, 0, 0, False, "", resume)
    return [
        gr.update(visible=False),               # start_btn
        question_out, choix_out, feedback_out, score_out,
        *states,                                # states (5)
        gr.update(visible=False),               # next_btn
        gr.update(visible=False),               # score_final_display
        gr.update(visible=False),               # encouragement_display
        gr.update(visible=False),               # bilan_theme_display
        gr.update(visible=False),               # bilan_theme_table
        gr.update(visible=False),               # details_title
        gr.update(visible=False),               # resume_table
        gr.update(visible=False),               # restart_btn
        gr.update(visible=False),               # recap_block
    ]

def update_ui(qs, index, score, finished, feedback_txt, resume):
    if index >= len(qs):
        return list(update_final_screen(qs, score, resume))
    q = qs[index]
    score_txt = f"Score : {score}/{len(qs)}"
    return [
        gr.update(value=q["question"], visible=True),           # question
        gr.update(choices=q["options"], value=None, interactive=True, visible=True),  # choix
        gr.update(value=feedback_txt, visible=True),            # feedback
        gr.update(value=score_txt, visible=True),               # score_display
        qs, index, score, finished, resume                      # states (5)
    ]

def update_final_screen(qs, score, resume):
    finished = True
    total_questions = len(qs)
    pourcentage = (score / total_questions) * 100 if total_questions else 0

    if pourcentage == 100:
        score_class = "score-excellent"; encouragement = "🎉 Parfait ! Tu as tout réussi !"
    elif pourcentage >= 80:
        score_class = "score-tres-bien"; encouragement = "👍 Très bien joué !"
    elif pourcentage >= 60:
        score_class = "score-pas-mal"; encouragement = "👏 Pas mal, continue comme ça !"
    else:
        score_class = "score-a-ameliorer"; encouragement = "💪 Continue à t'entraîner !"

    score_et_encouragement = f"""
<div class="{score_class}">
  <h3>🥇 Score final : {score}/{total_questions} ({pourcentage:.0f}%)</h3>
  <p>{encouragement}</p>
</div>
"""

    per_theme, detailed = build_resume_tables(resume)

    bilan_theme = ""
    themes_a_reviser = ""
    bilan_table = pd.DataFrame()
    if not per_theme.empty:
        bilan_theme = "**📊 Bilan par thème**"
        bilan_table = per_theme.copy()
        min_acc = per_theme["% Réussite"].min()
        themes_a_travailler = per_theme.loc[per_theme["% Réussite"] == min_acc, "Thème"].tolist()
        if len(themes_a_travailler) > 0:
            themes_txt = ", ".join(themes_a_travailler)
            themes_a_reviser = f"**📚 À réviser en priorité :** {themes_txt}"

    detailed_copy = detailed.copy() if not detailed.empty else detailed

    return [
        gr.update(value="### 🎯 Quiz terminé !", visible=True),   # question (titre final)
        gr.update(visible=False),                                  # radio
        gr.update(value="", visible=False),                        # feedback
        gr.update(visible=False),                                  # score_display
        qs, len(qs), score, finished, resume,                     # states (5)
        gr.update(visible=False),                                  # next_btn
        gr.update(value=score_et_encouragement, visible=True),     # score_final_display
        gr.update(value=themes_a_reviser, visible=bool(themes_a_reviser)),  # encouragement_display (révisions)
        gr.update(value=bilan_theme, visible=not per_theme.empty), # bilan_theme_display
        gr.update(value=bilan_table, visible=not per_theme.empty), # bilan_theme_table
        gr.update(value="**📋 Détails des réponses (trié par thème)**", visible=True),  # details_title
        gr.update(value=detailed_copy, visible=True),              # resume_table
        gr.update(visible=True),                                   # restart_btn
        gr.update(visible=True),                                   # recap_block
    ]

def check_answer(reponse, qs, index, score, finished, resume):
    if finished or reponse is None:
        return [gr.update()] * 19

    current_q = qs[index]
    correct = current_q["réponse"]
    resultat = "✅" if reponse == correct else "❌"

    resume.append({
        "Thème": current_q.get("theme", "Sans thème"),
        "Question": current_q["question"],
        "Ta réponse": reponse,
        "Bonne réponse": correct,
        "Résultat": resultat,
        "Correct": (reponse == correct),
    })

    if reponse == correct:
        score += 1
        index += 1
        if index >= len(qs):
            final_results = list(update_final_screen(qs, score, resume))
            result = [gr.update(visible=False)]  # start_btn
            result.extend(final_results)
            return result
        else:
            outputs = list(update_ui(qs, index, score, finished, "✅ Correct !", resume))
            result = [gr.update(visible=False)]
            result.extend(outputs)
            result.extend([
                gr.update(visible=False),  # next_btn
                gr.update(visible=False),  # score_final_display
                gr.update(visible=False),  # encouragement_display
                gr.update(visible=False),  # bilan_theme_display
                gr.update(visible=False),  # bilan_theme_table
                gr.update(visible=False),  # details_title
                gr.update(visible=False),  # resume_table
                gr.update(visible=False),  # restart_btn
                gr.update(visible=False),  # recap_block
            ])
            return result
    else:
        return [
            gr.update(visible=False),                          # start_btn
            gr.update(),                                       # question
            gr.update(interactive=False),                      # choix
            gr.update(value=f"❌ Faux. Réponse correcte : {correct}"),  # feedback
            gr.update(value=f"Score : {score}/{len(qs)}"),     # score_display
            qs, index, score, finished, resume,                # states (5)
            gr.update(visible=True),                           # next_btn
            gr.update(visible=False),                          # score_final_display
            gr.update(visible=False),                          # encouragement_display
            gr.update(visible=False),                          # bilan_theme_display
            gr.update(visible=False),                          # bilan_theme_table
            gr.update(visible=False),                          # details_title
            gr.update(visible=False),                          # resume_table
            gr.update(visible=False),                          # restart_btn
            gr.update(visible=False),                          # recap_block
        ]

def next_question(qs, index, score, finished, resume):
    index += 1
    outputs = list(update_ui(qs, index, score, finished, "", resume))
    result = [gr.update(visible=False)]  # start_btn
    result.extend(outputs)
    result.extend([
        gr.update(visible=False),  # next_btn
        gr.update(visible=False),  # score_final_display
        gr.update(visible=False),  # encouragement_display
        gr.update(visible=False),  # bilan_theme_display
        gr.update(visible=False),  # bilan_theme_table
        gr.update(visible=False),  # details_title
        gr.update(visible=False),  # resume_table
        gr.update(visible=False),  # restart_btn
        gr.update(visible=False),  # recap_block
    ])
    return result

def restart_quiz():
    return start_quiz()


# =========================
# App Gradio
# =========================

with gr.Blocks(css=custom_css, title="Quiz Histoire CM1") as app:
    gr.Markdown("# 🧠 Quiz Histoire - CM1", elem_classes=["block"])

    with gr.Column(elem_classes=["block"]):
        start_btn = gr.Button("🚀 Démarrer le quiz", variant="primary", elem_classes=["primary-btn"])
        question = gr.Markdown(visible=False)
        choix = gr.Radio(choices=[], label="Choisis ta réponse :", visible=False)
        feedback = gr.Markdown(visible=False)
        score_display = gr.Textbox(label="Score", interactive=False, visible=False)
        next_btn = gr.Button("➡️ Question suivante", visible=False, variant="secondary")

    with gr.Column(elem_classes=["block"], visible=False) as recap_block:
        gr.Markdown("### 📊 Résultats du quiz")
        score_final_display = gr.HTML(visible=False, elem_classes=["score-final"])
        encouragement_display = gr.Markdown(visible=False, elem_classes=["encouragement"])
        bilan_theme_display = gr.Markdown(visible=False, elem_classes=["bilan-theme"])
        bilan_theme_table = gr.Dataframe(
            visible=False, label="", interactive=False, wrap=True, elem_classes=["dataframe"],
            headers=["Thème", "Bonnes réponses", "Questions", "% Réussite"]
        )
        details_title = gr.Markdown(visible=False)
        resume_table = gr.Dataframe(visible=False, label="Résultats détaillés", interactive=False, wrap=True,
                                    elem_classes=["dataframe"])
        with gr.Row():
            restart_btn = gr.Button("🔄 Rejouer", visible=False, variant="primary", elem_classes=["primary-btn"])

    # États internes
    qs_state = gr.State()
    idx_state = gr.State()
    score_state = gr.State()
    done_state = gr.State()
    resume_state = gr.State()

    outputs_common = [
        start_btn,
        question, choix, feedback, score_display,
        qs_state, idx_state, score_state, done_state, resume_state,
        next_btn, score_final_display, encouragement_display, bilan_theme_display,
        bilan_theme_table, details_title, resume_table, restart_btn, recap_block
    ]

    start_btn.click(fn=start_quiz, outputs=outputs_common)
    choix.change(fn=check_answer,
                 inputs=[choix, qs_state, idx_state, score_state, done_state, resume_state],
                 outputs=outputs_common)
    next_btn.click(fn=next_question,
                   inputs=[qs_state, idx_state, score_state, done_state, resume_state],
                   outputs=outputs_common)
    restart_btn.click(fn=restart_quiz, outputs=outputs_common)

if __name__ == "__main__":
    app.launch(
        server_name=os.getenv("GRADIO_SERVER_NAME", "0.0.0.0"),
        server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860"))
    )
