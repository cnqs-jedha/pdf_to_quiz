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
from ui.ui_gradio import start_quiz, check_answer, next_question, restart_quiz, send_drive_link_to_api

with gr.Blocks(css=custom_css, title="Quiz App") as app:
    # Page erreur
    with gr.Column(visible=True) as page_erreur:
        gr.Markdown("Générez votre quiz via un lien Google Drive")
        drive_input = gr.Textbox(label="Lien Google Drive")
        send_quiz_button = gr.Button("Lancer la génération du quiz")
        # output = gr.Textbox(label="Statut", interactive=False)
        # bouton_retry = gr.Button("🔄 Réessayer")

    # Page de chargement (loader)
    with gr.Column(visible=False) as page_loader:
        gr.Markdown("### ⏳ Génération du quiz en cours...")
        loader_message = gr.Markdown("Merci de patienter pendant la création de votre quiz 🔄")

    # Page quiz
    with gr.Column(visible=False) as page_quiz:
        with gr.Column(elem_classes=["block"]):
            start_btn = gr.Button("🚀 Démarrer le quiz", variant="primary", elem_classes=["primary-btn"])
            progress_bar = gr.HTML(visible=False, elem_id="quiz-progress")
            question = gr.Markdown(visible=False)
            choix = gr.Radio(choices=[], label="Choisis ta réponse :", visible=False, elem_classes=["quiz-radio"], container=False, elem_id="choices-radio")
            with gr.Row():
                explain_btn = gr.Button("Voir l'explication", visible=False, elem_classes=["explain-btn-rect"])
                feedback = gr.Markdown(visible=False)
            explain_md = gr.Markdown(visible=False)
            script_injector = gr.HTML(visible=False)
            score_display = gr.Markdown(visible=False)
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
    explain_visible = gr.State(False)

    outputs_common = [
        start_btn,
        question, progress_bar, choix, feedback, explain_btn, explain_md, script_injector, score_display,
        qs_state, idx_state, score_state, done_state, resume_state,
        next_btn, score_final_display, encouragement_display, bilan_theme_display,
        bilan_theme_table, details_title, resume_table, restart_btn, recap_block
    ]

    start_btn.click(fn=start_quiz, outputs=outputs_common)
    choix.change(fn=check_answer,
                    inputs=[choix, qs_state, idx_state, score_state, done_state, resume_state],
                    outputs=outputs_common)
    def _next_question_with_reset(*args):
        # Réinitialiser l'état d'explication avant de passer à la question suivante
        explain_visible.value = False
        return next_question(*args)
    
    next_btn.click(fn=_next_question_with_reset,
                    inputs=[qs_state, idx_state, score_state, done_state, resume_state],
                    outputs=outputs_common)
    
    def _toggle_explain():
        # Basculer l'état
        explain_visible.value = not explain_visible.value
        if explain_visible.value:
            return gr.update(visible=True), gr.update(value="Masquer l'explication")
        else:
            return gr.update(visible=False), gr.update(value="Voir l'explication")
    
    def _reset_explain_state():
        # Réinitialiser l'état d'explication
        explain_visible.value = False
        return gr.update(visible=False), gr.update(value="Voir l'explication")
    
    explain_btn.click(fn=_toggle_explain, outputs=[explain_md, explain_btn])
    restart_btn.click(fn=restart_quiz, outputs=outputs_common)

    # Quand je clique sur "Réessayer" → teste l’API
    # bouton_retry.click(fn=check_ready_for_gradio, outputs=[page_erreur, page_quiz])
    send_quiz_button.click(
        fn=send_drive_link_to_api, 
        inputs=drive_input, 
        outputs=[page_erreur, page_loader, page_quiz, loader_message]
    )



if __name__ == "__main__":
    app.launch( 
        server_name=os.getenv("GRADIO_SERVER_NAME", "0.0.0.0"),
        server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860"))
    )
