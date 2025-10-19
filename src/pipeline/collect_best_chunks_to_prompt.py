import random

def find_best_chunk_to_prompt(vector_db, themes, k=2, fetch_k=40, lambda_mult=0.5, chunks_len=3): #ATTENTION REMTTRE K10
    full_chunks_themes = []

    # Ne chercher dans la vector database que les meilleurs chunks qui correspondent à un theme et pas les meilluerss chunks pour toute la vector db
    for doc in vector_db.get()["metadatas"][:10]:
        print(doc)

    for query in themes:
        retriever = vector_db.as_retriever(
            # search_type="mmr",
            # search_kwargs={"k": k, "fetch_k": fetch_k, "lambda_mult": lambda_mult}

            # Similarité
            search_type="similarity", 
            search_kwargs={"k": k} # "filter": {"theme": "napoléon, france, pouvoir" #query REMETTRE
            
            # Similarité avec seuil de score minimum
            #search_type="similarity_score_threshold",
            #search_kwargs={"k": k, "score_threshold": 0.4}
        )

        relevant_docs = retriever.invoke("napoléon, france, pouvoir") #query REMETTRE
        print(query)
        print(f"[DEBUG] Total chunks collectés: {len(full_chunks_themes)}")
        #print(f"[DEBUG]type de relevant_docs : {type(relevant_docs)}"")
        #print(f"[DEBUG]relevant_docs : {relevant_docs}")
        print(f"Nombre de chunks récupérés pour le thème -- {query} -- : {len(relevant_docs)}")

        # if len(relevant_docs) > chunks_len:
        #     selected_docs = random.sample(relevant_docs, chunks_len)
        # else:
        #     selected_docs = relevant_docs

        for doc in relevant_docs:
            # doc.metadata['theme'] = query # remplace l'ancien thème qui a été déterminé par le clustering
            full_chunks_themes.append({
                "page_content": doc.page_content,
                "metadata": doc.metadata
            })

    print(len(full_chunks_themes))
    return full_chunks_themes