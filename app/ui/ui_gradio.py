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
import matplotlib.pyplot as plt
import io  # Pour la gestion des flux de données
import base64  # Pour l'encodage des images

# Imports des modules personnalisés
from core.helpers import build_resume_tables  # Pour construire les tableaux de résultats
from core.config import API_BASE_URL, API_QUESTIONS_PATH, USE_API, REQUIRE_API, BASE_DIR, json_path  # Configuration
from core.helpers import load_questions  # Pour charger les questions depuis l'API
from core.check import check_ready_api  # Pour vérifier si l'API est prête

# =========================
# Utilitaires d'affichage HTML
# =========================

def format_pages_text(pages_str: str) -> str:
    """
    Formate le texte des pages avec l'accord correct du mot 'page'.
    
    Args:
        pages_str (str): Chaîne contenant les numéros de pages (ex: "1, 2, 4")
    
    Returns:
        str: Texte formaté avec accord correct (ex: "page 1" ou "pages 1, 2, 4")
    """
    if not pages_str or pages_str.strip() == "":
        return "page 1"
    
    # Nettoyer la chaîne et extraire les numéros de pages
    pages_clean = pages_str.strip()
    pages_list = [p.strip() for p in pages_clean.split(',') if p.strip()]
    
    # Compter le nombre de pages
    num_pages = len(pages_list)
    
    if num_pages == 1:
        return f"page {pages_clean}"
    else:
        return f"pages {pages_clean}"

def render_details_table(detailed_df: pd.DataFrame) -> str:
    """
    Rend la table “Détails des réponses” en HTML.
    Détermination robuste du booléen de correction:
      - Priorité à la colonne 'Correct' (bool, str 'True'/'Vrai' etc.)
      - Sinon lit 'Résultat' (✅ / ❌)
      - Sinon compare 'Ta réponse' vs 'Bonne réponse'
    """
    if detailed_df is None or detailed_df.empty:
        return "<div class='resume-summary'><p>Aucun détail à afficher.</p></div>"

    def is_trueish(x):
        if isinstance(x, bool): 
            return x
        if x is None:
            return False
        s = str(x).strip().lower()
        return s in ("true", "vrai", "1", "oui", "ok", "✔", "✅")
    
    rows = []
    for _, r in detailed_df.iterrows():
        # 1) essaie 'Correct'
        ok = None
        if "Correct" in r:
            val = r["Correct"]
            try:
                if pd.isna(val):  # type: ignore
                    ok = None
                else:
                    ok = is_trueish(val)
            except Exception:
                ok = is_trueish(val)

        # 2) sinon 'Résultat'
        if ok is None and "Résultat" in r:
            res = str(r["Résultat"]).strip()
            if res in ("✅", "✔", "True", "Vrai"):
                ok = True
            elif res in ("❌", "✘", "False", "Faux"):
                ok = False

        # 3) sinon comparaison stricte des textes
        if ok is None:
            ok = str(r.get("Ta réponse", "")).strip() == str(r.get("Bonne réponse", "")).strip()

        badge = "<span class='badge ok'>✔</span>" if ok else "<span class='badge ko'>✘</span>"
        rows.append(f"""
            <tr>
                <td>{r.get('Thème','')}</td>
                <td>{r.get('Question','')}</td>
                <td>{r.get('Ta réponse','')}</td>
                <td>{r.get('Bonne réponse','')}</td>
                <td style="text-align:center">{badge}</td>
            </tr>
        """)

    return f"""
    <div class="details-table-wrap">
      <table class="details">
        <thead>
          <tr>
            <th>Thème</th><th>Question</th><th>Ta réponse</th><th>Bonne réponse</th><th>Résultat</th>
          </tr>
        </thead>
        <tbody>
          {''.join(rows)}
        </tbody>
      </table>
    </div>
    """

