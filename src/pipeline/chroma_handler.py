import os, shutil
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

"""def save_to_chroma(chunks, model_name, db_path):
    if os.path.exists(db_path):
        shutil.rmtree(db_path)

    embedding_model = HuggingFaceEmbeddings(model_name=model_name)
    documents = [Document(page_content=chunk, metadata={"chunk_id": i}) for i, chunk in enumerate(chunks)]

    db = Chroma.from_documents(documents, embedding_model, persist_directory=db_path)
    return db
"""

def save_to_chroma(chunks, model_name, db_path):
    if os.path.exists(db_path):
        shutil.rmtree(db_path)

    embedding_model = HuggingFaceEmbeddings(model_name=model_name)

    documents = []
    for chunk in chunks:
        documents.append(
            Document(
                page_content=chunk["text"],
                metadata={
                    "chunk_id": chunk["chunk_id"],
                    "file_id": chunk["file_id"],
                    "file_name": chunk["file_name"],
                    "page": chunk["page"],
                    "theme": chunk.get("theme", "unknown"),
                    "merged_cluster": chunk.get("merged_cluster", None)
                }
            )
        )

    db = Chroma.from_documents(documents, embedding_model, persist_directory=db_path)
    return db
