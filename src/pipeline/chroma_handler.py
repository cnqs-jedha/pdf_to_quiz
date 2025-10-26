import os
import shutil
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

DEFAULT_CHROMA_DIR = "/tmp/chroma_db"
os.makedirs(DEFAULT_CHROMA_DIR, exist_ok=True)

def save_to_chroma(chunks, model_name, db_path=None):
    """
    Crée ou recrée une base Chroma à partir des chunks fournis.

    Args:
        chunks (list[dict]): Liste de chunks contenant 'text' et métadonnées.
        model_name (str): Nom du modèle Hugging Face pour les embeddings.
        db_path (str, optional): Chemin de persistance. Défaut: /tmp/chroma_db

    Returns:
        Chroma: Instance initialisée avec les documents vectorisés.
    """

    # ✅ Si aucun chemin n'est fourni, utiliser /tmp/chroma_db
    persist_dir = db_path or DEFAULT_CHROMA_DIR

    # ✅ S’assurer que le dossier existe
    os.makedirs(persist_dir, exist_ok=True)

    # ⚠️ Si le dossier existe déjà, on le réinitialise proprement
    # On ne supprime plus le dossier racine, seulement son contenu
    if os.path.exists(persist_dir):
        for item in os.listdir(persist_dir):
            item_path = os.path.join(persist_dir, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                print(f"⚠️ Impossible de supprimer {item_path}: {e}")
    else:
        os.makedirs(persist_dir, exist_ok=True)


    # ✅ Initialiser le modèle d’embeddings
    embedding_model = HuggingFaceEmbeddings(model_name=model_name)

    # ✅ Convertir les chunks en documents LangChain
    documents = [
        Document(
            page_content=chunk["text"],
            metadata={
                "chunk_id": chunk["chunk_id"],
                "file_id": chunk["file_id"],
                "file_name": chunk["file_name"],
                "page": chunk["page"],
                "theme": chunk.get("theme", "unknown"),
                "merged_cluster": chunk.get("merged_cluster", None),
            },
        )
        for chunk in chunks
    ]

    # ✅ Créer la base vectorielle persistante
    db = Chroma.from_documents(
        documents,
        embedding_model,
        persist_directory=persist_dir
    )

    return db