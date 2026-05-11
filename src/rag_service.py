"""Service RAG (Retrieval Augmented Generation) pour AURA."""
import os
from typing import List, Tuple
from src.rag.embeddings import EmbeddingsManager
from src.rag.ingest import DocumentIngestor


class RAGService:
    """Service RAG pour recherche documentaire et génération de contexte."""
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        """Initialiser le service RAG.
        
        Args:
            embedding_model: Modèle d'embeddings à utiliser
        """
        self.embeddings_manager = EmbeddingsManager(embedding_model)
        self.ingestor = DocumentIngestor(chunk_size=256, overlap=50)
        self.indexed = False
    
    def index_documents(self, documents: List[Tuple[str, dict]]) -> None:
        """Indexer une liste de documents.
        
        Args:
            documents: Liste de tuples (texte, métadonnées)
        """
        self.embeddings_manager.add_documents(documents)
        self.indexed = True
    
    def index_folder(self, folder_path: str) -> int:
        """Indexer tous les documents d'un dossier.
        
        Args:
            folder_path: Chemin du dossier
            
        Returns:
            Nombre de chunks indexés
        """
        if not os.path.isdir(folder_path):
            return 0
        
        documents = self.ingestor.ingest_folder(folder_path)
        self.index_documents(documents)
        return len(documents)
    
    def retrieve(self, query: str, top_k: int = 3) -> List[dict]:
        """Récupérer les documents les plus pertinents pour une requête.
        
        Args:
            query: Requête utilisateur
            top_k: Nombre de résultats à retourner
            
        Returns:
            Liste des documents pertinents avec scores
        """
        if not self.indexed or not self.embeddings_manager.documents:
            return []
        
        return self.embeddings_manager.search(query, top_k)
    
    def build_context(self, query: str, top_k: int = 3) -> str:
        """Construire un contexte pour le LLM basé sur les documents.
        
        Args:
            query: Requête utilisateur
            top_k: Nombre de documents à récupérer
            
        Returns:
            Contexte formaté pour le LLM
        """
        results = self.retrieve(query, top_k)
        if not results:
            return ""
        
        context = "## CONTEXTE DOCUMENTAIRE\n"
        for idx, result in enumerate(results, 1):
            source = result["metadata"].get("source", "Inconnu")
            page = result["metadata"].get("page", "")
            page_str = f" (page {page})" if page else ""
            context += f"\n### Document {idx} - {source}{page_str}\n"
            context += f"**Pertinence: {result['score']:.2%}**\n"
            context += f"{result['text']}\n"
        
        return context
    
    def augmented_prompt(self, user_query: str, system_prompt: str = "", top_k: int = 3) -> str:
        """Générer un prompt augmenté avec le contexte documentaire.
        
        Args:
            user_query: Question de l'utilisateur
            system_prompt: Prompt système optionnel
            top_k: Nombre de documents à récupérer
            
        Returns:
            Prompt complet augmenté
        """
        context = self.build_context(user_query, top_k)
        
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{context}\n\nQuestion: {user_query}"
        else:
            full_prompt = f"{context}\n\nQuestion: {user_query}"
        
        return full_prompt
    
    def get_sources(self, query: str, top_k: int = 3) -> List[str]:
        """Récupérer les sources documentaires citées.
        
        Args:
            query: Requête
            top_k: Nombre de résultats
            
        Returns:
            Liste des sources
        """
        results = self.retrieve(query, top_k)
        sources = set()
        for result in results:
            source = result["metadata"].get("source", "Inconnu")
            sources.add(source)
        return sorted(list(sources))
    
    def clear(self) -> None:
        """Effacer l'index."""
        self.embeddings_manager.clear()
        self.indexed = False
    
    def get_stats(self) -> dict:
        """Obtenir les statistiques d'indexation.
        
        Returns:
            Dict avec nombre de documents et chunks
        """
        return {
            "indexed": self.indexed,
            "document_count": len(self.embeddings_manager.documents),
            "model": self.embeddings_manager.model.get_sentence_embedding_dimension()
        }
