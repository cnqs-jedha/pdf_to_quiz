# =========================
# APPLICATION PRINCIPALE GRADIO
# =========================
# Ce fichier contient la définition de l'interface utilisateur principale
# Il organise tous les composants de l'application et gère les interactions

# ============================================
# IMPORTS ET DÉPENDANCES
# ============================================

import os  # Pour les variables d'environnement
import json  # Pour manipuler les données JSON
import random  # Pour mélanger les questions
from pathlib import Path  # Pour gérer les chemins de fichiers

import gradio as gr  # Framework principal pour l'interface web
import pandas as pd  # Pour manipuler les tableaux de données
import requests  # Pour faire des requêtes HTTP vers l'API

# Imports des modules personnalisés
from core.config import API_BASE_URL, API_QUESTIONS_PATH, USE_API, REQUIRE_API, BASE_DIR, json_path  # Configuration
from core.check import check_ready_for_gradio  # Pour vérifier si l'API est prête
from core.helpers import load_questions  # Pour charger les questions
from ui.style import custom_css  # Styles CSS personnalisés
from ui.ui_gradio import start_quiz, check_answer, next_question, restart_quiz, send_drive_link_to_api  # Fonctions de l'interface

# ============================================
# CRÉATION DE L'INTERFACE PRINCIPALE
# ============================================