# Icône PDF (SVG) pour les cartes de révision
PDF_SVG = """
<svg class="pdf-icon-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 75.320129 92.604164">
  <g transform="translate(53.548057 -183.975276) scale(1.4843)">
    <path fill="#ff2116" d="M-29.632812 123.94727c-3.551967 0-6.44336 2.89347-6.44336 6.44531v49.49804c0 3.55185 2.891393 6.44532 6.44336 6.44532H8.2167969c3.5519661 0 6.4433591-2.89335 6.4433591-6.44532v-40.70117s.101353-1.19181-.416015-2.35156c-.484969-1.08711-1.275391-1.84375-1.275391-1.84375a1.0584391 1.0584391 0 0 0-.0059-.008l-9.3906254-9.21094a1.0584391 1.0584391 0 0 0-.015625-.0156s-.8017392-.76344-1.9902344-1.27344c-1.39939552-.6005-2.8417968-.53711-2.8417968-.53711l.021484-.002z"/>
    <path fill="#f5f5f5" d="M-29.632812 126.06445h28.3789058a1.0584391 1.0584391 0 0 0 .021484 0s1.13480448.011 1.96484378.36719c.79889772.34282 1.36536982.86176 1.36914062.86524.0000125.00001.00391.004.00391.004l9.3671868 9.18945s.564354.59582.837891 1.20899c.220779.49491.234375 1.40039.234375 1.40039a1.0584391 1.0584391 0 0 0-.002.0449v40.74609c0 2.41592-1.910258 4.32813-4.3261717 4.32813H-29.632812c-2.415914 0-4.326172-1.91209-4.326172-4.32813v-49.49804c0-2.41603 1.910258-4.32813 4.326172-4.32813z"/>
    <path fill="#ff2116" d="M-23.40766 161.09299c-1.45669-1.45669.11934-3.45839 4.39648-5.58397l2.69124-1.33743 1.04845-2.29399c.57665-1.26169 1.43729-3.32036 1.91254-4.5748l.8641-2.28082-.59546-1.68793c-.73217-2.07547-.99326-5.19438-.52872-6.31588.62923-1.51909 2.69029-1.36323 3.50626.26515.63727 1.27176.57212 3.57488-.18329 6.47946l-.6193 2.38125.5455.92604c.30003.50932 1.1764 1.71867 1.9475 2.68743l1.44924 1.80272 1.8033728-.23533c5.72900399-.74758 7.6912472.523 7.6912472 2.34476 0 2.29921-4.4984914 2.48899-8.2760865-.16423-.8499666-.59698-1.4336605-1.19001-1.4336605-1.19001s-2.3665326.48178-3.531704.79583c-1.202707.32417-1.80274.52719-3.564509 1.12186 0 0-.61814.89767-1.02094 1.55026-1.49858 2.4279-3.24833 4.43998-4.49793 5.1723-1.3991.81993-2.86584.87582-3.60433.13733zm2.28605-.81668c.81883-.50607 2.47616-2.46625 3.62341-4.28553l.46449-.73658-2.11497 1.06339c-3.26655 1.64239-4.76093 3.19033-3.98386 4.12664.43653.52598.95874.48237 2.01093-.16792zm21.21809-5.95578c.80089-.56097.68463-1.69142-.22082-2.1472-.70466-.35471-1.2726074-.42759-3.1031574-.40057-1.1249.0767-2.9337647.3034-3.2403347.37237 0 0 .993716.68678 1.434896.93922.58731.33544 2.0145161.95811 3.0565161 1.27706 1.02785.31461 1.6224.28144 2.0729-.0409zm-8.53152-3.54594c-.4847-.50952-1.30889-1.57296-1.83152-2.3632-.68353-.89643-1.02629-1.52887-1.02629-1.52887s-.4996 1.60694-.90948 2.57394l-1.27876 3.16076-.37075.71695s1.971043-.64627 2.97389-.90822c1.0621668-.27744 3.21787-.70134 3.21787-.70134zm-2.74938-11.02573c.12363-1.0375.1761-2.07346-.15724-2.59587-.9246-1.01077-2.04057-.16787-1.85154 2.23517.0636.8084.26443 2.19033.53292 3.04209l.48817 1.54863.34358-1.16638c.18897-.64151.47882-2.02015.64411-3.06364z"/>
    <path fill="#2c2c2c" d="M-20.930423 167.83862h2.364986q1.133514 0 1.840213.2169.706698.20991 1.189489.9446.482795.72769.482795 1.75625 0 .94459-.391832 1.6233-.391833.67871-1.056548.97958-.65772.30087-2.02913.30087h-.818651v3.72941h-1.581322zm1.581322 1.22447v3.33058h.783664q1.049552 0 1.44838-.39184.405826-.39183.405826-1.27345 0-.65772-.265887-1.06355-.265884-.41282-.587747-.50378-.314866-.098-1.000572-.098zm5.50664-1.22447h2.148082q1.560333 0 2.4909318.55276.9375993.55276 1.4133973 1.6443.482791 1.09153.482791 2.42096 0 1.3994-.4338151 2.49793-.4268149 1.09153-1.3154348 1.76324-.8816233.67172-2.5189212.67172h-2.267031zm1.581326 1.26645v7.018h.657715q1.378411 0 2.001144-.9516.6227329-.95858.6227329-2.5539 0-3.5125-2.6238769-3.5125zm6.4722254-1.26645h5.30372941v1.26645H-4.2075842v2.85478h2.9807225v1.26646h-2.9807225v4.16322h-1.5813254z"/>
  </g>
</svg>
""".strip()

