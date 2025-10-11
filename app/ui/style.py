# =========================
# UI (Gradio)
# =========================

custom_css = """
body, .gradio-container { 
    background-color: #f8fafc !important; 
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
}
.block { 
    background: #ffffff !important; 
    border-radius: 16px !important; 
    padding: 24px !important; 
    margin: 16px 0 !important;
    box-shadow: 0 8px 25px rgba(15, 23, 42, 0.08) !important; 
}
.markdown h1 {
    color: #1e293b !important;
    text-align: center !important;
    margin-bottom: 20px !important;
    font-weight: 700 !important;
}
.markdown h3 { 
    margin: 16px 0 12px 0 !important; 
    color: #334155 !important;
    font-weight: 600 !important;
}
.markdown p { line-height: 1.6 !important; color: #475569 !important; }
.score-excellent{background:linear-gradient(135deg,#059669 0%,#047857 100%)!important;color:#fff!important;padding:24px!important;border-radius:16px!important;text-align:center!important;margin:16px 0!important;font-size:1.5rem!important;font-weight:700!important;box-shadow:0 8px 32px rgba(5,150,105,.3)!important}
.score-tres-bien{background:linear-gradient(135deg,#3b82f6 0%,#1d4ed8 100%)!important;color:#fff!important;padding:24px!important;border-radius:16px!important;text-align:center!important;margin:16px 0!important;font-size:1.5rem!important;font-weight:700!important;box-shadow:0 8px 32px rgba(59,130,246,.3)!important}
.score-pas-mal{background:linear-gradient(135deg,#f59e0b 0%,#d97706 100%)!important;color:#fff!important;padding:24px!important;border-radius:16px!important;text-align:center!important;margin:16px 0!important;font-size:1.5rem!important;font-weight:700!important;box-shadow:0 8px 32px rgba(245,158,11,.3)!important}
.score-a-ameliorer{background:linear-gradient(135deg,#ef4444 0%,#dc2626 100%)!important;color:#fff!important;padding:24px!important;border-radius:16px!important;text-align:center!important;margin:16px 0!important;font-size:1.5rem!important;font-weight:700!important;box-shadow:0 8px 32px rgba(239,68,68,.3)!important}
.score-final h3 { margin: 0 0 12px 0 !important; font-size: 1.8rem !important; }
.score-final p { margin: 8px 0 0 0 !important; font-size: 1.2rem !important; opacity: .95 !important; }
.bilan-theme { background:#fefefe!important;border:1px solid #e2e8f0!important;border-radius:8px!important;padding:20px!important;margin:16px 0!important; }
.dataframe { border-radius: 8px!important; overflow: hidden!important; border: 1px solid #e2e8f0!important; }
.dataframe th { background-color:#f8fafc!important; color:#374151!important; font-weight:600!important; padding:12px 8px!important; border-bottom:2px solid #e5e7eb!important; }
.dataframe td { padding:10px 8px!important; border-bottom:1px solid #f3f4f6!important; vertical-align:top!important; }
.primary-btn { background:linear-gradient(135deg,#3b82f6 0%,#2563eb 100%)!important; border:none!important; border-radius:8px!important; padding:12px 24px!important; font-weight:600!important; transition:all .2s ease!important; }
.primary-btn:hover { transform: translateY(-1px)!important; box-shadow:0 6px 20px rgba(59,130,246,.3)!important; }
/* Barre de progression du quiz */
#quiz-progress {margin:0 0 16px 0}
#quiz-progress .bar{height:32px;border-radius:999px;background:#fef3e2;overflow:hidden;position:relative}
#quiz-progress .bar>span{display:block;height:100%;background:linear-gradient(135deg,#f97316,#ea580c);width:0;border-radius:999px;transition:width .25s ease}
#quiz-progress .label{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-weight:700;color:#1f2937;font-size:1.1rem}
/* Bloc réponse/explication (correct/incorrect) */
.answer-block{border:2px solid transparent!important;border-radius:12px!important;padding:16px!important;margin-top:12px!important}
.answer-block .answer-title{font-weight:700!important;margin-bottom:8px!important}
.answer-block .answer-expl{opacity:.95!important;line-height:1.6!important}
.answer-block.correct{background:rgba(16,185,129,.12)!important;border-color:#10b981!important}
.answer-block.correct .answer-title{color:#047857!important}
.answer-block.wrong{background:rgba(239,68,68,.12)!important;border-color:#ef4444!important}
.answer-block.wrong .answer-title{color:#b91c1c!important}
/* Mise en forme des options Radio sélectionnées */
.quiz-radio.correct label.selected,
.quiz-radio.correct label:has(input:checked){background:rgba(16,185,129,.12)!important;border:2px solid #10b981!important;color:#065f46!important}
.quiz-radio.wrong label.selected,
.quiz-radio.wrong label:has(input:checked){background:rgba(239,68,68,.12)!important;border:2px solid #ef4444!important;color:#7f1d1d!important}
/* Remplacer le point orange par ✅ ou ❌ selon la réponse */
.quiz-radio.correct label:has(input:checked) input[type="radio"] {
    display: none !important;
}
.quiz-radio.correct label:has(input:checked)::before {
    content: "✅" !important;
    font-size: 16px !important;
    margin-right: 8px !important;
    display: inline-block !important;
}
.quiz-radio.wrong label:has(input:checked) input[type="radio"] {
    display: none !important;
}
.quiz-radio.wrong label:has(input:checked)::before {
    content: "❌" !important;
    font-size: 16px !important;
    margin-right: 8px !important;
    display: inline-block !important;
}
/* Bouton d'explication et bloc d'aide */
.explain-teaser{background:#f8fafc!important;border:2px solid #e2e8f0!important;border-radius:12px!important;padding:16px!important;margin:12px 0!important;text-align:center!important}
.explain-btn-rect{background:linear-gradient(135deg,#3b82f6,#2563eb)!important;border:none!important;border-radius:10px!important;padding:10px 16px!important;font-weight:600!important;color:#fff!important;margin:0 auto!important;display:block!important}
.explain-btn-rect:hover{transform:translateY(-1px)!important;box-shadow:0 6px 16px rgba(59,130,246,.3)!important}
/* Explication longue (sur demande) */
.explain-content{background:rgba(59,130,246,.08)!important;border:2px solid #3b82f6!important;border-radius:12px!important;padding:16px!important;margin:12px 0!important}

/* Encadré vert pour la bonne réponse */
.correct-answer-box{background:rgba(16,185,129,.12)!important;border:2px solid #10b981!important;border-radius:12px!important;padding:16px!important;margin:12px auto!important;font-weight:600!important;color:#047857!important;text-align:center!important;max-width:600px!important;display:flex!important;align-items:center!important;justify-content:center!important;gap:8px!important}
.correct-answer-box .answer-label{font-size:0.9rem!important;text-transform:uppercase!important;letter-spacing:0.5px!important;margin:0!important;opacity:0.8!important}
.correct-answer-box .answer-text{font-size:1.1rem!important;line-height:1.4!important;margin:0!important}
"""