import pandas as pd
import random
from pathlib import Path
import json
import requests

def build_resume_tables(resume):
    """Construit (1) le bilan par thème et (2) le tableau détaillé trié par thème."""
    df = pd.DataFrame(resume)
    if df.empty:
        per_theme = pd.DataFrame(columns=["Thème", "Bonnes réponses", "Questions", "% Réussite"])
        detailed = pd.DataFrame(columns=["Thème", "Question", "Ta réponse", "Bonne réponse", "Résultat"])
        return per_theme, detailed

    per_theme = (
        df.groupby("Thème")["Correct"]
        .agg([("Bonnes réponses", "sum"), ("Questions", "count")])
        .assign(**{"% Réussite": lambda d: (d["Bonnes réponses"] / d["Questions"] * 100).round(0)})
        .sort_values("% Réussite", ascending=True)
        .reset_index()
    )

    detailed = (
        df[["Thème", "Question", "Ta réponse", "Bonne réponse", "Résultat"]]
        .sort_values(["Thème", "Question"], ascending=[True, True])
        .reset_index(drop=True)
    )
    return per_theme, detailed

def _normalize_questions(items):
    """Transforme la liste d'items -> liste de questions pour l'UI."""
    questions = []
    for item in items:
        options = list(item["choices"].values())
        random.shuffle(options)
        questions.append({
            "question": item["question"],
            "options": options,
            "réponse": item["correct_answer"],
            "theme": item["_theme"],
            "long_answer": item["correct_answer_long"],
            "difficulty": item["difficulty"],
            "metadata": item["metadata"]
        })
    return questions

def _extract_quiz_payload(data):
    """Cherche récursivement une clé 'quiz' contenant une liste."""
    if isinstance(data, dict):
        if "quiz" in data and isinstance(data["quiz"], list):
            return data["quiz"]
        for v in data.values():
            out = _extract_quiz_payload(v)
            if out is not None:
                return out
    elif isinstance(data, list):
        for el in data:
            out = _extract_quiz_payload(el)
            if out is not None:
                return out
    return None

def load_questions_from_api(api_base_url, api_question_path):
    url = f"{api_base_url.rstrip('/')}/{api_question_path.lstrip('/')}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()

    if not isinstance(data, dict) or "quiz" not in data:
        raise ValueError("Format inattendu: attendu {quiz:[...]}, reçu autre chose.")

    items = []
    for bloc in data["quiz"]:
        q = bloc.get("question", {})
        if not q:
            continue

        llm = q.get("llm_response", {})
        meta = q.get("metadata", {})

        qq = {
            "question": llm.get("text", ""),
            "choices": llm.get("choices", {}),
            "correct_answer": llm.get("correct_answer", {}).get("answer", ""),
            "correct_answer_long": llm.get("correct_answer_long", ""),
            "difficulty": llm.get("difficulty_level", ""),
            "_theme": meta.get("theme", "Sans thème"),
            "metadata": meta,
        }
        items.append(qq)

    return _normalize_questions(items)

def load_questions(api_base_url, api_question_path, use_api, require_api, json_path):
    if use_api:
        try:
            return load_questions_from_api(api_base_url, api_question_path)
        except Exception as e:
            if require_api:
                raise SystemExit(f"[ERREUR API] {e}")
            else:
                print(f"[WARN] API indisponible ({e}). Bascule sur le JSON local.")
    # Fallback JSON autorisé uniquement si REQUIRE_API=0
    if not json_path.exists():
        raise SystemExit(
            f"[ERREUR] JSON local introuvable : {json_path}. "
            "Active REQUIRE_API=1 pour forcer l’API ou remets questions_llm.json."
        )
    # return load_questions_from_json(json_path)