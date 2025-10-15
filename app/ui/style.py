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
    padding: .5rem;
    border-radius: 1rem;
    background-color: #FFFFFF;
    border: #px solid #DFDFDF;
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 1rem;
    align-items: center;
    text-decoration: none;
    transition: ease .3s;
}

.study-card:hover {
    transform: scale(1.05);
    box-shadow: 8px 8px 20px 0 rgba(91, 0, 171, .2);
}

.theme-tag {
    border-radius: 0.25rem;
    font-size: 0.75rem;
    padding: 2px 6px;
    background-color: rgb(240 227 252);
    margin-bottom: 3px;
    display: inline-block;
}

.pdf-icon-container{
    background-color: #fff2f2;
    padding: 1rem;
    border-radius: .75rem;
    height: 5rem;
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
"""