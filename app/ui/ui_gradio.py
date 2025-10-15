# =========================
# FICHIER PRINCIPAL DE L'INTERFACE QUIZ
# =========================
# Ce fichier contient toute la logique de l'interface utilisateur pour le quiz
# Il gère l'affichage des questions, la vérification des réponses, et la navigation

# ============================================
# IMPORTS ET DÉPENDANCES
# ============================================

import os  # Pour les opérations sur le système de fichiers
import json  # Pour manipuler les données JSON
import random  # Pour mélanger les questions
import time  # Pour les délais d'attente
from pathlib import Path  # Pour gérer les chemins de fichiers

import gradio as gr  # Framework pour créer l'interface web
import pandas as pd  # Pour manipuler les tableaux de données
import requests  # Pour faire des requêtes HTTP vers l'API

# Imports des modules personnalisés
from core.helpers import build_resume_tables  # Pour construire les tableaux de résultats
from core.config import API_BASE_URL, API_QUESTIONS_PATH, USE_API, REQUIRE_API, BASE_DIR, json_path  # Configuration
from core.helpers import load_questions  # Pour charger les questions depuis l'API
from core.check import check_ready_api  # Pour vérifier si l'API est prête


# ============================================
# FONCTION PRINCIPALE : DÉMARRAGE DU QUIZ
# ============================================

def start_quiz():
    """
    Démarre un nouveau quiz en chargeant les questions depuis l'API.
    
    Cette fonction :
    1. Charge les questions depuis l'API ou le fichier local
    2. Sélectionne aléatoirement 10 questions maximum
    3. Initialise l'interface avec la première question
    4. Retourne tous les éléments de l'interface mis à jour
    
    Returns:
        list: Liste des mises à jour pour tous les éléments de l'interface
    """
    print("⏳ Chargement des questions depuis l'API...", flush=True)
    
    # Charger les questions depuis l'API ou le fichier local
    niveau = load_questions(API_BASE_URL, API_QUESTIONS_PATH, USE_API, REQUIRE_API, json_path)
    print(f"📋 {len(niveau)} questions récupérées", flush=True)

    # Vérifier qu'il y a des questions disponibles
    if not niveau:
        return [
            gr.update(visible=True),   # afficher page erreur
            gr.update(visible=False),  # masquer loader
            gr.update(visible=False),  # masquer quiz
            "❌ Aucun quiz trouvé. Veuillez relancer la génération."
        ]

    # Sélectionner aléatoirement 10 questions maximum
    qs = random.sample(niveau, min(10, len(niveau)))
    resume = []  # Liste pour stocker les résultats de chaque question
    
    # Générer l'interface pour la première question
    question_out, progress_html, choix_out, explain_md_out, script_injector_out, score_out, *states = update_ui(qs, 0, 0, False, "", resume)

    # Retourner les mises à jour pour tous les éléments de l'interface
    return [
        gr.update(visible=False),  # start_btn (masquer le bouton démarrer)
        question_out, progress_html, choix_out, explain_md_out, script_injector_out, score_out,
        *states,  # États internes (questions, index, score, etc.)
        gr.update(visible=False),  # next_btn (masquer le bouton suivant)
        gr.update(visible=False),  # score_final_display (masquer le score final)
        gr.update(visible=False),  # encouragement_display (masquer l'encouragement)
        gr.update(visible=False),  # bilan_theme_display (masquer le bilan par thème)
        gr.update(visible=False),  # bilan_theme_table (masquer le tableau de thèmes)
        gr.update(visible=False),  # details_title (masquer le titre des détails)
        gr.update(visible=False),  # resume_table (masquer le tableau de résumé)
        gr.update(visible=False),  # restart_btn (masquer le bouton rejouer)
        gr.update(visible=False),  # recap_block (masquer le bloc de récapitulatif)
    ]

def start_quiz_from_home():
    """Démarre le quiz depuis la page d’accueil (cache home, montre quiz)."""
    quiz_updates = start_quiz()

    return [gr.update(visible=False),  # home masqué
            gr.update(visible=False),  # loader masqué
            gr.update(visible=True)] + quiz_updates



# ============================================
# FONCTION DE MISE À JOUR DE L'INTERFACE
# ============================================