# ============================================
# FONCTION PRINCIPALE : DÉMARRAGE DU QUIZ
# ============================================

def start_quiz():
    """
    Démarre un nouveau quiz en chargeant les questions depuis l'API.
    
    Cette fonction :
    1. Charge les questions depuis l'API ou le fichier local
    2. Sélectionne aléatoirement 10 questions maximum avec système de poids
    3. Initialise l'interface avec la première question
    4. Retourne tous les éléments de l'interface mis à jour
    
    Returns:
        list: Liste des mises à jour pour tous les éléments de l'interface
    """
    print("⏳ Chargement des questions depuis l'API...", flush=True)
    
    # Essayer d'abord de récupérer les questions pondérées
    try:
        response = requests.get(f"{API_BASE_URL}/weighted_questions?max_questions=10", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("questions"):
                niveau = data["questions"]
                print(f"📋 {len(niveau)} questions pondérées récupérées", flush=True)
            else:
                # Fallback vers l'ancien système
                niveau = load_questions(API_BASE_URL, API_QUESTIONS_PATH, USE_API, REQUIRE_API, json_path)
                print(f"📋 {len(niveau)} questions récupérées (mode fallback)", flush=True)
        else:
            # Fallback vers l'ancien système
            niveau = load_questions(API_BASE_URL, API_QUESTIONS_PATH, USE_API, REQUIRE_API, json_path)
            print(f"📋 {len(niveau)} questions récupérées (mode fallback)", flush=True)
    except Exception as e:
        print(f"⚠️ Erreur lors du chargement des questions pondérées: {e}", flush=True)
        # Fallback vers l'ancien système
        niveau = load_questions(API_BASE_URL, API_QUESTIONS_PATH, USE_API, REQUIRE_API, json_path)
        print(f"📋 {len(niveau)} questions récupérées (mode fallback)", flush=True)

    # Vérifier qu'il y a des questions disponibles
    if not niveau:
        return [
            gr.update(visible=True),   # afficher page erreur
            gr.update(visible=False),  # masquer loader
            gr.update(visible=False),  # masquer quiz
            "❌ Aucun quiz trouvé. Veuillez relancer la génération."
        ]

    # Dédupliquer les questions basées sur le texte de la question et les options
    seen_questions = set()
    unique_questions = []
    duplicates_count = 0
    
    for question in niveau:
        # Adapter à la nouvelle structure des questions
        if "question" in question and isinstance(question["question"], dict):
            # Nouvelle structure : question.llm_response.text
            text_value = question["question"].get("llm_response", {}).get("text", "")
            question_text = str(text_value).strip().lower() if text_value else ""
            options_dict = question["question"].get("llm_response", {}).get("choices", {})
            options = list(options_dict.values()) if options_dict else []
        else:
            # Ancienne structure : question.question
            text_value = question.get("question", "")
            question_text = str(text_value).strip().lower() if text_value else ""
            options = question.get("options", [])
        
        # Créer une signature unique basée sur la question et les options triées
        options_signature = "|".join(sorted([opt.strip().lower() for opt in options if opt.strip()]))
        question_signature = f"{question_text}|{options_signature}"
        
        if question_text and question_signature not in seen_questions:
            seen_questions.add(question_signature)
            unique_questions.append(question)
        else:
            duplicates_count += 1
    
    # Informer sur les doublons détectés
    if duplicates_count > 0:
        print(f"🔄 {duplicates_count} questions en doublon détectées et supprimées", flush=True)
    
    # Sélectionner aléatoirement 10 questions maximum parmi les questions uniques
    # Si moins de 10 questions disponibles, prendre toutes les questions disponibles
    max_questions = min(10, len(unique_questions))
    if max_questions < 10:
        print(f"⚠️ Seulement {max_questions} questions disponibles (moins que les 10 souhaitées)")
    
    qs = random.sample(unique_questions, max_questions)
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
        gr.update(visible=False),  # details_html (masquer le tableau des détails)
        gr.update(visible=False),  # resume_table (masquer le tableau de résumé)
        gr.update(visible=False),  # restart_btn (masquer le bouton rejouer)
        gr.update(visible=False),  # view_stats_btn (masquer le bouton statistiques)
        gr.update(visible=False),  # recap_block (masquer le bloc de récapitulatif)
    ]

