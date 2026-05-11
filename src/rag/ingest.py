"""Ingestion et prétraitement des documents pour le RAG."""
import os
import PyPDF2
from typing import List, Tuple
from docx import Document


class DocumentIngestor:
    """Ingère et prépare les documents pour le RAG."""
    
    def __init__(self, chunk_size: int = 256, overlap: int = 50):
        """Initialiser l'ingérer.
        
        Args:
            chunk_size: Taille des chunks en tokens (approximativement)
            overlap: Nombre de tokens de chevauchement entre chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def ingest_pdf(self, filepath: str) -> List[Tuple[str, dict]]:
        """Ingérer un fichier PDF.
        
        Args:
            filepath: Chemin du fichier PDF
            
        Returns:
            Liste de tuples (texte_chunk, métadonnées)
        """
        chunks = []
        try:
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        page_chunks = self._chunk_text(text)
                        for chunk_idx, chunk in enumerate(page_chunks):
                            chunks.append((
                                chunk,
                                {
                                    "source": os.path.basename(filepath),
                                    "type": "PDF",
                                    "page": page_num + 1,
                                    "chunk": chunk_idx
                                }
                            ))
        except Exception as e:
            print(f"Erreur lors de l'ingestion PDF {filepath}: {e}")
        
        return chunks
    
    def ingest_docx(self, filepath: str) -> List[Tuple[str, dict]]:
        """Ingérer un fichier DOCX.
        
        Args:
            filepath: Chemin du fichier DOCX
            
        Returns:
            Liste de tuples (texte_chunk, métadonnées)
        """
        chunks = []
        try:
            doc = Document(filepath)
            text = "\n".join([para.text for para in doc.paragraphs])
            page_chunks = self._chunk_text(text)
            for chunk_idx, chunk in enumerate(page_chunks):
                chunks.append((
                    chunk,
                    {
                        "source": os.path.basename(filepath),
                        "type": "DOCX",
                        "chunk": chunk_idx
                    }
                ))
        except Exception as e:
            print(f"Erreur lors de l'ingestion DOCX {filepath}: {e}")
        
        return chunks
    
    def ingest_txt(self, filepath: str) -> List[Tuple[str, dict]]:
        """Ingérer un fichier texte.
        
        Args:
            filepath: Chemin du fichier TXT
            
        Returns:
            Liste de tuples (texte_chunk, métadonnées)
        """
        chunks = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            page_chunks = self._chunk_text(text)
            for chunk_idx, chunk in enumerate(page_chunks):
                chunks.append((
                    chunk,
                    {
                        "source": os.path.basename(filepath),
                        "type": "TXT",
                        "chunk": chunk_idx
                    }
                ))
        except Exception as e:
            print(f"Erreur lors de l'ingestion TXT {filepath}: {e}")
        
        return chunks
    
    def ingest_folder(self, folder_path: str) -> List[Tuple[str, dict]]:
        """Ingérer tous les documents d'un dossier.
        
        Args:
            folder_path: Chemin du dossier
            
        Returns:
            Liste de tuples (texte_chunk, métadonnées)
        """
        all_chunks = []
        supported_extensions = {
            ".pdf": self.ingest_pdf,
            ".docx": self.ingest_docx,
            ".txt": self.ingest_txt
        }
        
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath):
                ext = os.path.splitext(filename)[1].lower()
                if ext in supported_extensions:
                    print(f"Ingestion: {filename}")
                    chunks = supported_extensions[ext](filepath)
                    all_chunks.extend(chunks)
        
        return all_chunks
    
    def _chunk_text(self, text: str) -> List[str]:
        """Découper le texte en chunks chevauchés.
        
        Args:
            text: Texte à découper
            
        Returns:
            Liste des chunks
        """
        # Découper par phrases pour préserver le contexte
        sentences = text.replace("\n", " ").split(". ")
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_words = len(sentence.split())
            if current_size + sentence_words > self.chunk_size:
                if current_chunk:
                    chunks.append(". ".join(current_chunk) + ".")
                current_chunk = [sentence]
                current_size = sentence_words
            else:
                current_chunk.append(sentence)
                current_size += sentence_words
        
        if current_chunk:
            chunks.append(". ".join(current_chunk) + ".")
        
        return [c for c in chunks if len(c.split()) > 5]  # Filtrer les chunks vides
