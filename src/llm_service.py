import json
import urllib.error
import urllib.request
from typing import Dict, Optional


class OllamaService:
    def __init__(self, base_url: str, model: str, timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def _post(self, endpoint: str, payload: Dict) -> Optional[Dict]:
        url = f"{self.base_url}{endpoint}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
                return json.loads(body)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
            return None

    def generate_maintenance_instruction(self, query: str, knowledge_hints: str = "") -> Optional[str]:
        prompt = (
            "Tu es un assistant de maintenance industrielle. "
            "Donne une procedure pratique, structuree et concise en francais. "
            "Inclure: securite, outils, etapes, verification finale. "
            "Si l'information est insuffisante, precise les hypotheses.\n\n"
            f"Contexte interne AURA:\n{knowledge_hints}\n\n"
            f"Demande utilisateur:\n{query}"
        )
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        }
        result = self._post("/api/generate", payload)
        if not result:
            return None
        response_text = result.get("response", "").strip()
        return response_text or None

    def is_available(self) -> bool:
        """Vérifier si Ollama local répond."""
        try:
            payload = {"model": self.model, "prompt": "test", "stream": False, "options": {"temperature": 0}}
            res = self._post("/api/generate", payload)
            return res is not None
        except Exception:
            return False