def start_quiz_from_home():
    """Démarre le quiz depuis la page d'accueil (cache home, montre quiz)."""
    quiz_updates = start_quiz()

    return [gr.update(visible=False),  # home masqué
            gr.update(visible=False),  # loader masqué
            gr.update(visible=True)] + quiz_updates

def start_quiz_from_history():
    """Démarre le quiz depuis l'historique (cache history, montre quiz)."""
    quiz_updates = start_quiz()

    return [gr.update(visible=False),  # home masqué
            gr.update(visible=False),  # loader masqué
            gr.update(visible=True),   # quiz visible
            gr.update(visible=False)] + quiz_updates  # history masqué

def start_quiz_from_stats():
    """Démarre le quiz depuis la page des statistiques (cache stats, montre quiz)."""
    quiz_updates = start_quiz()

    return [gr.update(visible=False),  # home masqué
            gr.update(visible=False),  # loader masqué
            gr.update(visible=True),   # quiz visible
            gr.update(visible=False)] + quiz_updates  # stats_page masqué



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
    
    # Adapter à la nouvelle structure des questions
    if "question" in q and isinstance(q["question"], dict):
        # Nouvelle structure : question.llm_response.text
        question_text = q["question"].get("llm_response", {}).get("text", "")
        question_md = f"### {question_text}"
        # Extraire les options de la nouvelle structure
        choices_dict = q["question"].get("llm_response", {}).get("choices", {})
        options = list(choices_dict.values()) if choices_dict else []
    else:
        # Ancienne structure : question.question
        question_text = q.get("question", "")
        question_md = f"### {question_text}"
        options = q.get("options", [])
    
    # Créer la barre de progression
    progress_percentage = ((index+1)/total)*100
    progress_html = f"""
    <div class="bar"><span style="width:{progress_percentage:.0f}%"></span>
    <div class="label">Question {index+1:02d}/{total:02d}</div></div>
    """.strip()
    
    # Créer le texte du score
    score_txt = f"Score : {score:02d}"
    
    # Retourner les mises à jour pour tous les éléments
    return [
        gr.update(value=question_md, visible=True),           # question (afficher la question)
        gr.update(value=progress_html, visible=True),           # progress (afficher l'indicateur de progression)
        gr.update(choices=options, value=None, interactive=True, visible=True, elem_classes=["quiz-radio"], elem_id="choices-radio"),  # choix (options de réponse)
        gr.update(value=q.get("long_answer", ""), visible=False), # explain_md (masquer l'explication)
        gr.update(value="", visible=False),                     # script_injector (masquer les scripts)
        gr.update(value=score_txt, visible=True),               # score_display (afficher le score)
        qs, index, score, finished, resume                      # states (états internes)
    ]

