def build_prompt(doc: str, theme: str, difficulty: str = "standard") -> str:
    niveau_instruction = {
        "facile": "La question doit être simple, accessible à un élève de collège.",
        "moyen": "La question doit correspondre à un niveau lycée ou début d’université.",
        "difficile": "La question doit être complexe, s’adresser à un étudiant avancé ou expert.",
        "standard": "Utilise un niveau intermédiaire (niveau lycée/université)."
    }[difficulty]

    return f"""
    Tu es un expert en pédagogie et tu dois créer 3 questions QCM à partir du texte ci-dessous.
    Poses les question comme le ferai un professeur.

    {niveau_instruction}

    **Important** : tu ne dois utiliser que les informations contenues dans le texte ci-dessous.  
    **Tu ne dois en aucun cas utiliser des connaissances extérieures.**

    Contrainte :
    - La question doit porter sur une information claire et importante du texte.
    - Il doit y avoir exactement 4 choix.
    - Les 4 choix doivent être différents.
    - Une seule bonne réponse.
    - Le niveau de difficulté de la question doit correspondre à celui demandé.
    - Tu ne dois pas inventer d'information : toute la question et ses réponses doivent découler directement du texte.
    - Les 3 questions doivent être différentes.
    - Utilise uniquement des guillemets doubles `"` pour les clés et les valeurs.
    - Pas de guillemets simples `'`.
    - **Réponds uniquement avec un objet JSON valide**, sans aucune explication, ni phrase introductive, ni conclusion.

    {{
        "Thème" : "{theme}",
        "questions: {{
            "question": "...",
            "choices": {{"a": "...", "b": "...", "c": "...", "d": "..."}},
            "correct_answer": {{"lettre": "...", "answer": "..."}},
            "difficulty_level": "..."
        }}, 
        {{
            "question": "...",
            "choices": {{"a": "...", "b": "...", "c": "...", "d": "..."}},
            "correct_answer": {{"lettre": "...", "answer": "..."}},
            "difficulty_level": "..."
        }},
        {{
            "question": "...",
            "choices": {{"a": "...", "b": "...", "c": "...", "d": "..."}},
            "correct_answer": {{"lettre": "...", "answer": "..."}},
            "difficulty_level": "..."
        }}
    }}

    ## Exemples de chunks et résultats de QCM attendu

    ### Exemple 1
    #### Le chunk
    {{"En 1789, la Révolution française marque un tournant majeur dans l'histoire de France..."}}

    #### Le résultat
    {{
        "question": "Quel événement a marqué un tournant majeur dans l'histoire de France en 1789 ?",
        "choices": {{
            "a": "La chute de Napoléon",
            "b": "La Révolution française",
            "c": "La guerre franco-prussienne",
            "d": "Le couronnement de Louis XVI"
        }},
        "correct_answer": {{
            "lettre": "b",
            "answer": "La Révolution française"
        }},
        "difficulty_level": "standard"
    }}

    ### Exemple 2
    #### Le chunk
    {{"L’eau change d’état selon la température..."}}

    #### Le résultat
    {{
        "question": "Quel est le nom du phénomène où l'eau passe de l'état liquide à l'état gazeux à 100 °C ?",
        "choices": {{
            "a": "La condensation",
            "b": "La solidification",
            "c": "La vaporisation",
            "d": "La fusion"
        }},
        "correct_answer": {{
            "lettre": "c",
            "answer": "La vaporisation"
        }},
        "difficulty_level": "difficile"
    }}

    ### Exemple 3
    #### Le chunk
    {{"L’Amazonie est une vaste forêt tropicale..."}}

    #### Le résultat
    {{
        "question": "Quel rôle joue l'Amazonie dans le climat mondial ?",
        "choices": {{
            "a": "Elle produit des vents froids",
            "b": "Elle régule le climat mondial",
            "c": "Elle empêche les tsunamis",
            "d": "Elle bloque les courants marins"
        }},
        "correct_answer": {{
            "lettre": "b",
            "answer": "Elle régule le climat mondial"
        }},
        "difficulty_level": "facile"
    }}

    Texte :
    \"\"\"{doc}\"\"\"
    """
