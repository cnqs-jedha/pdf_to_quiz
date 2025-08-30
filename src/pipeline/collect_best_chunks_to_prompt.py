def find_best_chunk_to_prompt(vector_db, themes):
    full_chunks_themes = []
    strings_chunks_themes = []

    for chunk in themes:
        query = chunk
    
        retriever = vector_db.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.5}
        )

        elevant_docs = retriever.invoke(query)
        full_chunks_themes.append(elevant_docs)

    for i, chunk in enumerate(full_chunks_themes):
        string = " ".join(doc.page_content for doc in chunk)

        strings_chunks_themes.append(string)

    return strings_chunks_themes