import json

def build_prompt(text: str, difficulty: str = "standard") -> str:
    niveau_instruction = {
        "facile": "La question doit être simple, accessible à un élève de collège.",
        "moyen": "La question doit correspondre à un niveau lycée ou début d’université.",
        "difficile": "La question doit être complexe, s’adresser à un étudiant avancé ou expert.",
        "standard": "Utilise un niveau intermédiaire (niveau lycée/université)."
    }[difficulty]

    return f"""
    Tu es un expert en pédagogie et tu dois créer 1 question de QCM pertinente à partir du texte ci-dessous.
    Poses les question comme le ferai un professeur.

    Quand tu génère le quizz, dans "correct_answer_long" écris moi une réponse longue à propos de la vrai réponse,
    qui aidera l'étudiant à rétenir pourquoi il a eu faux.

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
        "text": "...",
        "choices": {{"a": "...", "b": "...", "c": "...", "d": "..."}},
        "correct_answer": {{"lettre": "...", "answer": "..."}},
        "correct_answer_long": "..."
        "difficulty_level": "..."
    }}

    ## Exemples de chunks et résultats de QCM attendu

    ### Exemple 1
    #### Le chunk
    {{"En 1598, l’édit de Nantes fut promulgué par le roi Henri IV afin de mettre fin aux guerres de religion entre catholiques et protestants. Cet édit accordait aux protestants la liberté de culte dans certaines régions de France, ainsi que des droits civils et politiques. Cependant, le catholicisme restait la religion officielle du royaume."}}

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


    ### Exemple 2
    #### Le chunk
    {{"La photosynthèse est un processus par lequel les plantes transforment l’énergie lumineuse en énergie chimique. Grâce à la chlorophylle contenue dans leurs feuilles, elles absorbent le dioxyde de carbone de l’air et utilisent l’eau du sol pour produire du glucose et libérer de l’oxygène. Ce mécanisme est essentiel à la vie sur Terre."}}

    #### Le résultat
    {{
        "text": "Quel est le rôle principal de la photosynthèse chez les plantes ?",
        "choices": {{
            "a": "Produire de l’énergie chimique à partir de la lumière",
            "b": "Transformer l’oxygène en dioxyde de carbone",
            "c": "Remplacer l’eau par de l’air",
            "d": "Détruire le glucose pour libérer de l’énergie"
        }},
        "correct_answer": {{"lettre": "a", "answer": "Produire de l’énergie chimique à partir de la lumière"}},
        "correct_answer_long": "La photosynthèse permet aux plantes de capter la lumière grâce à la chlorophylle. Elles utilisent cette énergie pour transformer le CO₂ et l’eau en glucose, indispensable à leur croissance, tout en rejetant de l’oxygène. C’est un processus vital pour l’équilibre écologique.",
        "difficulty_level": "standard"
    }}


    ### Exemple 3
    #### Le chunk
    {{"Dans le roman 'Les Misérables' de Victor Hugo, le personnage de Jean Valjean incarne la rédemption. Ancien forçat condamné pour avoir volé du pain, il change de vie après avoir été sauvé par la bonté d’un évêque. Il devient un homme juste, mais reste poursuivi par l’inspecteur Javert, symbole de la loi inflexible."}}

    #### Le résultat
    {{
        "text": "Quel événement marque le début de la transformation de Jean Valjean dans Les Misérables ?",
        "choices": {{
            "a": "Sa rencontre avec l’évêque",
            "b": "Son arrestation par Javert",
            "c": "Son adoption de Cosette",
            "d": "Son retour en prison"
        }},
        "correct_answer": {{"lettre": "a", "answer": "Sa rencontre avec l’évêque"}},
        "correct_answer_long": "Jean Valjean est profondément marqué par l’acte de pardon et de générosité de l’évêque. Cet épisode déclenche son changement moral : il décide de devenir un homme honnête, ce qui constitue le véritable point de départ de sa rédemption.",
        "difficulty_level": "standard"
    }}


    Texte :
    \"\"\"{text}\"\"\"
    """
