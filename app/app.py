import os
import json
import random
from pathlib import Path

import gradio as gr
import pandas as pd
import requests

from core.config import API_BASE_URL, API_QUESTIONS_PATH, USE_API, REQUIRE_API, BASE_DIR, json_path
from core.check import check_ready_for_gradio
from core.helpers import load_questions
from ui.style import custom_css
from ui.ui_gradio import start_quiz, check_answer, next_question, restart_quiz

with gr.Blocks(css=custom_css, title="Quiz App") as app:
    # Page erreur
    with gr.Column(visible=True) as page_erreur:
        gr.Markdown("# ⚠️ Impossible de lancer le quiz")
        gr.Markdown("L’API est vide.")
        bouton_retry = gr.Button("🔄 Réessayer")

    # Page quiz
    with gr.Column(visible=False) as page_quiz:
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

    # Quand je clique sur "Réessayer" → teste l’API
    bouton_retry.click(fn=check_ready_for_gradio, outputs=[page_erreur, page_quiz])


if __name__ == "__main__":
    app.launch( 
        server_name=os.getenv("GRADIO_SERVER_NAME", "0.0.0.0"),
        server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860"))
    )
