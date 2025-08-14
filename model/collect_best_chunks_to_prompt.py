def find_best_chunk_to_prompt(vector_db, themes):
    full_chunks_themes = []
    strings_chunks_themes = []

    for chunk in themes:
        #print(i)
        query = chunk
    
        retriever = vector_db.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.5}
        )

        elevant_docs = retriever.invoke(query)
        #print(elevant_docs)
        full_chunks_themes.append(elevant_docs)

    for i, chunk in enumerate(full_chunks_themes):
        string = " ".join(doc.page_content for doc in chunk)

        strings_chunks_themes.append(string)

################################
        ## TU as tous les paragraphe par thème, maintenant il faut les prendre en compte dans le prompt et qu'il génère 3 questions de QCM par thème
################################
    print(strings_chunks_themes)

    #print(full_chunks_themes[1])
    

    #return elevant_docs
