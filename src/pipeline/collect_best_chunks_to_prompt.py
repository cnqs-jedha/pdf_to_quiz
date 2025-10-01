import random
"""def find_best_chunk_to_prompt(vector_db, themes, k=5, fetch_k=50, lambda_mult=0.5):
    full_chunks_themes = []
    strings_chunks_themes = []

    for query in themes:
    
        retriever = vector_db.as_retriever(
            search_type="mmr",
            search_kwargs={"k": k, "fetch_k": fetch_k, "lambda_mult": lambda_mult}
        )

        relevant_docs = retriever.invoke(query)
        full_chunks_themes.append(relevant_docs)
        
        
    for i, chunk in enumerate(full_chunks_themes):
        string = " ".join(doc.page_content for doc in chunk)

        strings_chunks_themes.append(string)

    return strings_chunks_themes"""

def find_best_chunk_to_prompt(vector_db, themes, k=10, fetch_k=50, lambda_mult=0.5, chunks_len=3):
    full_chunks_themes = []
    results_by_theme = {}

    for query in themes:
    
        retriever = vector_db.as_retriever(
            search_type="mmr",
            search_kwargs={"k": k, "fetch_k": fetch_k, "lambda_mult": lambda_mult}
        )

        relevant_docs = retriever.invoke(query)
        #print(f"[DEBUG] Total chunks collectés: {len(full_chunks_themes)}")


        if len(relevant_docs) > chunks_len:
            selected_docs = random.sample(relevant_docs, chunks_len)
            #print("len >", query)
        else:
            selected_docs = relevant_docs
            #print("no len", query)

        for doc in selected_docs:
            full_chunks_themes.append({
                "page_content": doc.page_content,
                "metadata": doc.metadata
            })

        #print(query)
        #print(selected_docs)

    print(len(full_chunks_themes))
    return full_chunks_themes