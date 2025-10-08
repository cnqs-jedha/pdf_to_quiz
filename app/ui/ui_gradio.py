import os
import json
import random
from pathlib import Path

import gradio as gr
import pandas as pd
import requests

from core.helpers import build_resume_tables
from core.config import API_BASE_URL, API_QUESTIONS_PATH, USE_API, REQUIRE_API, BASE_DIR, json_path
from core.helpers import load_questions

niveau = load_questions(API_BASE_URL, API_QUESTIONS_PATH, USE_API, REQUIRE_API, json_path)

def start_quiz():
    qs = random.sample(niveau, min(10, len(niveau)))  # 10 questions si possible
    resume = []
    question_out, progress_html, choix_out, feedback_out, explain_btn_out, explain_md_out, script_injector_out, score_out, *states = update_ui(qs, 0, 0, False, "", resume)
    return [
        gr.update(visible=False),               # start_btn
        question_out, progress_html, choix_out, feedback_out, explain_btn_out, explain_md_out, script_injector_out, score_out,
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
    total = len(qs)
    numero = f"{index+1:02d}/{total:02d}"
    question_md = f"### {q['question']}"
    progress_html = f"<div class=\"bar\"><span style=\"width:{((index+1)/total)*100:.0f}%\"></span><div class=\"label\">Question {index+1:02d}/{total:02d}</div></div>"
    score_txt = f"Score : {score:02d}"
    return [
        gr.update(value=question_md, visible=True),           # question
        gr.update(value=progress_html, visible=True),           # progress
        gr.update(choices=q["options"], value=None, interactive=True, visible=True, elem_classes=["quiz-radio"], elem_id="choices-radio"),  # choix (reset classes)
        gr.update(value="", visible=False),            # feedback (teaser)
        gr.update(visible=False, value="Voir l'explication"),   # explain_btn (hidden until answered, reset text)
        gr.update(value=q.get("long_answer", ""), visible=False), # explain_md (content hidden)
        gr.update(value="", visible=False),                     # script_injector (hidden)
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
            # Construire la liste détaillée avec fichiers et pages
            themes_details = []
            for theme in themes_a_travailler:
                # Trouver les questions de ce thème dans le quiz
                theme_questions = [q for q in qs if q.get("theme") == theme]
                if theme_questions:
                    # Grouper par fichier et pages
                    file_pages = {}
                    for q in theme_questions:
                        metadata = q.get("metadata", {})
                        file_name = metadata.get("file_name", "Fichier inconnu")
                        page = metadata.get("page", "?")
                        if file_name not in file_pages:
                            file_pages[file_name] = set()
                        file_pages[file_name].add(page)
                    
                    # Formater la liste
                    theme_info = f"**{theme}**\n"
                    for file_name, pages in file_pages.items():
                        pages_list = sorted(list(pages))
                        pages_str = ", ".join(map(str, pages_list))
                        theme_info += f"  • {file_name} (pages: {pages_str})\n"
                    themes_details.append(theme_info.strip())
            
            if themes_details:
                themes_a_reviser = f"**📚 À réviser en priorité :**\n\n" + "\n\n".join(themes_details)

    detailed_copy = detailed.copy() if not detailed.empty else detailed

    return [
        gr.update(value="### 🎯 Quiz terminé !", visible=True),   # question (titre final)
        gr.update(visible=False),                                  # progress_bar
        gr.update(visible=False),                                  # choix
        gr.update(visible=False),                                  # feedback teaser
        gr.update(visible=False),                                  # explain_btn
        gr.update(visible=False),                                  # explain_md
        gr.update(visible=False),                                  # script_injector
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
        return [gr.update()] * 23

    current_q = qs[index]
    # Récupérer la bonne réponse depuis la structure JSON
    if "llm_response" in current_q and "correct_answer" in current_q["llm_response"]:
        correct = current_q["llm_response"]["correct_answer"]["answer"]
    else:
        correct = current_q["réponse"]  # fallback pour l'ancienne structure
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
        explication = current_q.get("long_answer", "")
        feedback_txt = ""
        return [
            gr.update(visible=False),                          # start_btn (1)
            gr.update(),                                       # question (2)
            gr.update(),                                       # ✅ progress_html (3)  <-- ajouté
            gr.update(interactive=False,
                      elem_classes=["quiz-radio","correct", f"correct-{correct}"]), # choix (4)
            gr.update(value=feedback_txt, visible=False),       # feedback (5)
            gr.update(visible=True),                           # explain_btn (6)
            gr.update(value=f"<div class=\"explain-content\">{current_q.get('long_answer','')}</div>", visible=False),  # explain_md (7)
            gr.update(value="", visible=False),                     # script_injector (8)
            gr.update(value=f"Score : {score:02d}"),     # score_display (9)
            qs, index, score, finished, resume,                # states (10..14)
            gr.update(visible=True),                           # next_btn (15)
            gr.update(visible=False),                          # score_final_display (16)
            gr.update(visible=False),                          # encouragement_display (17)
            gr.update(visible=False),                          # bilan_theme_display (18)
            gr.update(visible=False),                          # bilan_theme_table (19)
            gr.update(visible=False),                          # details_title (20)
            gr.update(visible=False),                          # resume_table (21)
            gr.update(visible=False),                          # restart_btn (22)
            gr.update(visible=False),                          # recap_block (23)
        ]
    else:
        explication = current_q.get('long_answer', '')
        feedback_html = ""
        script_html = ""
        return [
            gr.update(visible=False),                          # start_btn (1)
            gr.update(),                                       # question (2)
            gr.update(),                                       # ✅ progress_html (3)  <-- ajouté
            gr.update(interactive=False,
                        elem_classes=["quiz-radio","wrong"],
                        elem_id=f"choices-radio-{correct.replace(' ', '-').replace('é', 'e').replace('è', 'e').replace('à', 'a').replace('ç', 'c').replace('ô', 'o').replace('ù', 'u').replace('î', 'i').replace('ê', 'e')[:30]}"),   # choix (4)
            gr.update(value=feedback_html, visible=False),                    # feedback (5)
            gr.update(visible=True),                           # explain_btn (6)
            gr.update(value=f"<div class=\"explain-content\">{current_q.get('long_answer','')}</div>", visible=False),  # explain_md (7)
            gr.update(value=script_html, visible=False),       # script_injector (8) - pas de script à injecter
            gr.update(value=f"Score : {score:02d}"),     # score_display (9)
            qs, index, score, finished, resume,                # states (10..14)
            gr.update(visible=True),                           # next_btn (15)
            gr.update(visible=False),                          # score_final_display (16)
            gr.update(visible=False),                          # encouragement_display (17)
            gr.update(visible=False),                          # bilan_theme_display (18)
            gr.update(visible=False),                          # bilan_theme_table (19)
            gr.update(visible=False),                          # details_title (20)
            gr.update(visible=False),                          # resume_table (21)
            gr.update(visible=False),                          # restart_btn (22)
            gr.update(visible=False),                          # recap_block (23)
        ]

def next_question(qs, index, score, finished, resume):
    index += 1
    if index >= len(qs):
        final_results = list(update_final_screen(qs, score, resume))
        result = [gr.update(visible=False)]  # start_btn
        result.extend(final_results)
        return result
    else:
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


def send_drive_link_to_api(drive_link: str):
    """Envoie le lien Google Drive à l’API pour lancer la génération du quiz."""
    if not drive_link or "drive.google.com" not in drive_link:
        return gr.update(value="❌ Lien Google Drive invalide. Vérifie le format.")

    try:
        resp = requests.post(
            f"{API_BASE_URL}/run_pipeline",
            json={"drive_link": drive_link},
            timeout=30
        )
        if resp.status_code == 200:
            data = resp.json()
            message = data.get("message", "✅ Quiz en cours de génération.")
            return gr.update(value=message)
        else:
            return gr.update(value=f"⚠️ Erreur API : {resp.text}")
    except Exception as e:
        return gr.update(value=f"❌ Erreur de connexion à l’API : {e}")