# Créer l'application Gradio avec les styles personnalisés
with gr.Blocks(css=custom_css, title="Quiz App") as app:
    
    # ============================================
    # PAGE D'ENTRÉE : SAISIE DU LIEN GOOGLE DRIVE
    # ============================================
    
    # Page d'erreur/entrée (visible par défaut)
    with gr.Column(visible=True) as page_erreur:
        gr.Markdown("Générez votre quiz via un lien Google Drive")
        drive_input = gr.Textbox(label="Lien Google Drive")  # Champ de saisie pour le lien
        send_quiz_button = gr.Button("Lancer la génération du quiz")  # Bouton pour lancer la génération
        # output = gr.Textbox(label="Statut", interactive=False)  # Champ de statut (commenté)
        # bouton_retry = gr.Button("🔄 Réessayer")  # Bouton de retry (commenté)

    # ============================================
    # PAGE DE CHARGEMENT : GÉNÉRATION EN COURS
    # ============================================
    
    # Page de chargement (masquée par défaut)
    with gr.Column(visible=False) as page_loader:
        gr.Markdown("### ⏳ Génération du quiz en cours...")
        loader_message = gr.Markdown("Merci de patienter pendant la création de votre quiz 🔄")

    # ============================================
    # PAGE PRINCIPALE : INTERFACE DU QUIZ
    # ============================================
    
    # Page quiz (masquée par défaut)
    with gr.Column(visible=False) as page_quiz:
        # ============================================
        # BLOC PRINCIPAL : INTERFACE DU QUIZ
        # ============================================
        
        with gr.Column(elem_classes=["block"]):
            # Bouton pour démarrer le quiz
            start_btn = gr.Button("🚀 Démarrer le quiz", variant="primary", elem_classes=["primary-btn"])
            
            # Barre de progression du quiz
            progress_bar = gr.HTML(visible=False, elem_id="quiz-progress")
            
            # Affichage de la question
            question = gr.Markdown(visible=False)
            
            # Options de réponse (boutons radio)
            choix = gr.Radio(choices=[], label="Choisis ta réponse :", visible=False, elem_classes=["quiz-radio"], container=False, elem_id="choices-radio")
            
            # Ligne contenant le bouton d'explication et le feedback
            with gr.Row():
                explain_btn = gr.Button("Voir l'explication", visible=False, elem_classes=["explain-btn-rect"])
                feedback = gr.Markdown(visible=False)
            
            # Zone d'affichage de l'explication
            explain_md = gr.Markdown(visible=False)
            
            # Zone pour les scripts (masquée)
            script_injector = gr.HTML(visible=False)
            
            # Affichage du score actuel
            score_display = gr.Markdown(visible=False)
            
            # Bouton pour passer à la question suivante
            next_btn = gr.Button("➡️ Question suivante", visible=False, variant="secondary")

        # ============================================
        # BLOC DE RÉCAPITULATIF : RÉSULTATS FINAUX
        # ============================================
        
        # Bloc de récapitulatif (masqué par défaut)
        with gr.Column(elem_classes=["block"], visible=False) as recap_block:
            gr.Markdown("### 📊 Résultats du quiz")
            
            # Affichage du score final avec style coloré
            score_final_display = gr.HTML(visible=False, elem_classes=["score-final"])
            
            # Message d'encouragement
            encouragement_display = gr.Markdown(visible=False, elem_classes=["encouragement"])
            
            # Bilan par thème
            bilan_theme_display = gr.Markdown(visible=False, elem_classes=["bilan-theme"])
            
            # Tableau du bilan par thème
            bilan_theme_table = gr.Dataframe(
                visible=False, label="", interactive=False, wrap=True, elem_classes=["dataframe"],
                headers=["Thème", "Bonnes réponses", "Questions", "% Réussite"]
            )
            
            # Titre pour les détails
            details_title = gr.Markdown(visible=False)
            
            # Tableau des résultats détaillés
            resume_table = gr.Dataframe(visible=False, label="Résultats détaillés", interactive=False, wrap=True,
                                        elem_classes=["dataframe"])
            
            # Bouton pour rejouer
            with gr.Row():
                restart_btn = gr.Button("🔄 Rejouer", visible=False, variant="primary", elem_classes=["primary-btn"])

    # ============================================
    # ÉTATS INTERNES DE L'APPLICATION
    # ============================================
    
    # États pour stocker les données du quiz
    qs_state = gr.State()  # Liste des questions
    idx_state = gr.State()  # Index de la question actuelle
    score_state = gr.State()  # Score actuel
    done_state = gr.State()  # État de fin de quiz
    resume_state = gr.State()  # Résumé des réponses
    explain_visible = gr.State(False)  # État de visibilité de l'explication

    # ============================================
    # DÉFINITION DES SORTIES COMMUNES
    # ============================================
    
    # Liste de tous les éléments qui peuvent être mis à jour
    outputs_common = [
        start_btn,  # Bouton démarrer
        question, progress_bar, choix, feedback, explain_btn, explain_md, script_injector, score_display,  # Éléments du quiz
        qs_state, idx_state, score_state, done_state, resume_state,  # États internes
        next_btn, score_final_display, encouragement_display, bilan_theme_display,  # Éléments de navigation
        bilan_theme_table, details_title, resume_table, restart_btn, recap_block  # Éléments de récapitulatif
    ]

    # ============================================
    # GESTIONNAIRES D'ÉVÉNEMENTS PRINCIPAUX
    # ============================================
    
    # Clic sur le bouton "Démarrer le quiz"
    start_btn.click(fn=start_quiz, outputs=outputs_common)
    
    # Changement de sélection dans les options de réponse
    choix.change(fn=check_answer,
                    inputs=[choix, qs_state, idx_state, score_state, done_state, resume_state],
                    outputs=outputs_common)
    
    # ============================================
    # FONCTION POUR PASSER À LA QUESTION SUIVANTE
    # ============================================
    
    def _next_question_with_reset(*args):
        """
        Passe à la question suivante en réinitialisant l'état d'explication.
        Cette fonction s'assure que l'explication est masquée avant de passer à la question suivante.
        """
        # Réinitialiser l'état d'explication avant de passer à la question suivante
        explain_visible.value = False
        return next_question(*args)
    
    # Clic sur le bouton "Question suivante"
    next_btn.click(fn=_next_question_with_reset,
                    inputs=[qs_state, idx_state, score_state, done_state, resume_state],
                    outputs=outputs_common)
    
    # ============================================
    # GESTION DU BOUTON D'EXPLICATION
    # ============================================
    
    def _toggle_explain(btn_text):
        """
        Bascule l'affichage de l'explication et change le texte du bouton.
        
        Cette fonction détecte le type de bouton (explication ou correction) 
        et adapte le texte en conséquence.
        
        Args:
            btn_text (str): Texte actuel du bouton
        
        Returns:
            tuple: Mises à jour pour l'explication et le bouton
        """
        # Basculer l'état de visibilité
        explain_visible.value = not explain_visible.value
        
        if explain_visible.value:
            # Si on affiche l'explication
            if "explication" in btn_text:
                return gr.update(visible=True), gr.update(value="Masquer l'explication")
            else:  # "correction" dans le texte
                return gr.update(visible=True), gr.update(value="Masquer la correction")
        else:
            # Si on masque l'explication
            if "explication" in btn_text:
                return gr.update(visible=False), gr.update(value="Voir l'explication")
            else:  # "correction" dans le texte
                return gr.update(visible=False), gr.update(value="Voir la correction")
    
    def _reset_explain_state():
        """
        Réinitialise l'état d'explication.
        Utilisée lors du passage à la question suivante.
        """
        # Réinitialiser l'état d'explication
        explain_visible.value = False
        return gr.update(visible=False), gr.update(value="Voir l'explication")
    
    # Clic sur le bouton d'explication
    explain_btn.click(fn=_toggle_explain, inputs=[explain_btn], outputs=[explain_md, explain_btn])
    
    # Clic sur le bouton "Rejouer"
    restart_btn.click(fn=restart_quiz, outputs=outputs_common)

    # ============================================
    # GESTIONNAIRE POUR LA GÉNÉRATION DU QUIZ
    # ============================================
    
    # Clic sur le bouton "Lancer la génération du quiz"
    # Cette fonction envoie le lien Google Drive à l'API et gère le processus de génération
    send_quiz_button.click(
        fn=send_drive_link_to_api,  # Fonction qui gère l'envoi du lien à l'API
        inputs=drive_input,  # Entrée : le lien Google Drive saisi par l'utilisateur
        outputs=[page_erreur, page_loader, page_quiz, loader_message]  # Sorties : les différentes pages et le message
    )

# ============================================
# LANCEMENT DE L'APPLICATION
# ============================================

if __name__ == "__main__":
    """
    Point d'entrée de l'application.
    Lance le serveur Gradio avec les paramètres de configuration.
    """
    app.launch( 
        server_name=os.getenv("GRADIO_SERVER_NAME", "0.0.0.0"),  # Adresse du serveur (par défaut : toutes les interfaces)
        server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860"))  # Port du serveur (par défaut : 7860)
    )
