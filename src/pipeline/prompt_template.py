import json

def build_prompt(text: str, difficulty: str = "standard") -> str:
    niveau_instruction = {
        "facile": "La question doit être simple, accessible à un élève de collège.",
        "moyen": "La question doit correspondre à un niveau lycée ou début d’université.",
        "difficile": "La question doit être complexe, s’adresser à un étudiant avancé ou expert.",
        "standard": "Utilise un niveau intermédiaire (niveau lycée/université)."
    }[difficulty]

    # Variable qui spécifie la structure du JSON attendu
    json_output_format = """
    {
        "text": "...",
        "choices": {"a": "...", "b": "...", "c": "...", "d": "..."},
        "correct_answer": {"lettre": "...", "answer": "..."},
        "correct_answer_long": "...",
        "difficulty_level": "..."
    }
    """

    return f"""
    Tu es un expert en pédagogie et tu dois créer 1 question de QCM pertinente à partir du contexte ci-dessous.
    Poses les question comme le ferai un professeur.

    Tu dois uniquement utiliser les informations contenues dans le contexte. Tu ne dois pas mobiliser de connaissances extérieures ni inventer d'information.  

    Quand tu génère le quizz, dans "correct_answer_long" écris moi une réponse longue à propos de la vrai réponse,
    qui aidera l'étudiant à rétenir pourquoi il a eu faux.
    
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
    - Chaque choix doit faire une longueur maximum de 5 mots

    Le résultat attendu devra respecter les consignes suivantes :
    - utilise uniquement des guillemets doubles `"` pour les clés et les valeurs.
    - n'utilise pas de guillemets simples `'`.
    - **réponds uniquement avec un objet JSON valide**, sans aucune explication, ni phrase introductive, ni conclusion.
    
    Voici le format attendu en sortie : {json_output_format}

    Pour t'aider, voici un bon exemple et un mauvais exemple de question.
    
    ###### DEBUT DES EXEMPLES ######
    ###### Bon exemple de question

    #### Le résultat
    {{
        "text": "Quel était l’objectif principal de l’édit de Nantes en 1598 ?",
        "choices": {{
            "a": "Renforcer le pouvoir du pape en France",
            "b": "Mettre fin aux guerres de religion",
            "c": "Imposer le protestantisme comme religion officielle",
            "d": "Supprimer les droits civils des catholiques"
        }},
        "correct_answer": {{"lettre": "b", "answer": "Mettre fin aux guerres de religion"}},
        "correct_answer_long": "L’édit de Nantes fut signé par Henri IV en 1598 pour apaiser les tensions entre catholiques et protestants. Il garantissait aux protestants certains droits civils et la liberté de culte dans des lieux précis, mais reconnaissait le catholicisme comme religion d’État. Son but était donc la paix religieuse.",
        "difficulty_level": "standard"
    }}


    ###### Mauvais exemple de question, à ne pas reproduire
    {{
        "text": "Qui n'a pas été couronné par le pape en l'an 800 ?",
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
        "correct_answer_long": "Carolus Magnus et Charles Ier correspondent à Charlemagne qui a été couronné en 800.",
        "difficulty_level": "difficile"
    }}


    ###### FIN DES EXEMPLES ######
    
    Contexte :
    < DEBUT CONTEXTE >
    {text}
    < FIN CONTEXTE >
    """