def update_final_screen(qs, score, resume):
    """Écran final : jauge + fiche de révision + bilan (cartes) + détails (HTML)."""
    finished = True
    total_questions = len(qs)
    pourcentage = (score / total_questions) * 100 if total_questions else 0
    
    # Sauvegarder la session complète
    try:
        from datetime import datetime
        import uuid
        
        session_id = str(uuid.uuid4())
        themes_covered = list(set([r.get("Thème", "Sans thème") for r in resume]))
        
        session_data = {
            "session_id": session_id,
            "start_time": datetime.now().isoformat(),  # On pourrait améliorer cela
            "end_time": datetime.now().isoformat(),
            "total_questions": total_questions,
            "correct_answers": score,
            "score_percentage": pourcentage,
            "themes_covered": themes_covered
        }
        
        # Envoyer la session à l'API
        requests.post(f"{API_BASE_URL}/save_quiz_session", json=session_data, timeout=5)
        print(f"💾 Session sauvegardée: {session_id} - Score: {score}/{total_questions} ({pourcentage:.1f}%)")
    except Exception as e:
        print(f"⚠️ Erreur lors de la sauvegarde de la session: {e}")

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
                <circle 
                    cx="50" 
                    cy="50" 
                    r="45" 
                    stroke="#e6e6e6" 
                    stroke-width="10" 
                    fill="none" 
                />
                
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
    """.strip()

    # --- Bilan et détails à partir du résumé ---
    per_theme, detailed = build_resume_tables(resume)

    # Cartes Thèmes
    bilan_cards_html = ""
    if not per_theme.empty:
        best_idx = per_theme["% Réussite"].idxmax()
        worst_idx = per_theme["% Réussite"].idxmin()
        theme_best = per_theme.loc[best_idx, "Thème"]
        theme_worst = per_theme.loc[worst_idx, "Thème"]

        cards = []
        for _, row in per_theme.iterrows():
            acc = int(row["% Réussite"])
            color_class = (
                "score-top" if acc >= 90 else
                "score-good" if acc >= 75 else
                "score-bof" if acc >= 50 else
                "score-bad"
            )
            cards.append(f"""
                <div class="bilan-card {color_class}">
                    <div class="bilan-header">
                        <h4>{row['Thème']}</h4>
                        <span>{acc}%</span>
                    </div>
                    <div class="bilan-progress">
                        <div class="bar" style="width:{acc}%"></div>
                    </div>
                    <p>{int(row['Bonnes réponses'])} bonnes réponses sur {int(row['Questions'])}</p>
                </div>
            """)

        bilan_cards_html = f"<div class='bilan-grid'>{''.join(cards)}</div>"

    # Fiche de révision (cartes PDF)     
    bilan_theme = ""
    themes_a_reviser = ""
    bilan_table = pd.DataFrame()
    if not per_theme.empty:
        bilan_theme = ("<h3 class='study-title'>Bilan par thème</h3>" + bilan_cards_html).strip()
        bilan_table = per_theme.copy()
        # Identifier les thèmes à retravailler (ceux avec le plus faible % de réussite)
        min_acc = per_theme["% Réussite"].min()
        themes_a_travailler = per_theme.loc[per_theme["% Réussite"] == min_acc, "Thème"].tolist()

        if len(themes_a_travailler) > 0:
            # Construire la liste détaillée avec fichiers et pages
            themes_details = []
            for theme in themes_a_travailler:
                # Trouver les questions de ce thème dans le quiz
                theme_questions = [q for q in qs if q.get("question", {}).get("metadata", {}).get("theme") == theme]
                if theme_questions:
                    # Grouper par fichier et pages
                    file_pages = {}
                    for q in theme_questions:
                        metadata = q.get("question", {}).get("metadata", {})
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
                            pages_text = format_pages_text(pages_clean)
                            file_html += f"""
                                <a href="{drive_link}" target="_blank" class="study-card">
                                    <div class="pdf-icon-container">
                                    {PDF_SVG}
                                    </div>
                                    <div class="study-card-content">
                                        <span class="theme-tag">{theme_name}</span>
                                        <p>{file_name.strip('• ').strip()}</p>
                                        <span class="pdf-pages">{pages_text}</span>
                                    </div>
                                </a>
                            """

                    cards_html += file_html

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
    details_html_value = render_details_table(detailed_copy)

    return [
        gr.update(value="<h3 class=\"quiz-finish-title\"> 🎯 Quiz terminé !</h3>", visible=True),   # question (titre final)
        gr.update(visible=False),                                  # progress_bar
        gr.update(visible=False),                                  # choix
        gr.update(visible=False),                                  # explain_md
        gr.update(visible=False),                                  # script_injector
        gr.update(visible=False),                                  # score_display
        qs, len(qs), score, finished, resume,                     # states (5)
        gr.update(visible=False),                                  # next_btn
        gr.update(value=score_et_encouragement, visible=True),     # score_final_display
        gr.update(value=themes_a_reviser, visible=bool(themes_a_reviser)),  # encouragement_display (révisions)
        gr.update(value=bilan_theme, visible=not per_theme.empty),  # bilan_theme_display
        gr.update(value=bilan_table, visible=False),                # bilan_theme_table
        gr.update(value="**📋 Détails des réponses (trié par thème)**", visible=True),  # details_title
        gr.update(value=details_html_value, visible=True),         # details_html
        gr.update(value=detailed_copy, visible=False),              # resume_table
        gr.update(visible=True),                                   # restart_btn
        gr.update(visible=True),                                   # view_stats_btn
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
    3. Sauvegarde la réponse dans l'historique
    4. Affiche le bouton d'explication avec le bon texte
    5. Applique les styles visuels appropriés (vert pour correct, rouge pour incorrect)
    
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
        return [gr.update() for _ in range(23)]  # 23 éléments avec view_stats_btn

    current_q = qs[index]
    
    # Adapter à la nouvelle structure des questions
    if "question" in current_q and isinstance(current_q["question"], dict):
        # Nouvelle structure : question.llm_response
        llm_response = current_q["question"].get("llm_response", {})
        correct = llm_response.get("correct_answer", {}).get("answer") or current_q.get("réponse")
        metadata = current_q["question"].get("metadata", {})
        question_text = llm_response.get("text", "")
        long_answer = llm_response.get("correct_answer_long", "")
    else:
        # Ancienne structure
        correct = current_q.get("llm_response", {}).get("correct_answer", {}).get("answer") or current_q.get("réponse")
        metadata = current_q.get("metadata", {})
        question_text = current_q.get("llm_response", {}).get("text", "")
        long_answer = current_q.get("long_answer", "")

    is_correct = reponse == correct
    resultat = "✅" if is_correct else "❌"

    # Sauvegarder la réponse dans l'historique
    try:
        from datetime import datetime
        question_id = f"{metadata.get('theme', 'unknown')}_{question_text[:50]}"
        
        answer_data = {
            "question_id": question_id,
            "user_answer": reponse,
            "correct_answer": correct,
            "is_correct": is_correct,
            "theme": metadata.get("theme", "Sans thème"),
            "timestamp": datetime.now().isoformat(),
            "quiz_session_id": "current_session"  # On peut améliorer cela plus tard
        }
        
        # Envoyer la réponse à l'API
        requests.post(f"{API_BASE_URL}/save_answer", json=answer_data, timeout=5)
        print(f"💾 Réponse sauvegardée: {question_id[:30]}... - {'✅' if is_correct else '❌'}")
    except Exception as e:
        print(f"⚠️ Erreur lors de la sauvegarde de la réponse: {e}")

    resume.append({
        "Thème": metadata.get("theme", "Sans thème"),
        "Question": question_text,
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
            <div class="answer-long-text">{long_answer}</div>
        </div>
        """
        choix_style = ["quiz-radio", "correct"]
    else:
        explain_html = f"""
        <div class="wrong-title-container">
            <h3 class="answer-intro-wrong">❌ Mauvaise réponse, la bonne réponse était :</h3>
            <div class="answer-correction">✅ <i>"{correct}"</i></div>
        </div>
        <div class="answer-container wrong">
            <p class="answer-explication-title">Explication :</p>
            <div class="answer-long-text">{long_answer}</div>
        </div>
        """
        choix_style = ["quiz-radio", "wrong"]

    # Retourner les mises à jour
    return [
        gr.update(visible=False),          # start_btn
        gr.update(),                       # question
        gr.update(),                       # progress bar
        gr.update(interactive=False, elem_classes=choix_style),  # désactiver radio
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
        gr.update(visible=False),          # details_html
        gr.update(visible=False),          # resume_table
        gr.update(visible=False),          # restart_btn
        gr.update(visible=False),          # view_stats_btn
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
            gr.update(visible=False),  # details_html
            gr.update(visible=False),  # resume_table
            gr.update(visible=False),  # restart_btn
            gr.update(visible=False),  # view_stats_btn
            gr.update(visible=False),  # recap_block
        ])
        return result

