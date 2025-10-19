# =========================
# FICHIER DE STYLES CSS POUR L'INTERFACE QUIZ
# =========================
# Ce fichier contient tous les styles CSS personnalisés pour l'application Gradio
# Il définit l'apparence visuelle de tous les éléments de l'interface

custom_css = """
/* ============================================
   STYLES POUR LA PAGE DES STATISTIQUES
   ============================================ */

.stats-page {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
    background: #f8fafc;
    min-height: 100vh;
}

.stats-header {
    text-align: center;
    margin-bottom: 3rem;
    padding: 0;
    background: transparent;
    border-radius: 15px;
    box-shadow: none;
}

/*
.stats-header {
    text-align: center;
    margin-bottom: 3rem;
    padding: 2rem;
    background: white;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
*/

.stats-page-title {
    font-size: 2.5rem;
    color: #1e293b;
    margin: 0 0 1rem 0;
    font-weight: bold;
}

.stats-page-subtitle {
    font-size: 1.1rem;
    color: #64748b;
    margin: 0;
    font-weight: 500;
}



/* ============================================
   STYLES POUR L'HISTORIQUE (ANCIEN)
   ============================================ */

.history {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

.stats-container {
    margin: 2rem 0;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}

.stat-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    transition: transform 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
}

.stat-card h3 {
    font-size: 2.5rem;
    margin: 0 0 0.5rem 0;
    font-weight: bold;
}

.stat-card p {
    margin: 0;
    font-size: 1rem;
    opacity: 0.9;
}

.limit-info {
    font-size: 0.8rem;
    margin-top: 0.5rem;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-weight: 500;
}

.stat-card .limit-info {
    background: rgba(16, 185, 129, 0.1);
    color: #059669;
    border: 1px solid rgba(16, 185, 129, 0.2);
}

.stat-card:has(.limit-info:contains("⚠️")) .limit-info {
    background: rgba(245, 158, 11, 0.1);
    color: #d97706;
    border: 1px solid rgba(245, 158, 11, 0.2);
}

.chart-container {
    margin: 2rem 0;
    padding: 1.5rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    border: 1px solid #e2e8f0;
}

/* Amélioration du graphique matplotlib */
.chart-container .matplotlib {
    background: white !important;
    border-radius: 8px !important;
}

.chart-container svg {
    border-radius: 8px !important;
}

/* ============================================
   STYLES POUR LE TABLEAU DES SESSIONS
   ============================================ */

.sessions-table {
    margin: 2rem 0;
    padding: 1.5rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    border: 1px solid #e2e8f0;
    overflow: hidden;
}

.sessions-table .dataframe {
    border: none !important;
    border-radius: 12px !important;
    overflow: hidden;
}

.sessions-table .dataframe table {
    border-collapse: collapse;
    width: 100%;
    border: none !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.sessions-table .dataframe thead th {
    background: #f8fafc !important;
    color: #374151 !important;
    padding: 1rem 0.75rem !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    border: none !important;
    text-align: left !important;
    border-bottom: 2px solid #e2e8f0 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.sessions-table .dataframe tbody tr {
    transition: background-color 0.2s ease;
    border-bottom: 1px solid #f1f5f9 !important;
}

.sessions-table .dataframe tbody tr:hover {
    background: #f8fafc !important;
}

.sessions-table .dataframe tbody tr:nth-child(even) {
    background: #fafbfc !important;
}

.sessions-table .dataframe tbody td {
    padding: 0.875rem 0.75rem !important;
    border: none !important;
    text-align: left !important;
    font-size: 0.875rem !important;
    color: #374151 !important;
    vertical-align: middle;
}

.sessions-table .dataframe tbody tr:last-child {
    border-bottom: none !important;
}

/* ============================================
   STYLES POUR LES CARTES DE SESSIONS
   ============================================ */

.sessions-cards-container {
    margin: 2rem 0;
}

.sessions-title {
    font-size: 1.5rem;
    color: #1e293b;
    margin-bottom: 1.5rem;
    font-weight: 600;
}

.sessions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin: 1rem 0;
}

.session-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    border: 1px solid #e2e8f0;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.session-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    border-radius: 12px 12px 0 0;
}

.session-card.score-top::before {
    background: linear-gradient(90deg, #10b981, #059669);
}

.session-card.score-good::before {
    background: linear-gradient(90deg, #3b82f6, #2563eb);
}

.session-card.score-bof::before {
    background: linear-gradient(90deg, #f59e0b, #d97706);
}

.session-card.score-bad::before {
    background: linear-gradient(90deg, #ef4444, #dc2626);
}

.session-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.12);
}

.session-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.session-header h4 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: #1e293b;
}

.session-score {
    font-size: 1.2rem;
    font-weight: bold;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    color: white;
}

.session-card.score-top .session-score {
    background: #10b981;
}

.session-card.score-good .session-score {
    background: #3b82f6;
}

.session-card.score-bof .session-score {
    background: #f59e0b;
}

.session-card.score-bad .session-score {
    background: #ef4444;
}

.session-progress {
    margin-bottom: 1rem;
}

.progress-bar {
    width: 100%;
    height: 8px;
    background: #f1f5f9;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 0.5rem;
}

.progress-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s ease;
}

.session-card.score-top .progress-fill {
    background: linear-gradient(90deg, #10b981, #059669);
}

.session-card.score-good .progress-fill {
    background: linear-gradient(90deg, #3b82f6, #2563eb);
}

.session-card.score-bof .progress-fill {
    background: linear-gradient(90deg, #f59e0b, #d97706);
}

.session-card.score-bad .progress-fill {
    background: linear-gradient(90deg, #ef4444, #dc2626);
}

.progress-text {
    font-size: 0.875rem;
    font-weight: 600;
    color: #6b7280;
}

.session-themes {
    margin-top: 0.5rem;
}

.session-themes p {
    margin: 0;
    font-size: 0.875rem;
    color: #6b7280;
    line-height: 1.4;
}

/* ============================================
   STYLES GÉNÉRAUX DE L'APPLICATION
   ============================================ */

/* Style de base pour le corps de la page et le conteneur Gradio */
body, .gradio-container { 
    background-color: #f8fafc !important;  /* Couleur de fond gris très clair */
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;  /* Police moderne et lisible */
    max-width: 100% !important;
}

/* Style pour tous les blocs de contenu (questions, réponses, etc.) */
.block-container { 
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
.recap {
    background: #ffffff;
    border-radius: 1rem;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 .5rem 1.5rem rgba(0, 0, 0, 0.1);
    max-width: 1000px;
    margin: 0 auto;
}

/* Espacement optimisé entre les sections du récapitulatif */
.recap > * {
    margin-bottom: 1.5rem;
}

.recap > *:last-child {
    margin-bottom: 0;
}

/* Espacement spécifique pour les sections principales */
.score-final {
    margin-bottom: 2rem !important;
}

.encouragement {
    margin-bottom: 2rem !important;
}

.bilan-theme {
    margin-bottom: 2rem !important;
}

/* Supprimer les liserets de la section bilan-theme */
.bilan-theme::before {
    display: none;
}

.quiz-finish-title {
    margin-top: 0 !important;
    transform: translateY(-8px);
}

.score-jauge-container {
    position: relative; 
    width: 100px; 
    height: 100px; 
    display: flex;
    align-items: center; 
    justify-content: center;
    position: absolute;
    top: -1.5rem;
    background-color: white;
    padding: 12px;
    border-radius: 999px;
    box-shadow: 8px 8px 20px 0 rgba(0, 0, 0, .1);
    transform: rotate(-15deg);
    right: -1rem;
}

.score-jauge-container svg {
    width: 100px;
    height: 100px;
}

.jauge-circle.score-bad {
    stroke: #ED3B3C;
}
.jauge-percentage-text.score-bad {
    color: #ED3B3C;
}

.jauge-circle.score-bof {
    stroke: #FF7801;
}
.jauge-percentage-text.score-bof {
    color: #FF7801;
}

.jauge-circle.score-good {
    stroke: #FFB901;
}
.jauge-percentage-text.score-good {
    color: #FFB901;
}

.jauge-circle.score-top {
    stroke: #0FB076;
}
.jauge-percentage-text.score-top {
    color: #0FB076;
}

.jauge-percentage-text {
    position: absolute;
    font-size: 1.25rem;
    font-weight: 600;
    color: #111;
}

.score-card {
    background-color: #F9F9F9;
    padding: 1rem 1.5rem;
    border-radius: 1rem;
    display: flex;
    gap: 1rem;
    align-items: center;
    position: relative;
}

.score-card.score-top {
    background-color: #E2F5EE;
}
.score-card.score-good {
    background-color: #FFF5D9;
}
.score-card.score-bof {
    background-color: #FFEBD9;
}
.score-card.score-bad {
    background-color: #FDE7E7;
}

.score-text-container {
    width: 100%;
    text-align: center;
}

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


/* Study card */
.study-container {
    padding: 1.5rem;
    background-color: #F9F9F9;
    border-radius: 1rem;
}

.study-title {
    font-size: 1.5rem;
    text-align: center;
    color: #1e293b;
    font-weight: 700;
    margin-bottom: 1rem;
}

.study-intro {
    opacity: .7;
    text-align: center;
    max-width: 24rem;
    margin: 0 auto;
}

.study-card-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    justify-content: center;
    gap: 1rem;
    margin-top: 1.5rem;
}

.study-card {
    padding: 1rem;
    border-radius: 1rem;
    background-color: #FFFFFF;
    border: 1px solid #e2e8f0;
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 1rem;
    align-items: center;
    text-decoration: none;
    transition: all .2s ease;
    box-shadow: 0 4px 12px rgba(0,0,0,.06);
}

.study-card:hover {
    transform: scale(1.05);
    box-shadow: 8px 8px 20px 0 rgba(91, 0, 171, .2);
}

.theme-tag {
    border-radius: 0.5rem;
    font-size: 0.75rem;
    padding: 4px 8px;
    background-color: rgba(135, 4, 253, 0.1);
    color: #8704FD;
    font-weight: 600;
    margin-bottom: 6px;
    display: inline-block;
    border: 1px solid rgba(135, 4, 253, 0.2);
}

.pdf-icon-container{
    background-color: rgba(135, 4, 253, 0.05);
    padding: 1rem;
    border-radius: .75rem;
    height: 5rem;
    border: 1px solid rgba(135, 4, 253, 0.1);
}

.pdf-icon-svg {
    width: auto;
    height: 100%;
    margin: 0 auto .5rem;
}

.study-card-content p {
    margin: .5rem 0 0;
    margin-left: 0.25rem;
    font-size: 1.25rem;
    line-height: 1.4rem;
    font-weight: bold;
    word-break: break-word;
}

.pdf-pages {
    opacity: .7;
    font-style: italic;
    display: block;
    margin-left: 4px;
}

/* ============================================
   STYLES POUR LES TABLEAUX ET BILANS
   ============================================ */

/* Style pour le bloc de bilan par thème - même style que study-container */
.bilan-theme { 
    background: #F9F9F9 !important;  /* Même fond que study-container */
    border-radius: 1rem !important;  /* Coins arrondis */
    padding: 1.5rem !important;  /* Espacement interne */
    margin: 1rem 0 !important;  /* Espacement vertical */
}

.bilan-theme h3 {
    margin-top: 0 !important;
    margin-bottom: 1rem !important;
    color: #1e293b !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    text-align: center !important;
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
    background: #8704FD;  /* Dégradé bleu */
    border: none !important;  /* Pas de bordure */
    border-radius: 8px !important;  /* Coins arrondis */
    padding: 12px 24px !important;  /* Espacement interne */
    font-weight: 600 !important;  /* Texte semi-gras */
    transition: all 0.3s ease !important;  /* Animation fluide */
    color: white;
}

/* Effet de survol pour les boutons principaux */
.primary-btn:hover { 
    background-color: #590AA0;
}

.secondary-btn { 
    background: #F3E6FF;  /* Dégradé bleu */
    border: 1px solid #8704FD;  /* Pas de bordure */
    border-radius: 8px !important;  /* Coins arrondis */
    padding: 11px 23px !important;  /* Espacement interne */
    font-weight: 600 !important;  /* Texte semi-gras */
    transition: all 0.2s ease !important;  /* Animation fluide */
    color: #8704FD;
}

/* Effet de survol pour les boutons principaux */
.primary-btn:hover { 
    background-color: #590AA0;
    color: white;
}


/* ============================================
   STYLES POUR LA BARRE DE PROGRESSION
   ============================================ */
/* Conteneur de la barre de progression */
#quiz-progress {
    margin: 0 0 16px 0;  /* Espacement en bas */
}

.loader-questions {
    position: relative;
}

.loader-questions .current-score {
    position: absolute;
    top: .2rem;
    right: 0;
}

/* Barre de progression elle-même */
#quiz-progress .bar {
    height: .3rem;  /* Hauteur de la barre */
    border-radius: 999px;  /* Forme arrondie (pilule) */
    background: #F3E6FF;  /* Fond orange clair */
}

/* Partie remplie de la barre (animation) */
#quiz-progress .bar > span {
    display: block;  /* Affichage en bloc */
    height: 100%;  /* Hauteur complète */
    background: #8704FD;  /* Dégradé orange */
    width: 0;  /* Largeur initiale (sera animée) */
    border-radius: 999px;  /* Forme arrondie */
    transition: width 0.25s ease;  /* Animation fluide */
}

/* Label au centre de la barre */
#quiz-progress .label {
    margin-top: .2rem;
    color: #410578;
    font-size: .75rem;
    opacity: .7;
}

/* ============================================
   STYLES POUR LES BLOCS DE RÉPONSE
   ============================================ */


.quiz {
    background: #ffffff;
    border-radius: 1rem;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 .5rem 1.5rem rgba(0, 0, 0, 0.1);
    max-width: 1000px;
    margin: 0 auto;
}

.quiz h3 {
    font-size: 1.25rem;
    margin-top: 2rem;
}

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

.quiz .quiz-radio .wrap {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 1rem;
}

.quiz .quiz-radio .wrap label {
    padding: 16px 24px;
    min-height: 64px;
}

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

.answer-container {
    padding: 1rem;
    border-radius: 1rem;
    border: 1px solid #fff;
}

.answer-container.wrong {
    background-color: #FDE7E7;
    border-color: #ED3B3C;
}

.answer-container.correct {
    background-color: #E2F5EE;
    border-color: #0FB076;
}

.answer-intro-bravo{
    margin-top: 1.5rem !important;
    margin-bottom: 1rem;
    color: #0FB076;
}

.answer-intro-wrong{
    margin-top: 1.5rem !important;
    margin-bottom: 1rem;
    color: #ED3B3C;
}

.answer-container .answer-explication-title {
    font-weight: 700;
}

.answer-container .answer-long-text {
    opacity: .7;
}

.answer-correction {
    padding:1rem 1.25rem;
    background-color: #E2F5EE;
    border: 1px solid #0FB076;
    color: 0FB076;
    border-radius: 1rem;
    margin-bottom: .5rem !important;
    display: inline-block;
    width: auto !important;
}

/* ============================================
   STYLES POUR LA PAGE D'ACCUEIL
   ============================================ */

.home {
    background: #ffffff;
    border-radius: 1rem;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 .5rem 1.5rem rgba(0, 0, 0, 0.1);
    max-width: 1000px;
    margin: 0 auto;
}

.home .main-title .title {
    margin-bottom: .5rem;
}

.home .intro {
    opacity: .7;
    margin-top: 0;
    margin-bottom: 2rem !important;
}

.home .col-block {
    background-color: #F9F9F9;
    border-radius: 1rem;
    padding: 1.5rem;
    justify-content: space-between;
}

.home intro-right {
    opacity:.7;
}

.home .col-block .intro {
    margin-bottom: .5rem !important;
}

/*Loading page*/

/* ============================================
   STYLES POUR LA PAGE DE CHARGEMENT
   ============================================ */

.loading-page {
    border-radius: 1rem;
    padding: 1.5rem;
    margin: 1rem 0;
    margin: 0 auto;
    background: rgb(135, 4, 253);
    height: calc(100vh - 32px);
    align-items: center;
    justify-content: center;
}

.loader-component {
    display: flex;
    align-items: center;
    justify-content: center;
}

.loader {
  position: relative;
  width: 75px;
  height: 100px;
  margin:0 auto;
}

.loading-page #component-14 .svelte-au1olv {
    display: none !important;
    opacity: 0 !important;
}

.loading-page p {
    text-align: center;
    color: white;
    font-size: 1rem;
    opacity: .8;
}

.loader__bar {
  position: absolute;
  bottom: 0;
  width: 10px;
  height: 50%;
  background: #ffffff;
  transform-origin: center bottom;
  box-shadow: 1px 1px 0 rgba(0,0,0,.2);
}

/* On remplace la boucle SCSS @for par des règles manuelles */
.loader__bar:nth-child(1) {
  left: 0;
  transform: scale(1, 0.2);
  animation: barUp1 4s infinite;
}

.loader__bar:nth-child(2) {
  left: 15px;
  transform: scale(1, 0.4);
  animation: barUp2 4s infinite;
}

.loader__bar:nth-child(3) {
  left: 30px;
  transform: scale(1, 0.6);
  animation: barUp3 4s infinite;
}

.loader__bar:nth-child(4) {
  left: 45px;
  transform: scale(1, 0.8);
  animation: barUp4 4s infinite;
}

.loader__bar:nth-child(5) {
  left: 60px;
  transform: scale(1, 1);
  animation: barUp5 4s infinite;
}

.loader__ball {
  position: absolute;
  bottom: 10px;
  left: 0;
  width: 10px;
  height: 10px;
  background: #ffffff;
  border-radius: 50%;
  animation: ball 4s infinite;
}

/* Animations */

@keyframes ball {
  0%   { transform: translate(0, 0); }
  5%   { transform: translate(8px, -14px); }
  10%  { transform: translate(15px, -10px); }
  17%  { transform: translate(23px, -24px); }
  20%  { transform: translate(30px, -20px); }
  27%  { transform: translate(38px, -34px); }
  30%  { transform: translate(45px, -30px); }
  37%  { transform: translate(53px, -44px); }
  40%  { transform: translate(60px, -40px); }
  50%  { transform: translate(60px, 0); }
  57%  { transform: translate(53px, -14px); }
  60%  { transform: translate(45px, -10px); }
  67%  { transform: translate(37px, -24px); }
  70%  { transform: translate(30px, -20px); }
  77%  { transform: translate(22px, -34px); }
  80%  { transform: translate(15px, -30px); }
  87%  { transform: translate(7px, -44px); }
  90%  { transform: translate(0, -40px); }
  100% { transform: translate(0, 0); }
}

@keyframes barUp1 { 
  0%,40%   { transform: scale(1, .2); }
  50%,90%  { transform: scale(1, 1); }
  100%     { transform: scale(1, .2); }
}

@keyframes barUp2 { 
  0%,40%   { transform: scale(1, .4); }
  50%,90%  { transform: scale(1, .8); }
  100%     { transform: scale(1, .4); }
}

@keyframes barUp3 { 
  0%,100%  { transform: scale(1, .6); }
}

@keyframes barUp4 { 
  0%,40%   { transform: scale(1, .8); }
  50%,90%  { transform: scale(1, .4); }
  100%     { transform: scale(1, .8); }
}

@keyframes barUp5 { 
  0%,40%   { transform: scale(1, 1); }
  50%,90%  { transform: scale(1, .2); }
  100%     { transform: scale(1, 1); }
}

/* ==========20251510=======
   BILAN PAR THÈME — CARTES
   ========================= */
.bilan-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
  animation: fadeIn .6s ease;
}

.bilan-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 1rem;
  padding: 1.25rem 1.5rem;
  box-shadow: 0 6px 16px rgba(0,0,0,.1), 0 2px 4px rgba(0,0,0,.06);
  border: 1px solid #e2e8f0;
  border-left: 4px solid #e2e8f0;
  transition: all .2s ease;
  position: relative;
}
.bilan-card:hover { 
  transform: scale(1.05); 
  box-shadow: 8px 8px 20px 0 rgba(91, 0, 171, .2), 0 8px 24px rgba(0,0,0,.15);
}

.bilan-header {
  display: flex; 
  align-items: center; 
  justify-content: space-between;
  margin-bottom: .75rem;
}
.bilan-header h4 {
  font-size: 1.1rem; 
  margin: 0; 
  font-weight: 700; 
  color: #1e293b;
  line-height: 1.3;
}
.bilan-header span {
  font-size: 1rem; 
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 6px;
  background: rgba(135, 4, 253, 0.1);
  color: #8704FD;
}

.bilan-progress {
  background: #f1f5f9;
  height: 6px;
  border-radius: 999px;
  overflow: hidden;
  margin: .5rem 0 .75rem 0;
  position: relative;
}
.bilan-progress .bar { 
  height: 100%; 
  width: 0; 
  transition: width .6s ease;
  border-radius: 999px;
}

/* Couleur de la barre selon niveau */
.bilan-card.score-bad  .bar { background: linear-gradient(90deg, #ef4444, #dc2626); }
.bilan-card.score-bof  .bar { background: linear-gradient(90deg, #f59e0b, #d97706); }
.bilan-card.score-good .bar { background: linear-gradient(90deg, #3b82f6, #2563eb); }
.bilan-card.score-top  .bar { background: linear-gradient(90deg, #10b981, #059669); }

/* Couleur de la bordure gauche selon niveau */
.bilan-card.score-bad { border-left-color: #ef4444; }
.bilan-card.score-bof { border-left-color: #f59e0b; }
.bilan-card.score-good { border-left-color: #3b82f6; }
.bilan-card.score-top { border-left-color: #10b981; }

.bilan-card p {
  margin: 0; 
  color: #64748b; 
  font-size: .9rem;
  font-weight: 500;
  line-height: 1.4;
}

/* Résumé global au-dessus des cartes */
.resume-summary {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: .75rem;
  padding: 1rem 1.25rem;
  margin: .5rem 0 1rem;
  animation: fadeIn .6s ease;
}
.resume-summary h4 { margin: 0 0 .25rem 0; }

/* Détails — tableau : zébrage et meilleure lisibilité */
.dataframe table { width: 100%; border-collapse: collapse; }
.dataframe tr:nth-child(even) { background-color: #f9fafb !important; }
.dataframe th, .dataframe td { font-size: .95rem !important; }
.dataframe td:last-child { text-align: center !important; font-weight: 700; } /* colonne "Résultat" */

/* Apparitions douces */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Animation d'apparition progressive pour les sections */
.recap > * {
  animation: fadeInUp 0.6s ease forwards;
  opacity: 0;
  transform: translateY(20px);
}

.recap > *:nth-child(1) { animation-delay: 0.1s; }
.recap > *:nth-child(2) { animation-delay: 0.2s; }
.recap > *:nth-child(3) { animation-delay: 0.3s; }
.recap > *:nth-child(4) { animation-delay: 0.4s; }

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .dataframe { font-size: .85rem; }
}

/* Détails (table HTML) */
.details-table-wrap { margin-top: .5rem; animation: fadeIn .5s ease; }
.details-table-wrap table.details {
  width: 100%; border-collapse: collapse; background: #fff; border-radius: .75rem;
  overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,.04);
}
.details-table-wrap th, .details-table-wrap td {
  padding: .75rem .85rem; border-bottom: 1px solid #f1f5f9; vertical-align: top; text-align: left;
}
.details-table-wrap thead th { background: #f8fafc; font-weight: 700; color: #1f2937; }
.details-table-wrap tbody tr:nth-child(even) { background: #fafafa; }

.badge {
  display: inline-block; padding: 2px 8px; border-radius: 999px; font-weight: 700; font-size: .85rem;
}
.badge.ok { background: #E2F5EE; color: #0FB076; }
.badge.ko { background: #FDE7E7; color: #ED3B3C; }

/* === Unifier l'aspect "grand panneau" : Sessions = Bilan === */

/* Panneau pour la section Sessions */
.stats-page .sessions-cards-container {
  background: #f8fafc !important;      /* même fond que le bilan */
  border: 1px solid #e2e8f0 !important; /* fine bordure grise */
  border-radius: 16px !important;       /* coins arrondis */
  box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important; /* ombre douce */
  padding: 1.5rem 2rem !important;      /* respiration interne */
  margin: 0 0 1.5rem 0 !important;      /* écart sous le panneau */
}

/* Titre au centre, même hiérarchie visuelle que le bilan */
.stats-page .sessions-cards-container .sessions-title {
  text-align: center !important;
  margin: 0 0 1.5rem 0 !important;
  font-weight: 700 !important;
  font-size: 1.5rem !important;
}

/* La grille de cartes ne doit pas recréer d'espaces parasites */
.stats-page .sessions-cards-container .sessions-grid {
  margin: 0 !important;
}

/* (Si on avait neutralisé les wrappers Gradio avant, on s'assure qu'ils 
   ne réintroduisent pas de cadres intermédiaires dans la section) */
.stats-page .sessions-cards-container .gr-box,
.stats-page .sessions-cards-container .gr-group,
.stats-page .sessions-cards-container .gr-panel,
.stats-page .sessions-cards-container .block-container {
  background: transparent !important;
  box-shadow: none !important;
  border: 0 !important;
  padding: 0 !important;
  margin: 0 !important;
}


"""