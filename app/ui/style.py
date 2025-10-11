# =========================
# FICHIER DE STYLES CSS POUR L'INTERFACE QUIZ
# =========================
# Ce fichier contient tous les styles CSS personnalisés pour l'application Gradio
# Il définit l'apparence visuelle de tous les éléments de l'interface

custom_css = """
/* ============================================
   STYLES GÉNÉRAUX DE L'APPLICATION
   ============================================ */

/* Style de base pour le corps de la page et le conteneur Gradio */
body, .gradio-container { 
    background-color: #f8fafc !important;  /* Couleur de fond gris très clair */
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;  /* Police moderne et lisible */
}

/* Style pour tous les blocs de contenu (questions, réponses, etc.) */
.block { 
    background: #ffffff !important;  /* Fond blanc pour les blocs */
    border-radius: 16px !important;  /* Coins arrondis pour un look moderne */
    padding: 24px !important;  /* Espacement interne */
    margin: 16px 0 !important;  /* Espacement entre les blocs */
    box-shadow: 0 8px 25px rgba(15, 23, 42, 0.08) !important;  /* Ombre légère pour la profondeur */
}

/* ============================================
   STYLES POUR LES TITRES ET TEXTE
   ============================================ */

/* Style pour les titres principaux (h1) */
.markdown h1 {
    color: #1e293b !important;  /* Couleur bleu-gris foncé */
    text-align: center !important;  /* Centré */
    margin-bottom: 20px !important;  /* Espacement en bas */
    font-weight: 700 !important;  /* Texte en gras */
}

/* Style pour les sous-titres (h3) */
.markdown h3 { 
    margin: 16px 0 12px 0 !important;  /* Espacement vertical */
    color: #334155 !important;  /* Couleur gris-bleu */
    font-weight: 600 !important;  /* Texte semi-gras */
}

/* Style pour les paragraphes */
.markdown p { 
    line-height: 1.6 !important;  /* Hauteur de ligne pour la lisibilité */
    color: #475569 !important;  /* Couleur gris moyen */
}
/* ============================================
   STYLES POUR LES SCORES FINAUX
   ============================================ */

/* Score excellent (100%) - Vert */
.score-excellent {
    background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;  /* Dégradé vert */
    color: #fff !important;  /* Texte blanc */
    padding: 24px !important;  /* Espacement interne */
    border-radius: 16px !important;  /* Coins arrondis */
    text-align: center !important;  /* Centré */
    margin: 16px 0 !important;  /* Espacement vertical */
    font-size: 1.5rem !important;  /* Taille de police */
    font-weight: 700 !important;  /* Texte en gras */
    box-shadow: 0 8px 32px rgba(5, 150, 105, 0.3) !important;  /* Ombre verte */
}

/* Score très bien (80-99%) - Bleu */
.score-tres-bien {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;  /* Dégradé bleu */
    color: #fff !important;
    padding: 24px !important;
    border-radius: 16px !important;
    text-align: center !important;
    margin: 16px 0 !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3) !important;  /* Ombre bleue */
}

/* Score pas mal (60-79%) - Orange */
.score-pas-mal {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;  /* Dégradé orange */
    color: #fff !important;
    padding: 24px !important;
    border-radius: 16px !important;
    text-align: center !important;
    margin: 16px 0 !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    box-shadow: 0 8px 32px rgba(245, 158, 11, 0.3) !important;  /* Ombre orange */
}

/* Score à améliorer (<60%) - Rouge */
.score-a-ameliorer {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;  /* Dégradé rouge */
    color: #fff !important;
    padding: 24px !important;
    border-radius: 16px !important;
    text-align: center !important;
    margin: 16px 0 !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    box-shadow: 0 8px 32px rgba(239, 68, 68, 0.3) !important;  /* Ombre rouge */
}

/* Styles pour les éléments du score final */
.score-final h3 { 
    margin: 0 0 12px 0 !important; 
    font-size: 1.8rem !important;  /* Titre plus grand */
}

.score-final p { 
    margin: 8px 0 0 0 !important; 
    font-size: 1.2rem !important; 
    opacity: 0.95 !important;  /* Légèrement transparent */
}

/* ============================================
   STYLES POUR LES TABLEAUX ET BILANS
   ============================================ */

/* Style pour le bloc de bilan par thème */
.bilan-theme { 
    background: #fefefe !important;  /* Fond blanc cassé */
    border: 1px solid #e2e8f0 !important;  /* Bordure grise */
    border-radius: 8px !important;  /* Coins arrondis */
    padding: 20px !important;  /* Espacement interne */
    margin: 16px 0 !important;  /* Espacement vertical */
}

/* Style pour les tableaux de données */
.dataframe { 
    border-radius: 8px !important;  /* Coins arrondis */
    overflow: hidden !important;  /* Masque le débordement */
    border: 1px solid #e2e8f0 !important;  /* Bordure grise */
}

/* Style pour les en-têtes de tableau */
.dataframe th { 
    background-color: #f8fafc !important;  /* Fond gris clair */
    color: #374151 !important;  /* Texte gris foncé */
    font-weight: 600 !important;  /* Texte semi-gras */
    padding: 12px 8px !important;  /* Espacement interne */
    border-bottom: 2px solid #e5e7eb !important;  /* Bordure inférieure */
}

/* Style pour les cellules de tableau */
.dataframe td { 
    padding: 10px 8px !important;  /* Espacement interne */
    border-bottom: 1px solid #f3f4f6 !important;  /* Bordure inférieure légère */
    vertical-align: top !important;  /* Alignement en haut */
}

/* ============================================
   STYLES POUR LES BOUTONS
   ============================================ */

/* Style pour les boutons principaux (démarrer, rejouer) */
.primary-btn { 
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;  /* Dégradé bleu */
    border: none !important;  /* Pas de bordure */
    border-radius: 8px !important;  /* Coins arrondis */
    padding: 12px 24px !important;  /* Espacement interne */
    font-weight: 600 !important;  /* Texte semi-gras */
    transition: all 0.2s ease !important;  /* Animation fluide */
}

/* Effet de survol pour les boutons principaux */
.primary-btn:hover { 
    transform: translateY(-1px) !important;  /* Légère élévation */
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3) !important;  /* Ombre bleue */
}
/* ============================================
   STYLES POUR LA BARRE DE PROGRESSION
   ============================================ */

/* Conteneur de la barre de progression */
#quiz-progress {
    margin: 0 0 16px 0;  /* Espacement en bas */
}

/* Barre de progression elle-même */
#quiz-progress .bar {
    height: 32px;  /* Hauteur de la barre */
    border-radius: 999px;  /* Forme arrondie (pilule) */
    background: #fef3e2;  /* Fond orange clair */
    overflow: hidden;  /* Masque le débordement */
    position: relative;  /* Position relative pour le label */
}

/* Partie remplie de la barre (animation) */
#quiz-progress .bar > span {
    display: block;  /* Affichage en bloc */
    height: 100%;  /* Hauteur complète */
    background: linear-gradient(135deg, #f97316, #ea580c);  /* Dégradé orange */
    width: 0;  /* Largeur initiale (sera animée) */
    border-radius: 999px;  /* Forme arrondie */
    transition: width 0.25s ease;  /* Animation fluide */
}

/* Label au centre de la barre */
#quiz-progress .label {
    position: absolute;  /* Position absolue */
    top: 50%;  /* Centré verticalement */
    left: 50%;  /* Centré horizontalement */
    transform: translate(-50%, -50%);  /* Centrage parfait */
    font-weight: 700;  /* Texte en gras */
    color: #1f2937;  /* Couleur gris foncé */
    font-size: 1.1rem;  /* Taille de police */
}

/* ============================================
   STYLES POUR LES BLOCS DE RÉPONSE
   ============================================ */

/* Style de base pour les blocs de réponse */
.answer-block {
    border: 2px solid transparent !important;  /* Bordure transparente par défaut */
    border-radius: 12px !important;  /* Coins arrondis */
    padding: 16px !important;  /* Espacement interne */
    margin-top: 12px !important;  /* Espacement en haut */
}

/* Titre dans le bloc de réponse */
.answer-block .answer-title {
    font-weight: 700 !important;  /* Texte en gras */
    margin-bottom: 8px !important;  /* Espacement en bas */
}

/* Explication dans le bloc de réponse */
.answer-block .answer-expl {
    opacity: 0.95 !important;  /* Légèrement transparent */
    line-height: 1.6 !important;  /* Hauteur de ligne pour la lisibilité */
}

/* Bloc de réponse correcte (vert) */
.answer-block.correct {
    background: rgba(16, 185, 129, 0.12) !important;  /* Fond vert clair */
    border-color: #10b981 !important;  /* Bordure verte */
}

.answer-block.correct .answer-title {
    color: #047857 !important;  /* Texte vert foncé */
}

/* Bloc de réponse incorrecte (rouge) */
.answer-block.wrong {
    background: rgba(239, 68, 68, 0.12) !important;  /* Fond rouge clair */
    border-color: #ef4444 !important;  /* Bordure rouge */
}

.answer-block.wrong .answer-title {
    color: #b91c1c !important;  /* Texte rouge foncé */
}

/* ============================================
   STYLES POUR LES OPTIONS DE RÉPONSE (RADIO)
   ============================================ */

/* Options radio sélectionnées - Réponse correcte */
.quiz-radio.correct label.selected,
.quiz-radio.correct label:has(input:checked) {
    background: rgba(16, 185, 129, 0.12) !important;  /* Fond vert clair */
    border: 2px solid #10b981 !important;  /* Bordure verte */
    color: #065f46 !important;  /* Texte vert foncé */
}

/* Options radio sélectionnées - Réponse incorrecte */
.quiz-radio.wrong label.selected,
.quiz-radio.wrong label:has(input:checked) {
    background: rgba(239, 68, 68, 0.12) !important;  /* Fond rouge clair */
    border: 2px solid #ef4444 !important;  /* Bordure rouge */
    color: #7f1d1d !important;  /* Texte rouge foncé */
}

/* Remplacer le point radio par ✅ pour les bonnes réponses */
.quiz-radio.correct label:has(input:checked) input[type="radio"] {
    display: none !important;  /* Masquer le point radio */
}

.quiz-radio.correct label:has(input:checked)::before {
    content: "✅" !important;  /* Afficher un checkmark */
    font-size: 16px !important;  /* Taille de l'icône */
    margin-right: 8px !important;  /* Espacement à droite */
    display: inline-block !important;  /* Affichage en ligne */
}

/* Remplacer le point radio par ❌ pour les mauvaises réponses */
.quiz-radio.wrong label:has(input:checked) input[type="radio"] {
    display: none !important;  /* Masquer le point radio */
}

.quiz-radio.wrong label:has(input:checked)::before {
    content: "❌" !important;  /* Afficher une croix */
    font-size: 16px !important;  /* Taille de l'icône */
    margin-right: 8px !important;  /* Espacement à droite */
    display: inline-block !important;  /* Affichage en ligne */
}

/* ============================================
   STYLES POUR LES BOUTONS D'EXPLICATION
   ============================================ */

/* Bloc d'aide pour l'explication */
.explain-teaser {
    background: #f8fafc !important;  /* Fond gris très clair */
    border: 2px solid #e2e8f0 !important;  /* Bordure grise */
    border-radius: 12px !important;  /* Coins arrondis */
    padding: 16px !important;  /* Espacement interne */
    margin: 12px 0 !important;  /* Espacement vertical */
    text-align: center !important;  /* Centré */
}

/* Bouton d'explication */
.explain-btn-rect {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;  /* Dégradé bleu */
    border: none !important;  /* Pas de bordure */
    border-radius: 10px !important;  /* Coins arrondis */
    padding: 10px 16px !important;  /* Espacement interne */
    font-weight: 600 !important;  /* Texte semi-gras */
    color: #fff !important;  /* Texte blanc */
    margin: 0 auto !important;  /* Centré horizontalement */
    display: block !important;  /* Affichage en bloc */
}

/* Effet de survol pour le bouton d'explication */
.explain-btn-rect:hover {
    transform: translateY(-1px) !important;  /* Légère élévation */
    box-shadow: 0 6px 16px rgba(59, 130, 246, 0.3) !important;  /* Ombre bleue */
}

/* ============================================
   STYLES POUR LES EXPLICATIONS ET CORRECTIONS
   ============================================ */

/* Contenu de l'explication longue */
.explain-content {
    background: rgba(59, 130, 246, 0.08) !important;  /* Fond bleu très clair */
    border: 2px solid #3b82f6 !important;  /* Bordure bleue */
    border-radius: 12px !important;  /* Coins arrondis */
    padding: 16px !important;  /* Espacement interne */
    margin: 12px 0 !important;  /* Espacement vertical */
}

/* Encadré vert pour afficher la bonne réponse */
.correct-answer-box {
    background: rgba(16, 185, 129, 0.12) !important;  /* Fond vert clair */
    border: 2px solid #10b981 !important;  /* Bordure verte */
    border-radius: 12px !important;  /* Coins arrondis */
    padding: 16px !important;  /* Espacement interne */
    margin: 12px auto !important;  /* Centré horizontalement avec espacement */
    font-weight: 600 !important;  /* Texte semi-gras */
    color: #047857 !important;  /* Couleur verte foncée */
    text-align: center !important;  /* Centré */
    max-width: 600px !important;  /* Largeur maximale */
    display: flex !important;  /* Affichage en flexbox */
    align-items: center !important;  /* Centré verticalement */
    justify-content: center !important;  /* Centré horizontalement */
    gap: 8px !important;  /* Espacement entre les éléments */
}

/* Label dans l'encadré de la bonne réponse */
.correct-answer-box .answer-label {
    font-size: 0.9rem !important;  /* Taille de police plus petite */
    text-transform: uppercase !important;  /* Texte en majuscules */
    letter-spacing: 0.5px !important;  /* Espacement entre les lettres */
    margin: 0 !important;  /* Pas de marge */
    opacity: 0.8 !important;  /* Légèrement transparent */
}

/* Texte de la bonne réponse */
.correct-answer-box .answer-text {
    font-size: 1.1rem !important;  /* Taille de police légèrement plus grande */
    line-height: 1.4 !important;  /* Hauteur de ligne */
    margin: 0 !important;  /* Pas de marge */
}
"""