class PromptGenerator:
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
        self.history = {
            "actif": "Procédure standard: sécuriser la zone, isoler l'actif, vérifier les journaux d'alarme, contrôler les capteurs associés, appliquer les étapes de remise en service et valider les indicateurs de fonctionnement.",
            "capteur": "Procédure standard: vérifier l'alimentation, les connectiques, la calibration, les seuils de déclenchement et la cohérence des mesures avant remise en production.",
            "ligne": "Procédure standard: coordonner l'arrêt technique, isoler la ligne, notifier les équipes, réaliser le contrôle visuel et fonctionnel, puis relancer selon la procédure de redémarrage.",
            "automate": "Procédure standard: sauvegarder la configuration, vérifier les E/S, contrôler les alarmes, tester les séquences et valider le retour au régime nominal."
        }
        
    def _fallback_prompt(self, query):
        query_lower = query.lower()
        response = ""
        
        found = False
        for key, instruction in self.history.items():
            if key in query_lower:
                response += f"--- Instruction de Maintenance ({key.upper()}) ---\n{instruction}\n\nRecommandation: Suivre strictement la procédure LOTO (Lockout/Tagout).\n"
                found = True
                
        if not found:
            response = f"Aucune procédure spécifique trouvée pour la requête : '{query}'.\nVeuillez préciser l'actif, la ligne, le capteur ou l'automate concerné."
            
        return response.strip()

    def generate_prompt(self, query):
        """
        Utilise Ollama local si disponible, sinon fallback sur règles locales.
        """
        if self.llm_service:
            hints = "\n".join([f"- {k}: {v}" for k, v in self.history.items()])
            llm_response = self.llm_service.generate_maintenance_instruction(query=query, knowledge_hints=hints)
            if llm_response:
                return {"text": llm_response, "source": "ollama"}

        return {"text": self._fallback_prompt(query), "source": "fallback"}

    def export_to_pdf(self, response_text, filepath):
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            c = canvas.Canvas(filepath, pagesize=letter)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, 750, "Fiche d'Intervention - AURA")
            
            c.setFont("Helvetica", 11)
            y = 710
            for line in response_text.split('\n'):
                c.drawString(50, y, line)
                y -= 20
                if y < 50:
                    c.showPage()
                    c.setFont("Helvetica", 11)
                    y = 750
            c.save()
            return True
        except ImportError:
            return False
