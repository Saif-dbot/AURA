# ✅ RAG & LLM Multi-Provider - Implémentation Complète

## 📦 Fichiers créés

### 1. Système RAG (Retrieval Augmented Generation)

#### **`src/rag/__init__.py`**
- Module RAG vide (initialisation)

#### **`src/rag/embeddings.py`** (152 lignes)
- `EmbeddingsManager`: Gestion des embeddings avec sentence-transformers
- Recherche sémantique cosinus
- Import/export des index en JSON

**Capacités:**
- Génération automatique d'embeddings
- Recherche par similarité
- Support de plusieurs documents

#### **`src/rag/ingest.py`** (167 lignes)
- `DocumentIngestor`: Ingestion multi-format de documents
- Support: PDF, DOCX, TXT
- Chunking automatique avec chevauchement
- Traitement de dossiers entiers

**Capacités:**
- Extraction de texte avec PyPDF2
- Découpage intelligent par phrases
- Métadonnées per-chunk (source, page, type)

### 2. Service RAG intégré

#### **`src/rag_service.py`** (166 lignes)
- `RAGService`: Service de haut niveau pour RAG
- Indexation de documents
- Recherche avec contexte
- Construction de prompts augmentés

**Capacités:**
- `index_documents()`: Indexer une liste de docs
- `index_folder()`: Indexer un dossier entier
- `retrieve()`: Recherche sémantique
- `build_context()`: Formatage pour LLM
- `augmented_prompt()`: Prompt RAG complet
- `get_sources()`: Citation des sources

### 3. Gestion multi-LLM

#### **`src/llm_manager.py`** (200 lignes)
- `GroqService`: Intégration Groq API (cloud gratuit)
- `LLMManager`: Gestionnaire multi-provider
- Support Ollama + Groq
- Fallback automatique

**Capacités:**
- Configuration dynamique
- Test de disponibilité
- Fallback automatique si l'un échoue
- Format de réponse cohérent

### 4. Interface utilisateur

#### **`src/settings_page.py`** (230 lignes)
- Page de configuration complète
- UI moderne avec des sections claires
- Test de connexion en direct
- Sauvegarde en fichier `.env`

**Contient:**
- Configuration Ollama (URL + modèle)
- Configuration Groq (clé API + modèle)
- Préférence LLM par défaut
- Boutons de test
- Sauvegarde persistante

### 5. Documentation utilisateur

#### **`GROQ_SETUP.md`** (Plan complet)
- Guide complet Groq gratuit
- Étapes d'inscription
- Configuration dans AURA
- Modèles disponibles
- Dépannage

---

## 🎯 Architecture d'intégration

```
┌─────────────────────────────────────────┐
│         USER INTERFACE (GUI)            │
│   ┌─ Settings Page (Groq + Ollama)     │
│   ├─ Prompt Page (utilise LLM)         │
│   └─ NLP Page (utilise RAG)            │
└────────────────┬────────────────────────┘
                 │
        ┌────────▼──────────┐
        │   LLMManager      │
        │  (Multi-provider) │
        ├─────────┬─────────┤
        │ Ollama  │  Groq   │
        │ (Local) │  (API)  │
        └─────────┴─────────┘
        
        ┌────────────────────┐
        │   RAGService       │
        ├────────┬───────────┤
        │Ingestion│Embeddings │
        │(PDF...)│(Vector DB)│
        └────────┴───────────┘
```

---

## 🚀 Utilisation dans le code

### 1. Initialiser RAG + LLM

```python
# Initialisation RAG
from src.rag_service import RAGService
rag = RAGService()
rag.index_folder("data/documents")

# Initialisation LLM
from src.llm_manager import LLMManager
llm_manager = LLMManager()
llm_manager.setup_ollama("http://127.0.0.1:11434", "llama3.1:8b")
llm_manager.setup_groq("gsk_xxxx...xxxx")
llm_manager.set_primary_provider("ollama")
```

### 2. Utiliser RAG pour augmenter les prompts

```python
# Récupérer le contexte
context = rag.build_context("Qu'est-ce que le TRS?")

# Construire un prompt augmenté
prompt = rag.augmented_prompt(
    user_query="Comment optimiser le TRS?",
    system_prompt="Tu es un expert en maintenance"
)

# Générer une réponse
response = llm_manager.generate_instruction(
    query="Comment optimiser le TRS?",
    knowledge_hints=context
)
```

