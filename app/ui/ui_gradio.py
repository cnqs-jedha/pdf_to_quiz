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
    question_out, progress_html, choix_out, feedback_out, explain_btn_out, explain_md_out, script_injector_out, score_out, *states = update_ui(qs, 0, 0, False, "", resume)

    # Retourner les mises à jour pour tous les éléments de l'interface
    return [
        gr.update(visible=False),  # start_btn (masquer le bouton démarrer)
        question_out, progress_html, choix_out, feedback_out, explain_btn_out, explain_md_out, script_injector_out, score_out,
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
        gr.update(value="", visible=False),            # feedback (masquer le feedback)
        gr.update(visible=False, value="Voir l'explication"),   # explain_btn (masquer le bouton d'explication)
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
    # Si le quiz est terminé ou aucune réponse n'a été sélectionnée, ne rien faire
    if finished or reponse is None:
        return [gr.update()] * 23

    # Récupérer la question actuelle
    current_q = qs[index]
    
    # Récupérer la bonne réponse depuis la structure JSON
    # Support de deux formats : nouveau (llm_response) et ancien (réponse)
    if "llm_response" in current_q and "correct_answer" in current_q["llm_response"]:
        correct = current_q["llm_response"]["correct_answer"]["answer"]
    else:
        correct = current_q["réponse"]  # fallback pour l'ancienne structure
    
    # Déterminer si la réponse est correcte
    is_correct = reponse == correct
    resultat = "✅" if is_correct else "❌"

    # Ajouter le résultat à la liste des réponses
    resume.append({
        "Thème": current_q.get("theme", "Sans thème"),
        "Question": current_q["question"],
        "Ta réponse": reponse,
        "Bonne réponse": correct,
        "Résultat": resultat,
        "Correct": is_correct,
    })

    # Si la réponse est correcte
    if is_correct:
        score += 1  # Incrémenter le score
        explication = current_q.get("long_answer", "")
        feedback_txt = ""
        
        return [
            gr.update(visible=False),                          # start_btn (masquer le bouton démarrer)
            gr.update(),                                       # question (garder la question)
            gr.update(),                                       # progress_html (garder la barre de progression)
            gr.update(interactive=False,                       # choix (désactiver les options)
                      elem_classes=["quiz-radio","correct", f"correct-{correct}"]),  # Appliquer le style vert
            gr.update(value=feedback_txt, visible=False),       # feedback (masquer le feedback)
            gr.update(visible=True, value="Voir l'explication"),  # explain_btn (afficher avec texte "explication")
            gr.update(value=f"<div class=\"explain-content\">{current_q.get('long_answer','')}</div>", visible=False),  # explain_md (préparer l'explication)
            gr.update(value="", visible=False),                     # script_injector (masquer les scripts)
            gr.update(value=f"Score : {score:02d}"),     # score_display (mettre à jour le score)
            qs, index, score, finished, resume,                # states (états internes)
            gr.update(visible=True),                           # next_btn (afficher le bouton suivant)
            gr.update(visible=False),                          # score_final_display (masquer le score final)
            gr.update(visible=False),                          # encouragement_display (masquer l'encouragement)
            gr.update(visible=False),                          # bilan_theme_display (masquer le bilan par thème)
            gr.update(visible=False),                          # bilan_theme_table (masquer le tableau de thèmes)
            gr.update(visible=False),                          # details_title (masquer le titre des détails)
            gr.update(visible=False),                          # resume_table (masquer le tableau de résumé)
            gr.update(visible=False),                          # restart_btn (masquer le bouton rejouer)
            gr.update(visible=False),                          # recap_block (masquer le bloc de récapitulatif)
        ]
    else:
        # Si la réponse est incorrecte
        explication = current_q.get('long_answer', '')
        feedback_html = ""
        script_html = ""
        
        return [
            gr.update(visible=False),                          # start_btn (masquer le bouton démarrer)
            gr.update(),                                       # question (garder la question)
            gr.update(),                                       # progress_html (garder la barre de progression)
            gr.update(interactive=False,                       # choix (désactiver les options)
                        elem_classes=["quiz-radio","wrong"],   # Appliquer le style rouge
                        elem_id=f"choices-radio-{correct.replace(' ', '-').replace('é', 'e').replace('è', 'e').replace('à', 'a').replace('ç', 'c').replace('ô', 'o').replace('ù', 'u').replace('î', 'i').replace('ê', 'e')[:30]}"),   # ID unique pour le style
            gr.update(value=feedback_html, visible=False),     # feedback (masquer le feedback)
            gr.update(visible=True, value="Voir la correction"),  # explain_btn (afficher avec texte "correction")
            gr.update(value=f"<div class=\"correct-answer-box\"><span class=\"answer-label\">✅ Bonne réponse :</span><span class=\"answer-text\">{correct}</span></div><div class=\"explain-content\">{current_q.get('long_answer','')}</div>", visible=False),  # explain_md (préparer l'explication avec encadré vert)
            gr.update(value=script_html, visible=False),       # script_injector (masquer les scripts)
            gr.update(value=f"Score : {score:02d}"),     # score_display (mettre à jour le score)
            qs, index, score, finished, resume,                # states (états internes)
            gr.update(visible=True),                           # next_btn (afficher le bouton suivant)
            gr.update(visible=False),                          # score_final_display (masquer le score final)
            gr.update(visible=False),                          # encouragement_display (masquer l'encouragement)
            gr.update(visible=False),                          # bilan_theme_display (masquer le bilan par thème)
            gr.update(visible=False),                          # bilan_theme_table (masquer le tableau de thèmes)
            gr.update(visible=False),                          # details_title (masquer le titre des détails)
            gr.update(visible=False),                          # resume_table (masquer le tableau de résumé)
            gr.update(visible=False),                          # restart_btn (masquer le bouton rejouer)
            gr.update(visible=False),                          # recap_block (masquer le bloc de récapitulatif)
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