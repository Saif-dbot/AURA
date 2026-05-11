try:
    import spacy
except ImportError:
    spacy = None

try:
    from sentence_transformers import SentenceTransformer, util
except ImportError:
    SentenceTransformer, util = None, None

import re
import os
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import docx
except ImportError:
    docx = None

class NLPEngine:
    def __init__(self):
        # Graceful loading of spacy
        self.nlp = None
        if spacy:
            try:
                self.nlp = spacy.load("fr_core_news_md")
            except:
                pass
            
        self.model = None
        if SentenceTransformer:
            try:
                self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            except:
                pass
            
        self.knowledge_base = [
            "Dégradation progressive d'un actif critique détectée par hausse de vibrations et de température",
            "Défaillance d'un capteur de process causée par une perte de calibration",
            "Dérive d'un automate provoquant des arrêts intermittents de ligne",
            "Incident électrique lié à un défaut d'isolement dans l'armoire de commande",
            "Perte de performance d'une ligne de production suite à une alarme récurrente"
        ]
        if self.model:
            self.kb_embeddings = self.model.encode(self.knowledge_base)
            
        self.rca_history = []

    def add_to_knowledge_base(self, new_cause):
        """Ajoute une nouvelle panne (apprentissage continu)"""
        if new_cause and new_cause not in self.knowledge_base:
            self.knowledge_base.append(new_cause)
            if self.model:
                self.kb_embeddings = self.model.encode(self.knowledge_base)
            return True
        return False

    def parse_document(self, file_path):
        text = ""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf" and PyPDF2:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        elif ext == ".docx" and docx:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        return text

    def extract_manual_data(self, file_path_or_text):
        """
        Extrait des données des manuels machines.
        """
        if os.path.isfile(file_path_or_text):
            text = self.parse_document(file_path_or_text)
        else:
            text = file_path_or_text
            
        data = {
            'composants_critiques': [],
            'frequences_lubrification': [],
            'seuils_alerte': []
        }
        
        if not text:
            return data
            
        # Extraction par règles et IA (Spacy)
        if self.nlp:
            # Utilisation de Spacy pour l'analyse linguistique
            doc = self.nlp(text[:100000]) # Limit length for performance
            for chunk in doc.noun_chunks:
                text_lower = chunk.text.lower()
                if "actif" in text_lower or "ligne" in text_lower or "capteur" in text_lower or "automate" in text_lower or "production" in text_lower:
                    data['composants_critiques'].append(chunk.text)
        else:
            # Fallback Regex si Spacy n'est pas chargé
            if re.search(r"actif|asset", text, re.IGNORECASE):
                data['composants_critiques'].append("Actif critique")
            if re.search(r"ligne|production", text, re.IGNORECASE):
                data['composants_critiques'].append("Ligne de production")
            if re.search(r"capteur|sensor", text, re.IGNORECASE):
                data['composants_critiques'].append("Capteur de process")
            if re.search(r"automate|plc", text, re.IGNORECASE):
                data['composants_critiques'].append("Automate")
                
        # Nettoyage des doublons pour les composants critiques
        data['composants_critiques'] = list(set([c.strip().capitalize() for c in data['composants_critiques']]))
        
        lub_matches = re.findall(r'lubrification.*?(\d+\s*(?:heures|jours|mois|h|j))', text, re.IGNORECASE)
        if lub_matches:
            data['frequences_lubrification'] = list(set(lub_matches))
        
        temp_matches = re.findall(r'(?:température|pression).*?(?:>|supérieur à|max|maximal)\s*(\d+\s*(?:°C|bar|psi))', text, re.IGNORECASE)
        if temp_matches:
            data['seuils_alerte'] = list(set(temp_matches))
        
        return data

    def root_cause_analysis(self, report_text):
        """
        Analyse sémantique des rapports d'intervention pour identifier les causes racines.
        """
        if not self.model:
            return "Modèle NLP non chargé. (Installez spacy et sentence-transformers)"
            
        query_embedding = self.model.encode([report_text])
        cos_scores = util.cos_sim(query_embedding, self.kb_embeddings)[0]
        
        best_match_idx = cos_scores.argmax().item()
        confidence = cos_scores[best_match_idx].item()
        
        if confidence > 0.4:
            cause = self.knowledge_base[best_match_idx]
            self.rca_history.append(cause)
            return {
                "cause_racine": cause,
                "confiance": round(confidence * 100, 2)
            }
        else:
            return {
                "cause_racine": "Cause non identifiée dans la base de connaissances",
                "confiance": round(confidence * 100, 2)
            }