### 3. Citer les sources

```python
sources = rag.get_sources("TRS", top_k=3)
# Retourne: ["manuel_maintenance.pdf", "rapport_2026.docx"]
```

---

## 📋 Étapes d'intégration dans gui.py

> **À faire manuellement** (outils limitations):

1. **Importer les modules** dans `src/gui.py`:
```python
from src.settings_page import (
    build_settings_page, test_ollama_connection, 
    test_groq_connection, save_llm_config, reset_llm_config
)
from src.rag_service import RAGService
from src.llm_manager import LLMManager
```

2. **Ajouter à NAV_ITEMS** dans `src/theme.py`:
```python
NAV_ITEMS = [
    # ... existants ...
    ("Paramètres", "tab_settings"),
]
```

3. **Dans `__init__` de AuraApp**, après les autres services:
```python
# RAG Service
self.rag = RAGService()
# (chargement optionnel: self.rag.index_folder("data/documents"))

# LLM Manager
self.llm_manager = LLMManager()
self.llm_manager.setup_ollama(OLLAMA_BASE_URL, OLLAMA_MODEL)
# Groq sera configuré par l'utilisateur via Settings
```

4. **Ajouter la page settings** dans la construction des pages:
```python
# Dans la boucle de création de pages:
elif name == "tab_settings":
    build_settings_page(self, self.pages[name])
```

5. **Attacher les fonctions de settings** à `self`:
```python
self.test_ollama_connection = lambda: test_ollama_connection(self)
self.test_groq_connection = lambda: test_groq_connection(self)
self.save_llm_config = lambda: save_llm_config(self)
self.reset_llm_config = lambda: reset_llm_config(self)
```

6. **Mettre à jour prompt_generator.py** pour utiliser RAG + LLMManager:
```python
# Au lieu de self.llm_service, utiliser self.llm_manager
response = self.llm_manager.generate_instruction(
    query=user_input,
    knowledge_hints=context  # du RAG
)
```

---

## ⚙️ Configuration utilisateur

### Fichier `.env` (à la racine)
```
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.1:8b
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
GROQ_MODEL=mixtral-8x7b-32768
LLM_PRIMARY_PROVIDER=ollama
```

### Obtenir une clé Groq gratuite
1. Allez sur https://console.groq.com
2. Sign up gratuit (pas de carte de crédit)
3. Créez une clé API
4. Collez-la dans AURA → Paramètres

---

## 🧪 Tests

### Test Ollama
```bash
curl http://127.0.0.1:11434/api/tags
```

### Test Groq API
```bash
# Depuis Python:
from src.llm_manager import GroqService
svc = GroqService("gsk_xxxx")
print(svc.is_available())  # True si OK
```

### Test RAG
```python
from src.rag_service import RAGService
rag = RAGService()
rag.index_folder("data/documents")
results = rag.retrieve("maintenance", top_k=3)
print(results)
```

---

## ✅ Checklist de déploiement

- [ ] Importer RAGService + LLMManager dans gui.py
- [ ] Ajouter "Paramètres" à NAV_ITEMS
- [ ] Initialiser services dans AuraApp.__init__
- [ ] Créer page settings
- [ ] Tester Ollama (connexion locale)
- [ ] Tester Groq (avec clé API gratuite)
- [ ] Intégrer RAG dans prompt_generator
- [ ] Intégrer RAG dans nlp_engine
- [ ] Documenter pour utilisateur

---

## 📚 Résumé des capacités

| Fonctionnalité | Statut | Details |
|---|---|---|
| **RAG Indexing** | ✅ | PDF, DOCX, TXT, dossiers |
| **Embeddings** | ✅ | Sentence-transformers, stockage JSON |
| **Recherche** | ✅ | Similarité cosinus, top-k |
| **Ollama** | ✅ | Local, test connexion |
| **Groq API** | ✅ | Gratuit, fallback |
| **Configuration UI** | ✅ | Page settings complète |
| **Persistance** | ✅ | Fichier .env |
| **Tests** | ✅ | Boutons dans Settings |

---

**Version:** 1.0  
**Date:** 11 Mai 2026  
**Status:** ✅ Prêt pour intégration dans gui.py
