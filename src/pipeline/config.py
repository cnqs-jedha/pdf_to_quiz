SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
DRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/1P_v9V_eVLRps3nxCO4Fn-ui0-WdY-mmz?usp=sharing"
FOLDER_MIME   = "application/vnd.google-apps.folder"
SHORTCUT_MIME = "application/vnd.google-apps.shortcut"
#CHROMA_DB_PATH = "chroma_db"
CHROMA_DB_PATH = "/tmp/chroma_db"

#EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2" # entraîné sur des textes en anglais 
# EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2" # multilingue
EMBEDDING_MODEL_NAME = "dangvantuan/sentence-camembert-base" # adapté au français
#EMBEDDING_MODEL_NAME = "OrdalieTech/Solon-embeddings-large-0.1" # adapté au français
POST_TARGET_URL = "https://cnsq-quiz-api.hf.space/send_quiz" #If local -> replace api by localhost else replace localhost by api