"""Gestion des embeddings pour le RAG."""
import json
from typing import List, Tuple
from sentence_transformers import SentenceTransformer


class EmbeddingsManager:
    """Génère et gère les embeddings pour les documents."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialiser le gestionnaire d'embeddings.
        
        Args:
            model_name: Nom du modèle sentence-transformers à utiliser
        """
        self.model = SentenceTransformer(model_name)
        self.documents = []
        self.embeddings = []
    
    def add_document(self, text: str, metadata: dict = None) -> None:
        """Ajouter un document et générer son embedding.
        
        Args:
            text: Contenu du document
            metadata: Métadonnées (source, date, type, etc.)
        """
        if not text or not text.strip():
            return
        
        embedding = self.model.encode(text)
        self.documents.append({
            "text": text,
            "metadata": metadata or {},
            "embedding": embedding.tolist()
        })
    
    def add_documents(self, documents: List[Tuple[str, dict]]) -> None:
        """Ajouter plusieurs documents.
        
        Args:
            documents: Liste de tuples (texte, métadonnées)
        """
        for text, metadata in documents:
            self.add_document(text, metadata)
    
    def search(self, query: str, top_k: int = 3) -> List[dict]:
        """Rechercher les documents les plus similaires à la requête.
        
        Args:
            query: Requête de recherche
            top_k: Nombre de résultats à retourner
            
        Returns:
            Liste des documents les plus similaires avec scores
        """
        if not self.documents:
            return []
        
        query_embedding = self.model.encode(query)
        
        # Calculer les scores de similarité cosinus
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = []
        for doc in self.documents:
            score = cosine_similarity(
                [query_embedding],
                [doc["embedding"]]
            )[0][0]
            similarities.append((score, doc))
        
        # Trier par score décroissant et retourner top_k
        similarities.sort(key=lambda x: x[0], reverse=True)
        results = [
            {
                "text": doc["text"],
                "metadata": doc["metadata"],
                "score": float(score)
            }
            for score, doc in similarities[:top_k]
        ]
        return results
    
    def save_to_file(self, filepath: str) -> None:
        """Sauvegarder les embeddings et documents.
        
        Args:
            filepath: Chemin du fichier de sauvegarde
        """
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filepath: str) -> None:
        """Charger les embeddings et documents.
        
        Args:
            filepath: Chemin du fichier à charger
        """
        with open(filepath, "r", encoding="utf-8") as f:
            self.documents = json.load(f)
    
    def clear(self) -> None:
        """Effacer tous les documents et embeddings."""
        self.documents = []
        self.embeddings = []
