def find_best_chunk_to_prompt(vector_db, themes):
    full_chunks_themes = []
    strings_chunks_themes = []

    for topic in themes:
        query = topic
    
        # Recherche les 5 chunks les plus similaires au sujet de la requête
        retriever = vector_db.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.5}
        )

        relevant_docs = retriever.invoke(query)
        full_chunks_themes.append(relevant_docs)
        
        
    for i, chunk in enumerate(full_chunks_themes):
        string = " ".join(doc.page_content for doc in chunk)

        strings_chunks_themes.append(string)

    return strings_chunks_themes