def build_prompt(doc: str, theme: str, difficulty: str = "standard") -> str:
    niveau_instruction = {
        "facile": "La question doit être simple, accessible à un élève de collège.",
        "moyen": "La question doit correspondre à un niveau lycée ou début d’université.",
        "difficile": "La question doit être complexe, s’adresser à un étudiant avancé ou expert.",
        "standard": "Utilise un niveau intermédiaire (niveau lycée/université)."
    }[difficulty]

    # Variable qui spécifie la structure du JSON attendu
    json_output_format = """
    {
        "Thème": "__THEME__",
        "questions": [
            {
                "question": "...",
                "choices": {"a": "...", "b": "...", "c": "...", "d": "..."},
                "correct_answer": {"lettre": "...", "answer": "..."},
                "difficulty_level": "..."
            },
            {
                "question": "...",
                "choices": {"a": "...", "b": "...", "c": "...", "d": "..."},
                "correct_answer": {"lettre": "...", "answer": "..."},
                "difficulty_level": "..."
            },
            {
                "question": "...",
                "choices": {"a": "...", "b": "...", "c": "...", "d": "..."},
                "correct_answer": {"lettre": "...", "answer": "..."},
                "difficulty_level": "..."
            }
        ]
    }
    """.replace("__THEME__", theme)


    return f"""
    Tu es un professeur et tu dois créer 3 questions à choix multiples (QCM) à partir du contexte ci-dessous.

    Tu dois uniquement utiliser les informations contenues dans le contexte. Tu ne dois pas mobiliser de connaissances extérieures ni inventer d'information.  

    Tu dois adapter ton langage et la difficulté des questions à choix multiples au niveau de difficulté suivant : {niveau_instruction}.
    
    Les questions et les choix de réponse doivent être clairs, précis et sans ambiguité.
    Tu ne dois pas faire de fautes de français : pas de fautes d'orthographe, de conjugaison ou de grammaire.
    
    Tu dois formuler des énoncés de question qui répondent aux critères suivants :
    - chaque énoncé doit poser une seule question
    - chaque question doit porter sur une information claire et importante du contexte : par exemple, une date, un lieu, un personnage historique important, la définition d'un concept.
    - l'énoncé ne doit pas être négatif 
    - l'énoncé ne doit pas induire de jugement de valeur
    - l'énoncé ne doit pas donner d'indice sur la bonne réponse
    - les trois énoncés de questions doivent porter sur des éléments différents du contexte

    Pour chaque question, tu dois formuler quatre choix possibles : 
    - une seule et unique réponse sera correcte
    - les trois autres choix devront être plausibles mais strictement faux
    - chaque choix de réponse sera différent : un choix ne doit pas être répété avec une tournure synonyme
    - chaque choix sera affiché dans un ordre neutre : il peut être alphabétique, chronologique ou numérique
    - chaque choix sera homogène en termes de structure grammaticale

    Le résultat attendu devra respecter les consignes suivantes :
    - utilise uniquement des guillemets doubles `"` pour les clés et les valeurs.
    - n'utilise pas de guillemets simples `'`.
    - **réponds uniquement avec un objet JSON valide**, sans aucune explication, ni phrase introductive, ni conclusion.
    
    Voici le format attendu en sortie : {json_output_format}

    Pour t'aider, voici un bon exemple et un mauvais exemple de question.
    
    ###### DEBUT DES EXEMPLES ######
    ###### Bon exemple de question
    {{
        "question": "Quel événement a marqué un tournant majeur dans l'histoire de France en 1789 ?",
        "choices": {{
            "a": "La chute de Napoléon",
            "b": "La Révolution française",
            "c": "La guerre franco-prussienne",
            "d": "Le couronnement de Louis XVI",
        }},
        "correct_answer": {{
            "lettre": "b",
            "answer": "La Révolution française"
        }},
        "difficulty_level": "standard"
    }}

    ###### Mauvais exemple de question, à ne pas reproduire
    {{
        "question": "Qui n'a pas été couronné par le pape en l'an 800 ?",
        "choices": {{
            "a": "Charlemagne",
            "b": "Clovis",
            "c": "Carolus Magnus",
            "d": "Charles Ier"
        }},
        "correct_answer": {{
            "lettre": "b",
            "answer": "Clovis"
        }},
        "difficulty_level": "difficile"
    }}

    ###### FIN DES EXEMPLES ######
    
    Contexte :
    < DEBUT CONTEXTE >
    {doc}
    < FIN CONTEXTE >
    """
