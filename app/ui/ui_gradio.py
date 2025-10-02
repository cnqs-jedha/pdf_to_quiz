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

# niveau = load_questions(API_BASE_URL, API_QUESTIONS_PATH, USE_API, REQUIRE_API, json_path)

def start_quiz():
    niveau = load_questions(API_BASE_URL, API_QUESTIONS_PATH, USE_API, REQUIRE_API, json_path)
    
    qs = random.sample(niveau, min(10, len(niveau)))  # 10 questions si possible
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
                        theme_info += f"  • {file_name} (page(s): {pages_str})\n"
                    themes_details.append(theme_info.strip())
            
            if themes_details:
                themes_a_reviser = f"**📚 À réviser en priorité :**\n\n" + "\n\n".join(themes_details)
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
        explication = current_q.get("long_answer", "")
        feedback_txt = f"✅ Correct !\n\n{explication}" if explication else "✅ Correct !"
        return [
            gr.update(visible=False),                          # start_btn
            gr.update(),                                       # question (reste la même)
            gr.update(interactive=False),                      # choix (désactivé)
            gr.update(value=feedback_txt, visible=True),       # feedback (avec explication)
            gr.update(value=f"Score : {score}/{len(qs)}"),     # score_display
            qs, index, score, finished, resume,                # states (5)
            gr.update(visible=True),                           # next_btn (visible pour continuer)
            gr.update(visible=False),                          # score_final_display
            gr.update(visible=False),                          # encouragement_display
            gr.update(visible=False),                          # bilan_theme_display
            gr.update(visible=False),                          # bilan_theme_table
            gr.update(visible=False),                          # details_title
            gr.update(visible=False),                          # resume_table
            gr.update(visible=False),                          # restart_btn
            gr.update(visible=False),                          # recap_block
        ]
    else:
        return [
            gr.update(visible=False),                          # start_btn
            gr.update(),                                       # question
            gr.update(interactive=False),                      # choix
            gr.update(value=(
                f"❌ Faux. Réponse correcte : {correct}\n\n{current_q.get('long_answer', '')}" 
                if current_q.get('long_answer') else f"❌ Faux. Réponse correcte : {correct}"
            )),                                                # feedback
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