def update_ui(qs, index, score, finished, feedback_txt, resume):
    """
    Met à jour l'interface utilisateur pour afficher une question.
    
    Args:
        qs (list): Liste des questions du quiz
        index (int): Index de la question actuelle
        score (int): Score actuel de l'utilisateur
        finished (bool): Indique si le quiz est terminé
        feedback_txt (str): Texte de feedback à afficher
        resume (list): Liste des résultats des questions précédentes
    
    Returns:
        list: Mises à jour pour tous les éléments de l'interface
    """
    # Si on a dépassé le nombre de questions, afficher l'écran final
    if index >= len(qs):
        return list(update_final_screen(qs, score, resume))
    
    # Récupérer la question actuelle
    q = qs[index]
    total = len(qs)
    
    # Formater le numéro de question (ex: "01/10")
    numero = f"{index+1:02d}/{total:02d}"
    
    # Créer le HTML pour la question
    question_md = f"### {q['question']}"
    
    # Créer la barre de progression
    progress_percentage = ((index+1)/total)*100
    progress_html = f"<div class=\"bar\"><span style=\"width:{progress_percentage:.0f}%\"></span><div class=\"label\">Question {index+1:02d}/{total:02d}</div></div>"
    
    # Créer le texte du score
    score_txt = f"Score : {score:02d}"
    
    # Retourner les mises à jour pour tous les éléments
    return [
        gr.update(value=question_md, visible=True),           # question (afficher la question)
        gr.update(value=progress_html, visible=True),           # progress (afficher la barre de progression)
        gr.update(choices=q["options"], value=None, interactive=True, visible=True, elem_classes=["quiz-radio"], elem_id="choices-radio"),  # choix (options de réponse)
        # gr.update(value="", visible=False),            # feedback (masquer le feedback)
        # gr.update(visible=False, value="Voir l'explication"),   # explain_btn (masquer le bouton d'explication)
        gr.update(value=q.get("long_answer", ""), visible=False), # explain_md (masquer l'explication)
        gr.update(value="", visible=False),                     # script_injector (masquer les scripts)
        gr.update(value=score_txt, visible=True),               # score_display (afficher le score)
        qs, index, score, finished, resume                      # states (états internes)
    ]