def restart_quiz():
    """Relance complètement un quiz."""
    return start_quiz()

def show_user_history():
    """
    Affiche l'historique des performances de l'utilisateur.
    """
    print("🔍 Début de show_user_history", flush=True)
    try:
        # Récupérer l'historique depuis l'API
        print(f"📡 Appel API: {API_BASE_URL}/user_history", flush=True)
        response = requests.get(f"{API_BASE_URL}/user_history", timeout=10)
        print(f"📡 Réponse API: {response.status_code}", flush=True)
        if response.status_code == 200:
            history_data = response.json()
            print(f"📊 Données reçues: {len(history_data.get('quiz_sessions', []))} sessions", flush=True)
            
            # Calculer les statistiques
            total_sessions = len(history_data.get("quiz_sessions", []))
            total_questions = sum(session.get("total_questions", 0) for session in history_data.get("quiz_sessions", []))
            total_correct = sum(session.get("correct_answers", 0) for session in history_data.get("quiz_sessions", []))
            overall_percentage = (total_correct / total_questions * 100) if total_questions > 0 else 0
            
            # Statistiques générales avec indicateur de limite
            max_sessions = 5
            sessions_indicator = f"({total_sessions}/{max_sessions})" if total_sessions >= max_sessions else f"({total_sessions}/{max_sessions})"
            
            stats_html = f"""
            <div class="stats-grid">
                <div class="stat-card">
                    <div>
                        <h3>{total_sessions}</h3>
                        <p>Quiz réalisés</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div>
                        <h3>{total_questions}</h3>
                        <p>Questions répondues</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div>
                        <h3>{total_correct}</h3>
                        <p>Bonnes réponses</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div>
                        <h3>{overall_percentage:.1f}%</h3>
                        <p>Taux de réussite</p>
                    </div>
                </div>
            </div>
            """
            #{sessions_indicator}
            # <small class="limit-info">{"⚠️ Limite atteinte" if total_sessions >= max_sessions else "✅ Dans la limite"}</small>
            
            # Créer des cartes pour les sessions précédentes
            sessions_cards_html = ""
            sessions_data = []
            for session in history_data.get("quiz_sessions", []):
                date = session.get("end_time", "Inconnue")[:10]
                score = session.get("correct_answers", 0)
                total = session.get("total_questions", 0)
                percentage = session.get("score_percentage", 0)
                themes = session.get("themes_covered", [])
                
                # Déterminer la classe de couleur basée sur le pourcentage
                if percentage >= 90:
                    card_class = "score-top"
                elif percentage >= 75:
                    card_class = "score-good"
                elif percentage >= 50:
                    card_class = "score-bof"
                else:
                    card_class = "score-bad"
                
                # Créer la carte HTML (même style que bilan-card)
                sessions_cards_html += f"""
                <div class="bilan-card {card_class}">
                    <div class="bilan-header">
                        <h4>{date}</h4>
                        <span>{score}/{total}</span>
                    </div>
                    <div class="bilan-progress">
                        <div class="bar" style="width: {percentage}%"></div>
                    </div>
                    <p>{percentage:.1f}% • {', '.join(themes[:3])}{'...' if len(themes) > 3 else ''}</p>
                </div>
                """
                
                # Garder aussi les données pour le tableau (au cas où)
                sessions_data.append([
                    date,  # Date
                    f"{score}/{total}",  # Score
                    total,  # Questions
                    ", ".join(themes),  # Thèmes
                    f"{percentage:.1f}%"  # Progression
                ])
            
            # Créer un graphique simple des performances par thème
            theme_performance = history_data.get("theme_performance", {})
            if theme_performance:
                
                # Filtrer les thèmes de test et les thèmes vides
                filtered_themes = {}
                for theme, perf in theme_performance.items():
                    # Exclure les thèmes de test et les thèmes vides
                    if (theme and 
                        not theme.startswith("test_") and 
                        theme != "Sans thème" and 
                        theme.strip() != "" and
                        not theme.startswith("test_theme")):
                        filtered_themes[theme] = perf
                
                if not filtered_themes:
                    # Aucun thème valide trouvé
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.text(0.5, 0.5, 'Aucune donnée de performance par thème disponible.', 
                           ha='center', va='center', transform=ax.transAxes)
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
                    ax.axis('off')
                    chart_figure = fig
                else:
                    themes = list(filtered_themes.keys())
                    success_rates = []
                    
                    for theme in themes:
                        perf = filtered_themes[theme]
                        total = perf.get("correct", 0) + perf.get("incorrect", 0)
                        if total > 0:
                            success_rates.append(perf.get("correct", 0) / total * 100)
                        else:
                            success_rates.append(0)
                    
                    # Créer un graphique moderne avec style professionnel
                    plt.style.use('seaborn-v0_8-whitegrid')
                    fig, ax = plt.subplots(figsize=(14, 8))
                    
                    # Fond et style moderne
                    fig.patch.set_facecolor('#ffffff')
                    ax.set_facecolor('#fafbfc')
                    
                    # Couleurs dégradées modernes
                    colors = []
                    for rate in success_rates:
                        if rate >= 90:
                            colors.append('#10b981')  # Vert émeraude
                        elif rate >= 75:
                            colors.append('#3b82f6')  # Bleu moderne
                        elif rate >= 50:
                            colors.append('#f59e0b')  # Orange ambré
                        else:
                            colors.append('#ef4444')  # Rouge moderne
                    
                    # Créer les barres avec effets
                    bars = ax.bar(themes, success_rates, color=colors, 
                                 edgecolor='#ffffff', linewidth=2, 
                                 alpha=0.9)
                    
                    # Style du titre et des axes
                    ax.set_title('Performances par thème', 
                               fontsize=18, fontweight='bold', 
                               color='#1e293b', pad=25)
                    ax.set_xlabel('Thèmes', fontsize=14, color='#374151', fontweight='500')
                    ax.set_ylabel('Taux de réussite (%)', fontsize=14, color='#374151', fontweight='500')
                    
                    # Style des axes
                    ax.tick_params(axis='x', rotation=45, colors='#6b7280', labelsize=11)
                    ax.tick_params(axis='y', colors='#6b7280', labelsize=11)
                    ax.set_ylim(0, 105)
                    
                    # Grille subtile
                    ax.grid(True, alpha=0.2, color='#e5e7eb', linestyle='-', linewidth=0.5)
                    ax.set_axisbelow(True)
                    
                    # Ajouter les valeurs sur les barres avec style
                    for bar, rate in zip(bars, success_rates):
                        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                                f'{rate:.1f}%', ha='center', va='bottom',
                                fontweight='bold', fontsize=10, color='#374151')
                    
                    # Ajouter une ligne de référence à 80%
                    ax.axhline(y=80, color='#d1d5db', linestyle='--', alpha=0.7, linewidth=1)
                    ax.text(len(themes)-0.5, 82, 'Objectif 80%', fontsize=10, 
                           color='#6b7280', ha='right', va='bottom')
                    
                    # Ajuster l'espacement
                    plt.tight_layout()
                    chart_figure = fig
            else:
                # Créer un graphique vide
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.text(0.5, 0.5, 'Aucune donnee de performance par theme disponible.', 
                    ha='center', va='center', transform=ax.transAxes)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
                chart_figure = fig
            
            # Créer le HTML pour les cartes de sessions (avec même structure que bilan-theme)
            sessions_html = f"""
            
                <h3 class="study-title">Sessions précédentes</h3>
                <div class="bilan-grid">
                    {sessions_cards_html}
                </div>
            
            """
            
            return [
                gr.update(visible=False),  # home masqué
                gr.update(visible=False),  # loader masqué
                gr.update(visible=False),  # quiz masqué
                gr.update(visible=True),   # stats_page visible
                gr.update(value=stats_html, visible=True),  # stats_display
                gr.update(value=chart_figure, visible=True),  # theme_performance_chart
                gr.update(value=sessions_html, visible=True),  # sessions_table (maintenant HTML)
                gr.update(visible=True),   # back_to_home_btn
                gr.update(visible=True),   # new_quiz_from_stats_btn
                gr.update(visible=False),  # recap_block masqué (résultat du quiz)
            ]
        else:
            return [
                gr.update(visible=False),  # home masqué
                gr.update(visible=False),  # loader masqué
                gr.update(visible=False),  # quiz masqué
                gr.update(visible=True),   # stats_page visible
                gr.update(value="<p>Erreur lors du chargement de l'historique.</p>", visible=True),
                gr.update(visible=False),  # theme_performance_chart
                gr.update(visible=False),  # sessions_table
                gr.update(visible=True),   # back_to_home_btn
                gr.update(visible=True),   # new_quiz_from_stats_btn
                gr.update(visible=False),  # recap_block masqué (résultat du quiz)
            ]
    except Exception as e:
        print(f"⚠️ Erreur lors du chargement de l'historique: {e}")
        return [
            gr.update(visible=False),  # home masqué
            gr.update(visible=False),  # loader masqué
            gr.update(visible=False),  # quiz masqué
            gr.update(visible=True),   # stats_page visible
            gr.update(value=f"<p>Erreur: {str(e)}</p>", visible=True),
            gr.update(visible=False),  # theme_performance_chart
            gr.update(visible=False),  # sessions_table
            gr.update(visible=True),   # back_to_home_btn
            gr.update(visible=True),   # new_quiz_from_stats_btn
            gr.update(visible=False),  # recap_block masqué (résultat du quiz)
        ]

