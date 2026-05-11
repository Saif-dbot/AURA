"""Configuration de l'application AURA - Extensible."""
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


# =====================
# APPLICATION
# =====================
APP_TITLE = "AURA - Advanced Universal Resume Architect & Analytics"
APP_GEOMETRY = "1200x800"
APP_BG = "#f4f6f9"
APP_THEME = "clam"

# =====================
# FONTS
# =====================
FONT_MAIN = ("Segoe UI", 11)
FONT_HEADER = ("Segoe UI", 24, "bold")
FONT_SUBHEADER = ("Segoe UI", 12)
FONT_BUTTON = ("Segoe UI", 10, "bold")

# =====================
# PATHS
# =====================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
APP_DATA_DIR = os.path.join(BASE_DIR, "data")
ENV_PATH = os.path.join(BASE_DIR, ".env")
_load_env_file(ENV_PATH)

DB_FILENAME = os.getenv("AURA_DB_FILENAME", "aura.db")
LOG_PATH = os.path.join(APP_DATA_DIR, "logs", "aura.log")

# Allow overriding the DB path without changing code.
DB_PATH = os.getenv("AURA_DB_PATH", os.path.join(APP_DATA_DIR, DB_FILENAME))

# =====================
# LLM - OLLAMA (LOCAL)
# =====================
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

# =====================
# LLM - GROQ API (CLOUD GRATUIT)
# =====================
# Documentation: https://console.groq.com
# Gratuit, limite requêtes mais suffisant pour tests
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")  # À configurer par l'utilisateur
GROQ_MODEL = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")

# =====================
# LLM - PRÉFÉRENCES
# =====================
LLM_PRIMARY_PROVIDER = os.getenv("LLM_PRIMARY_PROVIDER", "ollama")  # "ollama" ou "groq"

# =====================
# RAG - RETRIEVAL AUGMENTED GENERATION
# =====================
RAG_DOCS_FOLDER = os.path.join(APP_DATA_DIR, "documents")  # Dossier des manuels
RAG_EMBEDDINGS_MODEL = "all-MiniLM-L6-v2"  # Modèle d'embeddings
RAG_CHUNK_SIZE = 256  # Taille des chunks en tokens
RAG_CHUNK_OVERLAP = 50  # Chevauchement entre chunks
RAG_TOP_K = 3  # Nombre de documents à récupérer

# =====================
# AUTHENTIFICATION
# =====================
DEFAULT_ADMIN_USER = "admin"
DEFAULT_ADMIN_HINT = "Mot de passe initial: admin123"

# =====================
# HELPER FUNCTIONS
# =====================


def get_llm_config() -> dict:
    """Obtenir la configuration LLM actuelle."""
    return {
        "ollama_url": OLLAMA_BASE_URL,
        "ollama_model": OLLAMA_MODEL,
        "groq_api_key": GROQ_API_KEY,
        "groq_model": GROQ_MODEL,
        "primary_provider": LLM_PRIMARY_PROVIDER,
    }


def get_rag_config() -> dict:
    """Obtenir la configuration RAG actuelle."""
    return {
        "docs_folder": RAG_DOCS_FOLDER,
        "embeddings_model": RAG_EMBEDDINGS_MODEL,
        "chunk_size": RAG_CHUNK_SIZE,
        "chunk_overlap": RAG_CHUNK_OVERLAP,
        "top_k": RAG_TOP_K,
    }
