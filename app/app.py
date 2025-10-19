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
from fastapi.staticfiles import StaticFiles


# Imports des modules personnalisés
from core.config import API_BASE_URL, API_QUESTIONS_PATH, USE_API, REQUIRE_API, BASE_DIR, json_path  # Configuration
from core.check import check_ready_for_gradio  # Pour vérifier si l'API est prête
from core.helpers import load_questions  # Pour charger les questions
from ui.style import custom_css  # Styles CSS personnalisés
from ui.ui_gradio import start_quiz, start_quiz_from_home, start_quiz_from_history, start_quiz_from_stats, check_answer, next_question, restart_quiz, send_drive_link_to_api, show_user_history  # Fonctions de l'interface

# ============================================
# CRÉATION DE L'INTERFACE PRINCIPALE
# ============================================

# Créer l'application Gradio avec les styles personnalisés
with gr.Blocks(css=custom_css, title="Quiz App") as app:
    
    # ============================================
    # PAGE D'ENTRÉE : SAISIE DU LIEN GOOGLE DRIVE
    # ============================================
    
    # Page d'erreur/entrée (visible par défaut)
    with gr.Column(visible=True, elem_classes=["home"]) as home:
        gr.Markdown(
            """
            <h1 class="title">
                🎓 Bienvenue sur le Générateur de Quiz
            </h1>
            <p class="intro">
                Crée un quiz à partir de tes documents ou reprends un quiz déjà généré par tes soins.
            </p>
            """,
            elem_classes=["main-title"]
        )

        # 📦 Deux colonnes : gauche (drive), droite (quiz déjà prêt)
        with gr.Row():
            with gr.Column(scale=1, elem_classes=["col-block"]):
                gr.Markdown(
                    "### Génére ton quiz via un lien Google Drive",
                    elem_id="subtitle-left"
                )
                drive_input = gr.Textbox(
                    label="Lien Google Drive",
                    placeholder="https://drive.google.com/...",
                    lines=1
                )
                send_quiz_button = gr.Button(
                    "Générer le quiz",
                    variant="primary",
                    elem_classes=["primary-btn"]
                )

            with gr.Column(scale=1, elem_classes=["col-block"]):
                gr.Markdown(
                    """
                    <h3 class="title">Tu as déjà généré un quiz ?</h3>
                    <p class="intro">Lance un quiz que tu as déja généré.</p>
                    """,
                    elem_classes=["right-col-title"]
                )
                # Bouton pour voir l'historique
                view_history_btn = gr.Button(
                    "Voir mes statistiques",
                    # variant="secondary",
                    elem_classes=["tertiary-btn"]
                )
                restart_quiz_home = gr.Button(
                    "Tester mes connaissances",
                    variant="secondary",
                    elem_classes=["secondary-btn"]
                )
                
                


    # ============================================
    # PAGE DE CHARGEMENT : GÉNÉRATION EN COURS
    # ============================================
    
    # Page de chargement (masquée par défaut)
    with gr.Column(visible=False, elem_classes=["loading-page"]) as page_loader:
        with gr.Column(elem_classes=["loader-component"]):
            gr.HTML(
                """
                <div class="loader">
                    <div class="loader__bar"></div>
                    <div class="loader__bar"></div>
                    <div class="loader__bar"></div>
                    <div class="loader__bar"></div>
                    <div class="loader__bar"></div>
                    <div class="loader__ball"></div>
                </div>
                """,
                elem_id="loading-animation"
            )
            
            loader_message = gr.Markdown(
                "Merci de patienter pendant la création de votre quiz...",
                elem_classes=["loading-text"]
            )

    # ============================================
    # PAGE PRINCIPALE : INTERFACE DU QUIZ
    # ============================================
    
    # Page quiz (masquée par défaut)
    with gr.Column(visible=False, elem_classes=["quiz"]) as page_quiz:
        # ============================================
        # BLOC PRINCIPAL : INTERFACE DU QUIZ
        # ============================================
        
        with gr.Column():
            # Bouton pour démarrer le quiz
            start_btn = gr.Button("🚀 Démarrer le quiz", variant="primary", elem_classes=["primary-btn"])
            
            with gr.Row(elem_classes=["loader-questions"]):
                # Barre de progression du quiz
                progress_bar = gr.HTML(visible=False, elem_id="quiz-progress")
                
                # Affichage du score actuel
                score_display = gr.Markdown(visible=False, elem_classes=["current-score"])
            
            # Affichage de la question
            question = gr.Markdown(visible=False)
            
            # Options de réponse (boutons radio)
            choix = gr.Radio(choices=[], label="Choisis ta réponse :", visible=False, elem_classes=["quiz-radio"], container=False, elem_id="choices-radio")

            # Bouton pour passer à la question suivante
            next_btn = gr.Button("Question suivante", visible=False, variant="primary", elem_classes=["primary-btn"])
            
            # Zone d'affichage de l'explication
            explain_md = gr.HTML(visible=False)
            
            # Zone pour les scripts (masquée)
            script_injector = gr.HTML(visible=False)
            
            
            

    # ============================================
    # PAGE DÉDIÉE AUX STATISTIQUES
    # ============================================
    
    # Page des statistiques (masquée par défaut)
    with gr.Column(elem_classes=["stats-page"], visible=False) as stats_page:
        gr.Markdown(
            """
            <h1 class="stats-page-title">Mes Statistiques</h1>
            <p class="stats-page-subtitle">Consulte tes performances et ton évolution</p>
            """,
            elem_classes=["stats-header"]
        )
        
        # Statistiques générales
        stats_display = gr.HTML(visible=False, elem_classes=["stats-container"])
        
        # Graphique des performances par thème
        theme_performance_chart = gr.Plot(visible=False, elem_classes=["chart-container"])
        
        # Tableau des sessions passées (maintenant en HTML)
        sessions_table = gr.HTML(
            visible=False, 
            elem_classes=["sessions-table"]
        )
        
        # Boutons de navigation
        with gr.Row():
            back_to_home_btn = gr.Button("Retour à l'accueil", variant="secondary", elem_classes=["secondary-btn"])
            new_quiz_from_stats_btn = gr.Button("Nouveau quiz", variant="primary", elem_classes=["primary-btn"])

    # ============================================
    # BLOC D'HISTORIQUE : STATISTIQUES UTILISATEUR (ANCIEN - À SUPPRIMER)
    # ============================================
    
    # Bloc d'historique (masqué par défaut) - CONSERVÉ POUR COMPATIBILITÉ
    with gr.Column(elem_classes=["history"], visible=False) as history_block:
        gr.Markdown("### 📊 Historique de tes performances")
        
        # Statistiques générales
        stats_display_old = gr.HTML(visible=False, elem_classes=["stats-container"])
        
        # Graphique des performances par thème
        theme_performance_chart_old = gr.Plot(visible=False, elem_classes=["chart-container"])
        
        # Tableau des sessions passées
        sessions_table_old = gr.Dataframe(
            visible=False, 
            label="Sessions précédentes", 
            interactive=False, 
            wrap=True, 
            elem_classes=["dataframe", "sessions-table"],
            headers=["Date", "Score", "Questions", "Thèmes", "Progression"]
        )
        
        # Bouton pour revenir au quiz
        back_to_quiz_btn = gr.Button("🔄 Nouveau quiz", visible=False, variant="primary", elem_classes=["primary-btn"])

    # ============================================
    # BLOC DE RÉCAPITULATIF : RÉSULTATS FINAUX
    # ============================================
    
    # Bloc de récapitulatif (masqué par défaut)
    with gr.Column(elem_classes=["recap"], visible=False) as recap_block:
        # gr.Markdown("### 📊 Résultats du quiz")
        
        # Affichage du score final avec style coloré
        score_final_display = gr.HTML(visible=False, elem_classes=["score-final"])
        
        # Message d'encouragement
        encouragement_display = gr.HTML(visible=False, elem_classes=["encouragement"])
        
        # Bilan par thème
        bilan_theme_display = gr.HTML(visible=False, elem_classes=["bilan-theme"])
        
        # Tableau du bilan par thème
        bilan_theme_table = gr.Dataframe(
            visible=False, label="", interactive=False, wrap=True, elem_classes=["dataframe"],
            headers=["Thème", "Bonnes réponses", "Questions", "% Réussite"]
        )
        
        # Titre pour les détails
        details_title = gr.Markdown(visible=False)
        details_html = gr.HTML(visible=False, elem_classes=["details-table"])
        
        # Tableau des résultats détaillés
        resume_table = gr.Dataframe(visible=False, label="Résultats détaillés", interactive=False, wrap=True,
                                    elem_classes=["dataframe"])
        
        # Boutons pour rejouer et voir les statistiques
        with gr.Row():
            restart_btn = gr.Button("Rejouer", visible=False, variant="primary", elem_classes=["primary-btn"])
            view_stats_btn = gr.Button("Voir mes statistiques", visible=False, variant="secondary", elem_classes=["secondary-btn"])

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
        question, progress_bar, choix, explain_md, script_injector, score_display,  # Éléments du quiz
        qs_state, idx_state, score_state, done_state, resume_state,  # États internes
        next_btn, score_final_display, encouragement_display, bilan_theme_display,  # Éléments de navigation
        bilan_theme_table, details_title, details_html, resume_table, restart_btn, view_stats_btn, recap_block  # Éléments de récapitulatif
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
    
    # Clic sur le bouton "Rejouer"
    restart_btn.click(fn=restart_quiz, outputs=outputs_common)
    
    # Clic sur le bouton "Voir mes statistiques" depuis l'écran final
    view_stats_btn.click(
        fn=show_user_history,
        outputs=[home, page_loader, page_quiz, stats_page, stats_display, theme_performance_chart, sessions_table, back_to_home_btn, new_quiz_from_stats_btn, recap_block]
    )

    # Clic sur le bouton "Rejouer" sur l'écran d'accueil
    restart_quiz_home.click(
        fn=start_quiz_from_home,
        outputs=[home, page_loader, page_quiz] + outputs_common
    )
    
    # Clic sur le bouton "Voir mes statistiques"
    view_history_btn.click(
        fn=show_user_history,
        outputs=[home, page_loader, page_quiz, stats_page, stats_display, theme_performance_chart, sessions_table, back_to_home_btn, new_quiz_from_stats_btn, recap_block]
    )
    
    # Clic sur le bouton "Nouveau quiz" depuis l'historique
    back_to_quiz_btn.click(
        fn=start_quiz_from_history,
        outputs=[home, page_loader, page_quiz, history_block] + outputs_common
    )
    
    # Clic sur le bouton "Retour à l'accueil" depuis les statistiques
    back_to_home_btn.click(
        fn=lambda: [gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)],
        outputs=[home, page_loader, page_quiz, stats_page]
    )
    
    # Clic sur le bouton "Nouveau quiz" depuis les statistiques
    new_quiz_from_stats_btn.click(
        fn=start_quiz_from_stats,
        outputs=[home, page_loader, page_quiz, stats_page] + outputs_common
    )

    # ============================================
    # GESTIONNAIRE POUR LA GÉNÉRATION DU QUIZ
    # ============================================
    
    # Clic sur le bouton "Lancer la génération du quiz"
    # Cette fonction envoie le lien Google Drive à l'API et gère le processus de génération
    send_quiz_button.click(
        fn=send_drive_link_to_api,  # Fonction qui gère l'envoi du lien à l'API
        inputs=drive_input,  # Entrée : le lien Google Drive saisi par l'utilisateur
        outputs=[home, page_loader, page_quiz, loader_message]  # Sorties : les différentes pages et le message
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
