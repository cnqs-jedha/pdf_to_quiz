SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
DRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/1P_v9V_eVLRps3nxCO4Fn-ui0-WdY-mmz?usp=sharing"
FOLDER_MIME   = "application/vnd.google-apps.folder"
SHORTCUT_MIME = "application/vnd.google-apps.shortcut"
# DRIVE_FILE_ID = [
#     "1AHE1lXi_kyrtRw31qEGJ7OYE9EO8kfGe",
#     "1lad6YB8RPnyPWZ1n2Swl-uQNAAurlpe7",
#     "1ljbKdP54lXIMhZdj5jDez_beidnc3scM",
#     "1mP6psfnvQSs5eCP04F8Kl-zDI3tNQfvi",
#     "1XTEndg-nbdU0E59QZD9ZwkHBU9FGXnBV"
# ]
# PDF_PATH = [
#     "/data/Histoire_CM1.pdf",
#     "/data/Histoire_toutes_les_leçons_CM1_A4.pdf",
#     "/data/RA16_C3_HIGE_CM1_Th1_avant_la_france_vu_JC_619867.pdf",
#     "/data/RA16_C3_HIGE_CM1_Th2_temps_des_rois_619869.pdf",
#     "/data/RA16_C3_HIGE_CM1_Th3_temps_Revolution_et_Empire_619871.pdf"
# ]
CHROMA_DB_PATH = "chroma_db"
#EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2" # entraîné sur des textes en anglais 
EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2" # multilingue
#EMBEDDING_MODEL_NAME = "dangvantuan/sentence-camembert-base" # adapté au français
#EMBEDDING_MODEL_NAME = "OrdalieTech/Solon-embeddings-large-0.1" # adapté au français
POST_TARGET_URL = "http://api:8000/send_quiz" #If local -> replace api by localhost else replace localhost by api