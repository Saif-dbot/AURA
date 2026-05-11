# 📖 GUIDE D'UTILISATION - RAG & Multi-LLM pour AURA

## 🎯 Résumé de ce qui a été créé

J'ai implémenté **deux grandes fonctionnalités**:

### 1️⃣ **RAG (Retrieval Augmented Generation)**
- Indexez vos manuels, procédures, rapports (PDF, DOCX, TXT)
- AURA les analysera et enrichira les réponses LLM avec le contexte
- Les sources seront citées automatiquement

### 2️⃣ **Support Multi-LLM**
- **Ollama** (local, aucune limite) - par défaut
- **Groq API** (cloud gratuit, très performant) - alternative

---

## 📝 OÙ AJOUTER L'API KEY GROQ

### **Option 1: Via l'interface AURA (Recommandé) ⭐**

> Les fichiers pour cette page sont déjà créés!

1. **Lancer AURA** (une fois intégrée)
2. **Aller dans "⚙️ Paramètres"** (barre de navigation gauche)
3. **Section "☁️ Groq API"**:
   - Cliquer sur **"Inscription gratuite: https://console.groq.com"** (lien dans l'app)
   - Créer un compte (gratuit, pas de carte de crédit)
   - Créer une clé API
   - Copier la clé (format: `gsk_xxx...xxx`)
   - Coller dans le champ **"Clé API Groq"**
4. **Cliquer "🔍 Tester Groq API"** pour vérifier
5. **Cliquer "💾 Enregistrer Configuration"**
6. **Changer préférence LLM** si vous voulez utiliser Groq par défaut

### **Option 2: Fichier .env (Avancé)**

À la racine du projet, créez un fichier `.env`:

```env
# Ollama (local)
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.1:8b

# Groq API (gratuit)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
GROQ_MODEL=mixtral-8x7b-32768

# Préférence
LLM_PRIMARY_PROVIDER=ollama
```

---

## ✅ ÉTAPES D'OBTENTION CLÉ GROQ GRATUITE

### **Groq API - Pourquoi gratuit?**
- Service nouveau et performant
- Cherche des utilisateurs pour tester
- Gratuit = Excellent pour développement

### **Comment obtenir:**

1. **Aller sur**: https://console.groq.com
2. **"Sign Up"** (email + mot de passe)
3. **Confirmer votre email**
4. **Aller dans "API Keys"**
5. **Cliquer "Create API Key"**
6. **Copier la clé** (n'apparaît qu'une fois!)
   - Format: `gsk_xxxxxxxxxxxxxxxxxxxxxxxx`
7. **Coller dans AURA → Paramètres**

> Voir **`GROQ_SETUP.md`** dans le projet pour guide complet

---

## 🚀 FICHIERS CRÉÉS

| Fichier | Description | Lignes |
|---------|-------------|--------|
| **`src/rag_service.py`** | Service RAG complet | 166 |
| **`src/rag/embeddings.py`** | Gestion des embeddings | 152 |
| **`src/rag/ingest.py`** | Ingestion documents | 167 |
| **`src/llm_manager.py`** | Multi-provider LLM | 200 |
| **`src/settings_page.py`** | UI de configuration | 230 |
| **`GROQ_SETUP.md`** | Guide Groq API | 🎯 Lire ceci! |
| **`RAG_LLM_IMPLEMENTATION.md`** | Doc technique complète | Référence |

---

## 🔌 INTÉGRATION DANS gui.py

> **À faire par vous** (outils limitations):

### **1. Importer au top du fichier:**
```python
from src.settings_page import (
    build_settings_page, test_ollama_connection, 
    test_groq_connection, save_llm_config, reset_llm_config
)
from src.rag_service import RAGService
from src.llm_manager import LLMManager
```

### **2. Ajouter à theme.py → NAV_ITEMS:**
```python
NAV_ITEMS = [
    ("Vue d'ensemble", "tab_dashboards"),
    ("Intelligence Tech", "tab_nlp"),
    ("Aide à la Décision", "tab_prompt"),
    ("Planification & TRS", "tab_planning"),
    ("Équipes & Tasks", "tab_scheduling"),
    ("Log & Audit", "tab_history"),
    ("⚙️ Paramètres", "tab_settings"),  # ← Ajouter ceci
]
```

### **3. Dans AuraApp.__init__(), après les autres services:**
```python
# RAG Service
self.rag = RAGService()
# self.rag.index_folder("data/documents")  # Si vous avez des docs

# LLM Manager
self.llm_manager = LLMManager()
self.llm_manager.setup_ollama(OLLAMA_BASE_URL, OLLAMA_MODEL)
# Groq sera configuré par l'utilisateur dans Settings
```

### **4. Dans la boucle de création de pages (après les autres):**
```python
# Après les autres pages...
elif name == "tab_settings":
    build_settings_page(self, self.pages[name])
    # Attacher les fonctions:
    self.test_ollama_connection = lambda: test_ollama_connection(self)
    self.test_groq_connection = lambda: test_groq_connection(self)
    self.save_llm_config = lambda: save_llm_config(self)
    self.reset_llm_config = lambda: reset_llm_config(self)
```

### **5. Mettre à jour page_titles() pour inclure Settings:**
```python
def page_titles(self):
    return {
        # ... existants ...
        "tab_settings": "Paramètres du système",
    }
```

---

## 🧪 TESTER LES SERVICES

### **Tester Ollama:**
```bash
# En terminal
curl http://127.0.0.1:11434/api/tags

# Ou dans AURA → Paramètres → "🔍 Tester Ollama"
```

### **Tester Groq:**
- Lancez AURA (après intégration)
- Allez dans Paramètres
- Entrez votre clé API Groq
- Cliquez "🔍 Tester Groq API"
- Vous devriez voir ✅ "Groq API est active!"

### **Tester RAG:**
```python
from src.rag_service import RAGService

rag = RAGService()
rag.index_folder("data/documents")  # Vos manuels ici

results = rag.retrieve("TRS", top_k=3)
for r in results:
    print(f"Source: {r['metadata']['source']} ({r['score']:.0%})")
    print(r['text'][:100] + "...")
```

---

## 💡 CAS D'USAGE

### **Scénario 1: Utilisateur demande "Qu'est-ce que le TRS?"**

1. **AURA recherche dans RAG** (manuels indexés)
2. **Récupère 3 meilleurs documents**
3. **Les passe au LLM** (Ollama ou Groq)
4. **LLM génère réponse basée sur les docs**
5. **Réponse citée avec sources!** ✅

### **Scénario 2: LLM Ollama timeout**

1. **Essaie Groq API automatiquement**
2. **Si Groq OK** → réponse de Groq
3. **Si les deux échouent** → message d'erreur
4. **User configure dans Paramètres** (page settings)

---

## 🎯 À RETENIR

| Élément | Où | Comment |
|---------|-----|--------|
| **API Key Groq** | Paramètres → "☁️ Groq API" | Coller clé `gsk_...` |
| **Obtenir clé** | https://console.groq.com | Signup gratuit |
| **Tester Groq** | Paramètres → "🔍 Tester" | Vert = OK, Rouge = Erreur |
| **Indexer docs** | `rag.index_folder()` | PDF/DOCX/TXT supportés |
| **Choisir LLM** | Paramètres → Provider | Ollama ou Groq |
| **Voir sources** | Réponses RAG | Automatiquement citées |

---

## 📚 FICHIERS À LIRE

1. **`GROQ_SETUP.md`** ← **LIRE CECI EN PREMIER!** 
   - Guide complet pour clé API gratuite
   
2. **`RAG_LLM_IMPLEMENTATION.md`**
   - Documentation technique complète
   - Architecture détaillée
   - Exemples de code

3. **Code dans `src/`**:
   - `rag_service.py` - Service RAG principal
   - `llm_manager.py` - Gestion multi-LLM
   - `settings_page.py` - UI paramètres

---

## ❓ FAQ

**Q: Est-ce que Groq est vraiment gratuit?**
A: Oui, complètement gratuit avec limites de débit. Suffisant pour tests.

**Q: Dois-je utiliser Groq ou Ollama?**
A: 
- **Ollama**: Local, aucune limite, pas Internet
- **Groq**: Cloud, gratuit, performant, nécessite Internet

**Q: Peut-je utiliser les deux?**
A: Oui! AURA bascule automatiquement si l'un échoue.

**Q: Comment indexer mes documents?**
A: `rag.index_folder("data/documents")` avant de lancer AURA

**Q: Où vont les clés API?**
A: Sécurisées dans fichier `.env` (non pushé sur GitHub)

---

## ✅ CHECKLIST FINAL

- [ ] **Lire `GROQ_SETUP.md`** pour comprendre Groq
- [ ] **S'inscrire sur Groq** (https://console.groq.com)
- [ ] **Obtenir clé API**
- [ ] **Intégrer 5 étapes ci-dessus** dans gui.py
- [ ] **Lancer AURA**
- [ ] **Aller dans Paramètres**
- [ ] **Tester Ollama** (doit être vert)
- [ ] **Ajouter clé Groq** et tester
- [ ] **Indexer documents RAG** (optionnel)
- [ ] **Utiliser dans Prompt/NLP pages**

---

**Bon travail! 🚀 Vous avez maintenant RAG + Multi-LLM prêt à intégrer!**

Questions? Voir `RAG_LLM_IMPLEMENTATION.md` pour plus de détails.
