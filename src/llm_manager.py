"""Gestionnaire multi-provider de LLM pour AURA."""
import json
import urllib.error
import urllib.request
from typing import Dict, Optional, Literal
from src.llm_service import OllamaService


class GroqService:
    """Service pour Groq API (LLM cloud gratuit)."""
    
    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768", timeout: int = 60):
        """Initialiser le service Groq.
        
        Args:
            api_key: Clé API Groq (gratuit sur https://console.groq.com)
            model: Modèle à utiliser
            timeout: Timeout pour les requêtes
        """
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.base_url = "https://api.groq.com/openai/v1"
        self.provider = "groq"

    def _post_json(self, endpoint: str, payload: Dict) -> Optional[Dict]:
        """Effectuer une requête POST JSON à Groq."""
        url = f"{self.base_url}{endpoint}"
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
                return json.loads(body)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as e:
            print(f"Erreur Groq API: {e}")
            return None

    def generate_maintenance_instruction(self, query: str, knowledge_hints: str = "") -> Optional[str]:
        """Générer une instruction de maintenance via Groq."""
        system_message = (
            "Tu es un assistant expert en maintenance industrielle. "
            "Donne une procédure pratique, structurée et concise en français. "
            "Inclure: sécurité, outils, étapes numérotées, vérification finale. "
            "Si l'information est insuffisante, précise les hypothèses."
        )
        
        user_message = f"{knowledge_hints}\n\nDemande: {query}" if knowledge_hints else query
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.2,
            "max_tokens": 1024
        }
        
        result = self._post_json("/chat/completions", payload)
        if not result or "choices" not in result:
            return None
        
        try:
            response_text = result["choices"][0]["message"]["content"].strip()
            return response_text or None
        except (KeyError, IndexError):
            return None
    
    def is_available(self) -> bool:
        """Vérifier si Groq API est accessible."""
        if not self.api_key or self.api_key.strip() == "":
            return False
        try:
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 10
            }
            result = self._post_json("/chat/completions", payload)
            return result is not None
        except:
            return False


class MistralService:
    """Service pour Mistral API (cloud)."""

    def __init__(self, api_key: str, model: str = "mistral-large", timeout: int = 60):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.base_url = "https://api.mistral.ai"
        self.provider = "mistral"

    def _post_json(self, endpoint: str, payload: Dict) -> Optional[Dict]:
        url = f"{self.base_url}{endpoint}"
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
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
            "Inclure: securite, outils, etapes, verification finale."
        )
        user_input = f"{knowledge_hints}\n\nDemande: {query}" if knowledge_hints else query
        payload = {
            "inputs": f"{prompt}\n\n{user_input}",
            "parameters": {"temperature": 0.2, "max_new_tokens": 512}
        }
        endpoint = f"/v1/models/{self.model}/generate"
        result = self._post_json(endpoint, payload)
        if not result:
            return None

        # Tentatives d'extraction du texte selon différents formats de réponse
        try:
            if "results" in result and isinstance(result["results"], list):
                r0 = result["results"][0]
                if isinstance(r0, dict):
                    if "content" in r0 and isinstance(r0["content"], list):
                        for item in r0["content"]:
                            if isinstance(item, dict) and "text" in item:
                                return item["text"].strip()
                    if "output_text" in r0:
                        return str(r0["output_text"]).strip()

            if "outputs" in result and isinstance(result["outputs"], list):
                for out in result["outputs"]:
                    if isinstance(out, dict) and "content" in out:
                        for c in out["content"]:
                            if isinstance(c, dict) and "text" in c:
                                return c["text"].strip()

            if "text" in result:
                return str(result["text"]).strip()
            if "response" in result:
                return str(result["response"]).strip()
        except Exception:
            return None

        return None

    def is_available(self) -> bool:
        if not self.api_key or self.api_key.strip() == "":
            return False
        try:
            payload = {"inputs": "test", "parameters": {"max_new_tokens": 1}}
            result = self._post_json(f"/v1/models/{self.model}/generate", payload)
            return result is not None
        except:
            return False


class LLMManager:
    """Gestionnaire multi-provider de LLM."""
    
    def __init__(self):
        self.ollama = None
        self.groq = None
        self.mistral = None
        self.primary_provider = "ollama"  # Par défaut Ollama
    
    def setup_ollama(self, base_url: str, model: str) -> None:
        """Configurer Ollama."""
        self.ollama = OllamaService(base_url, model)
    
    def setup_groq(self, api_key: str, model: str = "mixtral-8x7b-32768") -> None:
        """Configurer Groq."""
        if api_key and api_key.strip():
            self.groq = GroqService(api_key, model)

    def setup_mistral(self, api_key: str, model: str = "mistral-large") -> None:
        """Configurer Mistral API."""
        if api_key and api_key.strip():
            self.mistral = MistralService(api_key, model)
    
    def set_primary_provider(self, provider: Literal["ollama", "groq", "mistral"]) -> None:
        """Définir le provider par défaut."""
        if provider in ["ollama", "groq", "mistral"]:
            self.primary_provider = provider
    
    def generate_instruction(self, query: str, knowledge_hints: str = "", provider: str = None) -> Optional[str]:
        """Générer une instruction avec fallback automatique.
        
        Args:
            query: Requête utilisateur
            knowledge_hints: Contexte documentaire
            provider: Provider spécifique (None = utiliser le primary)
            
        Returns:
            Instruction générée ou None
        """
        target_provider = provider or self.primary_provider
        
        # Essayer le provider cible puis fallback vers les autres disponibles
        order = []
        if target_provider == "ollama":
            order = ["ollama", "mistral", "groq"]
        elif target_provider == "mistral":
            order = ["mistral", "ollama", "groq"]
        else:
            order = ["groq", "mistral", "ollama"]

        for p in order:
            try:
                if p == "ollama" and self.ollama and getattr(self.ollama, "is_available", lambda: True)():
                    res = self.ollama.generate_maintenance_instruction(query, knowledge_hints)
                    if res:
                        return res
                if p == "groq" and self.groq and self.groq.is_available():
                    res = self.groq.generate_maintenance_instruction(query, knowledge_hints)
                    if res:
                        return res
                if p == "mistral" and self.mistral and self.mistral.is_available():
                    res = self.mistral.generate_maintenance_instruction(query, knowledge_hints)
                    if res:
                        return res
            except Exception:
                continue

        return None
    
    def get_available_providers(self) -> dict:
        """Obtenir les providers disponibles."""
        ollama_available = False
        groq_available = False
        mistral_available = False
        
        if self.ollama:
            try:
                ollama_available = self.ollama.is_available()
            except:
                ollama_available = False
        
        if self.groq:
            try:
                groq_available = self.groq.is_available()
            except:
                groq_available = False

        if self.mistral:
            try:
                mistral_available = self.mistral.is_available()
            except:
                mistral_available = False
        
        return {
            "ollama": ollama_available,
            "groq": groq_available,
            "mistral": mistral_available
        }
