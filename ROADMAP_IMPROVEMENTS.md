# AURA - Roadmap d'Amélioration

## Vision
AURA évolue d'un prototype desktop vers une application locale d'aide à la maintenance, centrée sur la traçabilité, l'assistance décisionnelle et la génération d'instructions techniques.

## Ce qui est déjà en place
- Base SQLite et journalisation locale.
- Interface desktop Tkinter/ttk avec navigation par pages.
- RAG local pour indexer et rechercher les documents techniques.
- Support multi-LLM avec priorité configurable.
- Configuration utilisateur via `.env` et page Paramètres.

## Priorités
1. **Stabiliser le socle** : imports, configuration, logs, erreurs.
2. **RAG + LLM** : interroger les manuels, historiques et procédures locales.
3. **Généraliser le métier** : services réutilisables, moins de logique dispersée.
4. **Renforcer la persistance** : historique, rapports, audit.
5. **Fiabiliser l'UI desktop** : cohérence visuelle, ergonomie, navigation.
6. **Préparer le déploiement** : tests, packaging Windows, documentation.

## Phase 1 — Fondations backend
### Base de données
- Garder SQLite comme base locale par défaut.
- Compléter l'historique des interventions avec timestamps.
- Ajouter le CRUD des rapports et pièces jointes.

### Configuration
- Centraliser les variables d'environnement.
- Garder `.env` pour les secrets et les chemins locaux.
- Uniformiser les accès aux configs entre base, LLM et UI.

## Phase 2 — IA, RAG et LLM
### RAG
- Indexer les PDF, DOCX, TXT et dossiers de documentation.
- Découper proprement les contenus en chunks.
- Calculer les embeddings et faire la recherche sémantique.
- Citer les sources dans les réponses.

### LLM
- Garder Mistral comme alternative cloud principale.
- Garder Ollama seulement si le service local est réellement disponible.
- Conserver le fallback automatique entre providers.
- Permettre à l'utilisateur de choisir le provider par défaut.

## Phase 3 — UI desktop
- Garder Tkinter/ttk comme base.
- Consolider les composants réutilisables.
- Améliorer les formulaires, les cartes et la lisibilité.
- Ajouter une vraie vue Paramètres pour les services IA.

## Phase 4 — API et services
- Préparer une API REST si le besoin métier le justifie.
- Séparer clairement les routes, schémas et services.
- Ajouter validation, pagination et authentification si l'API sort du cadre local.

## Phase 5 — Tests et déploiement
- Ajouter des tests unitaires sur les services critiques.
- Vérifier les chemins, imports et connexions réseau.
- Préparer un build Windows avec PyInstaller.
- Documenter l'installation et l'utilisation locale.

## Quick wins
- RAG minimal sur les manuels locaux.
- LLM local ou cloud avec fallback.
- Export PDF des rapports.
- Amélioration du thème desktop.
- Authentification simple si nécessaire.

## Fichiers noyau à conserver
- `src/gui.py`
- `src/rag_service.py`
- `src/rag/`
- `src/llm_manager.py`
- `src/llm_service.py`
- `src/settings_page.py`
- `src/database/connection.py`

## Prochaine étape immédiate
1. Nettoyer les fichiers de démo et les documents redondants.
2. Pousser uniquement le code utile.
3. Garder la clé API hors du dépôt.
