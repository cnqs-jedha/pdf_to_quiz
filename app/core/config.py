import os
from pathlib import Path

def _env_flag(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return str(v).strip().lower() in {"1", "true", "yes", "on"}

# Par défaut pour Docker Compose : API joignable via le nom de service "api"
API_BASE_URL       = os.getenv("API_BASE_URL", "https://cnsq-quiz-api.hf.space")
API_QUESTIONS_PATH = os.getenv("API_QUESTIONS_PATH", "/quiz")
USE_API            = _env_flag("USE_API", True)
REQUIRE_API        = _env_flag("REQUIRE_API", True)

BASE_DIR = Path(__file__).parent
json_path = BASE_DIR / "questions_llm.json"  # seulement si fallback autorisé