def update_final_screen(qs, score, resume):
    finished = True
    total_questions = len(qs)
    pourcentage = (score / total_questions) * 100 if total_questions else 0

    if pourcentage == 100:
        score_class = "score-top"; encouragement = "🎉 Parfait ! Tu as tout réussi !"
    elif pourcentage >= 80:
        score_class = "score-good"; encouragement = "👍 Très bien joué !"
    elif pourcentage >= 60:
        score_class = "score-bof"; encouragement = "👏 Pas mal, continue comme ça !"
    else:
        score_class = "score-bad"; encouragement = "💪 Continue à t'entraîner !"

    dasharray = 283  # longueur approximative du cercle (2 * pi * r) avec r=45
    dashoffset = dasharray * (1 - pourcentage / 100)

    score_et_encouragement = f"""
    <div class="score-card {score_class}">
        <div class="score-jauge-container">
            <svg viewBox="0 0 100 100">
                <!-- Cercle de fond -->
                <circle cx="50" cy="50" r="45" stroke="#e6e6e6" stroke-width="10" fill="none" />
                
                <!-- Cercle de progression -->
                <circle
                    cx="50"
                    cy="50"
                    r="45"
                    stroke-width="10"
                    fill="none"
                    stroke-linecap="round"
                    stroke-dasharray="{dasharray}"
                    stroke-dashoffset="{dashoffset}"
                    transform="rotate(-90 50 50)"
                    class="jauge-circle {score_class}"
                    style="transition: stroke-dashoffset 0.6s ease;"
                />
            </svg>
            <div class="jauge-percentage-text {score_class}">
                {pourcentage:.0f}%
            </div>
        </div>
        <div class="score-text-container">
            <h3>Score final : {score}/{total_questions}</h3>
            <p>{encouragement}</p>
        </div>
    </div>
"""
# <div class="{score_class}">
#     <h3>🥇 Score final : {score}/{total_questions} ({pourcentage:.0f}%)</h3>
#     <p>{encouragement}</p>
# </div>

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
                        drive_id = metadata.get("file_id", "")
                        
                        if file_name not in file_pages:
                            file_pages[file_name] = {
                                "pages": set(),
                                "drive_id": drive_id
                            }
                        file_pages[file_name]["pages"].add(page)
                    
                    # Formater la liste
                    theme_info = f"**{theme}**\n"
                    for file_name, data in file_pages.items():
                        pages_list = sorted(list(data["pages"]))
                        pages_str = ", ".join(map(str, pages_list))
                        drive_id = data.get("drive_id", "")
                        drive_link = f"https://drive.google.com/file/d/{drive_id}/view" if drive_id else "#"
                        theme_info += f"  • {file_name} (pages: {pages_str}) [link:{drive_link}]\n"

                    themes_details.append(theme_info.strip())
            
            if themes_details:
                # themes_a_reviser = f"**📚 À réviser en priorité :**\n\n" + "\n\n".join(themes_details)
                # Construire les "cartes" HTML
                cards_html = ""
                for theme_info in themes_details:
                    lines = theme_info.split("\n")
                    theme_name = lines[0].replace("**", "")  # Supprimer la mise en forme Markdown
                    file_lines = lines[1:]  # Le reste correspond aux fichiers et pages


                    file_html = ""
                    for file_line in file_lines:    
                        if "(pages:" in file_line:
                            # Exemple de ligne :
                            # "  • feodalite.pdf (pages: 1, 2) [link:https://drive.google.com/.../view]"

                            # --- Séparation du lien Google Drive s'il est présent ---
                            parts = file_line.split("[link:")
                            file_part = parts[0].strip()
                            drive_link = parts[1].strip("]") if len(parts) > 1 else "#"

                            # --- Extraire le nom du fichier et les pages ---
                            file_name, pages_part = file_part.split("(pages:")
                            pages_clean = pages_part.strip(") ").strip()
                            file_html += f"""
                                        <a href="{drive_link}" target="_blank" class="study-card">
                                            <div class="pdf-icon-container">
                                                <svg class="pdf-icon-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 75.320129 92.604164">
                                                    <g transform="translate(53.548057 -183.975276) scale(1.4843)">
                                                        <path fill="#ff2116" d="M-29.632812 123.94727c-3.551967 0-6.44336 2.89347-6.44336 6.44531v49.49804c0 3.55185 2.891393 6.44532 6.44336 6.44532H8.2167969c3.5519661 0 6.4433591-2.89335 6.4433591-6.44532v-40.70117s.101353-1.19181-.416015-2.35156c-.484969-1.08711-1.275391-1.84375-1.275391-1.84375a1.0584391 1.0584391 0 0 0-.0059-.008l-9.3906254-9.21094a1.0584391 1.0584391 0 0 0-.015625-.0156s-.8017392-.76344-1.9902344-1.27344c-1.39939552-.6005-2.8417968-.53711-2.8417968-.53711l.021484-.002z" color="#000" font-family="sans-serif" overflow="visible" paint-order="markers fill stroke" style="line-height:normal;font-variant-ligatures:normal;font-variant-position:normal;font-variant-caps:normal;font-variant-numeric:normal;font-variant-alternates:normal;font-feature-settings:normal;text-indent:0;text-align:start;text-decoration-line:none;text-decoration-style:solid;text-decoration-color:#000000;text-transform:none;text-orientation:mixed;white-space:normal;shape-padding:0;isolation:auto;mix-blend-mode:normal;solid-color:#000000;solid-opacity:1"/>
                                                        <path fill="#f5f5f5" d="M-29.632812 126.06445h28.3789058a1.0584391 1.0584391 0 0 0 .021484 0s1.13480448.011 1.96484378.36719c.79889772.34282 1.36536982.86176 1.36914062.86524.0000125.00001.00391.004.00391.004l9.3671868 9.18945s.564354.59582.837891 1.20899c.220779.49491.234375 1.40039.234375 1.40039a1.0584391 1.0584391 0 0 0-.002.0449v40.74609c0 2.41592-1.910258 4.32813-4.3261717 4.32813H-29.632812c-2.415914 0-4.326172-1.91209-4.326172-4.32813v-49.49804c0-2.41603 1.910258-4.32813 4.326172-4.32813z" color="#000" font-family="sans-serif" overflow="visible" paint-order="markers fill stroke" style="line-height:normal;font-variant-ligatures:normal;font-variant-position:normal;font-variant-caps:normal;font-variant-numeric:normal;font-variant-alternates:normal;font-feature-settings:normal;text-indent:0;text-align:start;text-decoration-line:none;text-decoration-style:solid;text-decoration-color:#000000;text-transform:none;text-orientation:mixed;white-space:normal;shape-padding:0;isolation:auto;mix-blend-mode:normal;solid-color:#000000;solid-opacity:1"/>
                                                        <path fill="#ff2116" d="M-23.40766 161.09299c-1.45669-1.45669.11934-3.45839 4.39648-5.58397l2.69124-1.33743 1.04845-2.29399c.57665-1.26169 1.43729-3.32036 1.91254-4.5748l.8641-2.28082-.59546-1.68793c-.73217-2.07547-.99326-5.19438-.52872-6.31588.62923-1.51909 2.69029-1.36323 3.50626.26515.63727 1.27176.57212 3.57488-.18329 6.47946l-.6193 2.38125.5455.92604c.30003.50932 1.1764 1.71867 1.9475 2.68743l1.44924 1.80272 1.8033728-.23533c5.72900399-.74758 7.6912472.523 7.6912472 2.34476 0 2.29921-4.4984914 2.48899-8.2760865-.16423-.8499666-.59698-1.4336605-1.19001-1.4336605-1.19001s-2.3665326.48178-3.531704.79583c-1.202707.32417-1.80274.52719-3.564509 1.12186 0 0-.61814.89767-1.02094 1.55026-1.49858 2.4279-3.24833 4.43998-4.49793 5.1723-1.3991.81993-2.86584.87582-3.60433.13733zm2.28605-.81668c.81883-.50607 2.47616-2.46625 3.62341-4.28553l.46449-.73658-2.11497 1.06339c-3.26655 1.64239-4.76093 3.19033-3.98386 4.12664.43653.52598.95874.48237 2.01093-.16792zm21.21809-5.95578c.80089-.56097.68463-1.69142-.22082-2.1472-.70466-.35471-1.2726074-.42759-3.1031574-.40057-1.1249.0767-2.9337647.3034-3.2403347.37237 0 0 .993716.68678 1.434896.93922.58731.33544 2.0145161.95811 3.0565161 1.27706 1.02785.31461 1.6224.28144 2.0729-.0409zm-8.53152-3.54594c-.4847-.50952-1.30889-1.57296-1.83152-2.3632-.68353-.89643-1.02629-1.52887-1.02629-1.52887s-.4996 1.60694-.90948 2.57394l-1.27876 3.16076-.37075.71695s1.971043-.64627 2.97389-.90822c1.0621668-.27744 3.21787-.70134 3.21787-.70134zm-2.74938-11.02573c.12363-1.0375.1761-2.07346-.15724-2.59587-.9246-1.01077-2.04057-.16787-1.85154 2.23517.0636.8084.26443 2.19033.53292 3.04209l.48817 1.54863.34358-1.16638c.18897-.64151.47882-2.02015.64411-3.06364z"/>
                                                        <path fill="#2c2c2c" d="M-20.930423 167.83862h2.364986q1.133514 0 1.840213.2169.706698.20991 1.189489.9446.482795.72769.482795 1.75625 0 .94459-.391832 1.6233-.391833.67871-1.056548.97958-.65772.30087-2.02913.30087h-.818651v3.72941h-1.581322zm1.581322 1.22447v3.33058h.783664q1.049552 0 1.44838-.39184.405826-.39183.405826-1.27345 0-.65772-.265887-1.06355-.265884-.41282-.587747-.50378-.314866-.098-1.000572-.098zm5.50664-1.22447h2.148082q1.560333 0 2.4909318.55276.9375993.55276 1.4133973 1.6443.482791 1.09153.482791 2.42096 0 1.3994-.4338151 2.49793-.4268149 1.09153-1.3154348 1.76324-.8816233.67172-2.5189212.67172h-2.267031zm1.581326 1.26645v7.018h.657715q1.378411 0 2.001144-.9516.6227329-.95858.6227329-2.5539 0-3.5125-2.6238769-3.5125zm6.4722254-1.26645h5.30372941v1.26645H-4.2075842v2.85478h2.9807225v1.26646h-2.9807225v4.16322h-1.5813254z" font-family="Franklin Gothic Medium Cond" letter-spacing="0" style="line-height:125%;-inkscape-font-specification:'Franklin Gothic Medium Cond'" word-spacing="4.26000023"/>
                                                    </g>
                                                </svg>
                                            </div>
                                            <div class="study-card-content">
                                                <span class="theme-tag">{theme_name}</span>
                                                <p>{file_name.strip('• ').strip()}</p>
                                                <span class="pdf-pages">pages {pages_part.strip(') ')}</span>


                                            </div>
                                        </a>
                                        """# TRANSFORMER EN LIEN CLICABLE VERS LE BON PDF 
                                                # {f'<a href="{drive_link}" target="_blank" class="drive-link">{drive_id}</a>' if drive_id else ''}

                    # cards_html += f"""
                    # <div class="study-theme-container">
                    #     <h4>{theme_name}</h4>
                    #     <div class="study-card-container">
                    #         {file_html}
                    #     </div>
                    # </div>
                    # """

                    cards_html += f"""{file_html}"""

                # Encapsuler dans un conteneur global
                themes_a_reviser = f"""
                <div class="study-container">
                    <h3 class="study-title">Fiche de révision</h3>
                    <p class="study-intro">La fiche de révision met en avant les documents sur lesquels tu as fait des erreurs.</p>
                    <div class="study-card-container">
                        {cards_html}
                    </div>
                </div>
                """

    detailed_copy = detailed.copy() if not detailed.empty else detailed

    return [
        gr.update(value="<h3 class=\"quiz-finish-title\"> 🎯 Quiz terminé !</h3>", visible=True),   # question (titre final)
        gr.update(visible=False),                                  # progress_bar
        gr.update(visible=False),                                  # choix
        # gr.update(visible=False),                                  # feedback teaser
        # gr.update(visible=False),                                  # explain_btn
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

# ============================================
# FONCTION DE VÉRIFICATION DES RÉPONSES
# ============================================

def check_answer(reponse, qs, index, score, finished, resume):
    """
    Vérifie si la réponse de l'utilisateur est correcte et met à jour l'interface.
    
    Cette fonction :
    1. Vérifie si la réponse est correcte
    2. Met à jour le score si nécessaire
    3. Affiche le bouton d'explication avec le bon texte
    4. Applique les styles visuels appropriés (vert pour correct, rouge pour incorrect)
    
    Args:
        reponse (str): La réponse sélectionnée par l'utilisateur
        qs (list): Liste des questions du quiz
        index (int): Index de la question actuelle
        score (int): Score actuel de l'utilisateur
        finished (bool): Indique si le quiz est terminé
        resume (list): Liste des résultats des questions précédentes
    
    Returns:
        list: Mises à jour pour tous les éléments de l'interface
    """
    if finished or reponse is None:
        return [gr.update()] * 22  # (moins d'éléments car explain_btn supprimé)

    current_q = qs[index]
    correct = current_q.get("llm_response", {}).get("correct_answer", {}).get("answer") \
              or current_q.get("réponse")

    is_correct = reponse == correct
    resultat = "✅" if is_correct else "❌"

    resume.append({
        "Thème": current_q.get("theme", "Sans thème"),
        "Question": current_q["question"],
        "Ta réponse": reponse,
        "Bonne réponse": correct,
        "Résultat": resultat,
        "Correct": is_correct,
    })

    if is_correct:
        score += 1
        # feedback_html = f"### ✅ Bonne réponse !"
        explain_html = f"""
        <h3 class="answer-intro-bravo">✅ Bravo, c'est une bonne réponse !</h3>
        <div class="answer-container correct">
            <p class="answer-explication-title">Explication :</p>
            <div class="answer-long-text">{current_q.get('long_answer', '')}</div>
        </div>
        """
        choix_style = ["quiz-radio", "correct"]
    else:
        # feedback_html = f"### ❌ Mauvaise réponse. <br>✅ Bonne réponse : **{correct}**"
        explain_html = f"""
        <div class="wrong-title-container">
            <h3 class="answer-intro-wrong">❌ Mauvaise réponse, la bonne réponse était :</h3>
            <div class="answer-correction">✅ <i>"{correct}"</i></div>
        </div>
        <div class="answer-container wrong">
            <p class="answer-explication-title">Explication :</p>
            <div class="answer-long-text">{current_q.get('long_answer', '')}</div>
        </div>
        """
        choix_style = ["quiz-radio", "wrong"]

    # Retourner les mises à jour
    return [
        gr.update(visible=False),          # start_btn
        gr.update(),                       # question
        gr.update(),                       # progress bar
        gr.update(interactive=False, elem_classes=choix_style),  # désactiver radio
        # gr.update(value=feedback_html, visible=True),            # feedback (affiché)
        gr.update(value=explain_html, visible=True),             # explain_md (affiché directement)
        gr.update(value="", visible=False),                      # script_injector
        gr.update(value=f"Score : {score:02d}", visible=True),   # score_display
        qs, index, score, finished, resume,
        gr.update(visible=True),           # next_btn visible
        gr.update(visible=False),          # score_final_display
        gr.update(visible=False),          # encouragement_display
        gr.update(visible=False),          # bilan_theme_display
        gr.update(visible=False),          # bilan_theme_table
        gr.update(visible=False),          # details_title
        gr.update(visible=False),          # resume_table
        gr.update(visible=False),          # restart_btn
        gr.update(visible=False),          # recap_block
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
    """Envoie le lien Google Drive à l’API, affiche le loader, puis montre le quiz quand prêt."""

    # 1️⃣ Vérif du lien
    if not drive_link or "drive.google.com" not in drive_link:
        print('lien drive invalide', flush=True)
        yield [
            gr.update(visible=True),   # page_erreur visible
            gr.update(visible=False),  # loader masqué
            gr.update(visible=False),  # quiz masqué
            "❌ Lien Google Drive invalide."
        ]
        return

    # 2️⃣ Envoi du lien à l’API
    try:
        # print('try', flush=True)
        resp = requests.post(
            f"{API_BASE_URL}/run_pipeline",
            json={"drive_link": drive_link},
            timeout=15
        )
        # print(f"Status code: {resp.status_code}", flush=True)
        # print(f"Response text: {resp.text}", flush=True)
        if resp.status_code != 200:
            print('try code not 200')
            yield [
                gr.update(visible=True),
                gr.update(visible=False),
                gr.update(visible=False),
                f"⚠️ Erreur API : {resp.text}"
            ]
            return
    except Exception as e:
        # print('except', flush=True)
        # print(traceback.format_exc(), flush=True)
        yield [
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
            f"❌ Erreur de connexion à l’API : {e}"
        ]
        return

    # 3️⃣ Passage à la page de chargement
    # print('loader here', flush=True)
    yield [
        gr.update(visible=False),  # page_erreur masquée
        gr.update(visible=True),   # page_loader affichée
        gr.update(visible=False),  # page_quiz masquée
        "🚀 Pipeline lancée, génération du quiz en cours..."
    ]

    # 4️⃣ Boucle d’attente non bloquante
    for i in range(240):  # 60 x 5s = 5 minutes max
        # print('await function', flush=True)
        time.sleep(5)
        quiz_ready, quiz_data = check_ready_api()
        message = quiz_data.get("message", "Traitement en cours...")

        yield [
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=False),
            f"⏳ {message} ({(i+1)*5} sec)"
        ]

        if quiz_ready:
            # print('quiz ready', flush=True)
            time.sleep(2)
            yield [
                gr.update(visible=False),  # cacher page erreur
                gr.update(visible=False),  # cacher loader
                gr.update(visible=True),   # afficher quiz
                "✅ Quiz prêt !"
            ]
            return

    # 5️⃣ Timeout après 5 min
    # print('time out', flush=True)
    yield [
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False),
        "❌ Temps d’attente dépassé. Le quiz n’a pas pu être généré."
    ]