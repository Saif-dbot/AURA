import os


def _load_env_file(env_path: str) -> None:
	if not os.path.exists(env_path):
		return

	with open(env_path, "r", encoding="utf-8") as env_file:
		for raw_line in env_file:
			line = raw_line.strip()
			if not line or line.startswith("#") or "=" not in line:
				continue
			key, value = line.split("=", 1)
			key = key.strip()
			value = value.strip().strip('"').strip("'")
			if key and key not in os.environ:
				os.environ[key] = value


APP_TITLE = "AURA - Advanced Universal Resume Architect & Analytics"
APP_GEOMETRY = "1200x800"
APP_BG = "#f4f6f9"
APP_THEME = "clam"

FONT_MAIN = ("Segoe UI", 11)
FONT_HEADER = ("Segoe UI", 24, "bold")
FONT_SUBHEADER = ("Segoe UI", 12)
FONT_BUTTON = ("Segoe UI", 10, "bold")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
APP_DATA_DIR = os.path.join(BASE_DIR, "data")
ENV_PATH = os.path.join(BASE_DIR, ".env")
_load_env_file(ENV_PATH)

DB_FILENAME = os.getenv("AURA_DB_FILENAME", "aura.db")
LOG_PATH = os.path.join(APP_DATA_DIR, "logs", "aura.log")

# Allow overriding the DB path without changing code.
DB_PATH = os.getenv("AURA_DB_PATH", os.path.join(APP_DATA_DIR, DB_FILENAME))

OLLAMA_BASE_URL = "http://127.0.0.1:11434"
OLLAMA_MODEL = "llama3.1:8b"

DEFAULT_ADMIN_USER = "admin"
DEFAULT_ADMIN_HINT = "Mot de passe initial: admin123"