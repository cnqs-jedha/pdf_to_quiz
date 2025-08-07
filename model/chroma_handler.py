import os, shutil
from langchain_chroma import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

def save_to_chroma(chunks, model_name, db_path):
    if os.path.exists(db_path):
        shutil.rmtree(db_path)

    embedding_model = HuggingFaceEmbeddings(model_name=model_name)
    documents = [Document(page_content=chunk, metadata={"chunk_id": i}) for i, chunk in enumerate(chunks)]

    db = Chroma.from_documents(documents, embedding_model, persist_directory=db_path)
    return db
