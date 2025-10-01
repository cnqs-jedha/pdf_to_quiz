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
    border: 1px solid rgba(226, 232, 240, 0.8) !important;
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
"""