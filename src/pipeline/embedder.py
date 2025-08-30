from sentence_transformers import SentenceTransformer

def get_embeddings(chunks, model_name):
    model = SentenceTransformer(model_name)
    return model.encode(chunks)