# 🚀 Guide Groq API - Configuration AURA

## Qu'est-ce que Groq?

**Groq** est un fournisseur de LLM cloud **gratuit** qui offre :
- ✅ API gratuite sans carte de crédit nécessaire
- ✅ Modèles haute performance (Mixtral, LLama2, Gemma)
- ✅ Parfait pour développement et tests
- ✅ Fallback automatique si Ollama n'est pas disponible

## 📋 Étapes pour obtenir une clé API Groq

### 1️⃣ Créer un compte Groq

1. Allez sur **https://console.groq.com**
2. Cliquez sur **"Sign Up"**
3. Remplissez le formulaire (email, mot de passe)
4. Confirmez votre email

### 2️⃣ Créer une clé API

1. Connectez-vous à votre compte Groq
2. Allez dans **"API Keys"** ou **"Settings"**
3. Cliquez sur **"Create API Key"**
4. Nommez-la (ex: "AURA-Key")
5. **Copiez la clé** (elle n'apparaîtra qu'une fois!)

### 3️⃣ Ajouter la clé dans AURA

#### Méthode 1: Via l'interface (Recommandé)

1. Lancez AURA
2. Allez dans **⚙️ Paramètres** (barre de navigation)
3. Collez votre clé API Groq dans le champ **"Clé API Groq"**
4. Cliquez **"🔍 Tester Groq API"** pour vérifier
5. Cliquez **"💾 Enregistrer Configuration"**

#### Méthode 2: Via fichier .env (Avancé)

Créez un fichier `.env` à la racine du projet :

```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxx
GROQ_MODEL=mixtral-8x7b-32768
LLM_PRIMARY_PROVIDER=groq
```

## ✅ Vérifier la configuration

1. Ouvrez **Paramètres** dans AURA
2. Cliquez **"🔍 Tester Groq API"**
3. Vous devriez voir : **"✅ Groq API est active!"**

## 🎯 Modèles disponibles

| Modèle | Performance | Vitesse | Contexte |
|--------|-------------|---------|----------|
| **mixtral-8x7b-32768** | Très bon | Rapide | 32K tokens |
| **llama2-70b-4096** | Excellent | Rapide | 4K tokens |
| **gemma-7b-it** | Bon | Très rapide | 8K tokens |

## ⚡ Fonctionnement par défaut

AURA utilise cette logique :

1. **Essaie Ollama local** (http://127.0.0.1:11434)
2. **Si Ollama ne répond pas** → Essaie Groq API
3. **Si les deux échouent** → Message d'erreur

Vous pouvez changer la préférence dans **Paramètres**.

## 🚫 Dépannage

### "❌ Clé API invalide"
- ✓ Vérifiez que vous avez copié toute la clé
- ✓ La clé doit commencer par `gsk_`
- ✓ Vérifiez votre compte Groq est actif

### "❌ Groq ne répond pas"
- ✓ Vérifiez votre connexion internet
- ✓ Vérifiez que la clé API est correcte
- ✓ Groq peut avoir des limites (utilisez Ollama pour l'instant)

### Pas de réponse du LLM
- ✓ Vérifiez que Ollama OU Groq est configuré
- ✓ Utilisez l'onglet **Paramètres** pour tester la connexion

## 💡 Conseils

- **Développement**: Utilisez Ollama (local, aucune limite)
- **Tests cloud**: Utilisez Groq (gratuit, performant)
- **Production**: Envisagez un compte payant OpenAI/Anthropic

## 🔗 Ressources

- **Console Groq**: https://console.groq.com
- **Docs Groq**: https://console.groq.com/docs
- **Ollama**: https://ollama.ai (pour LLM local)