def send_drive_link_to_api(drive_link: str):
    """
    Envoie le lien Google Drive à l'API, affiche un loader, puis montre le quiz quand prêt.
    Fonction génératrice (yield) pour mises à jour progressives.
    """

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
        resp = requests.post(
            f"{API_BASE_URL}/run_pipeline",
            json={"drive_link": drive_link},
            timeout=15
        )

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
        yield [
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
            f"❌ Erreur de connexion à l’API : {e}"
        ]
        return

    # 3️⃣ Passage à la page de chargement
    yield [
        gr.update(visible=False),  # home masqué
        gr.update(visible=True),   # page_loader affichée
        gr.update(visible=False),  # page_quiz masquée
        "Pipeline lancée, génération du quiz en cours..."
    ]

    # 4️⃣ Boucle d’attente non bloquante, 20 min max (240 * 5s)
    for i in range(240):
        time.sleep(5)
        quiz_ready, quiz_data = check_ready_api()
        message = quiz_data.get("message", "Traitement en cours...")

        yield [
        gr.update(visible=False),  # home masqué
        gr.update(visible=True),   # page_loader affichée
        gr.update(visible=False),  # page_quiz masquée
            f"{message}"
        ]

        if quiz_ready:
            time.sleep(2)
            yield [
                gr.update(visible=False),  # home masqué
                gr.update(visible=False),  # cacher loader
                gr.update(visible=True),   # afficher quiz
                "✅ Quiz prêt !"
            ]
            return

    # 5️⃣ Timeout après les boucles
    yield [
        gr.update(visible=True),   # home visible
        gr.update(visible=False), # loader masqué
        gr.update(visible=False), # quiz masqué
        "❌ Temps d'attente dépassé. Le quiz n'a pas pu être généré."
    ]