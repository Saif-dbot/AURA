class MaintenancePlanner:
    def __init__(self):
        pass
        
    def performance_gap_analysis(self, real_production, theoretical_capacity):
        gap = theoretical_capacity - real_production
        trs = (real_production / theoretical_capacity) * 100 if theoretical_capacity > 0 else 0
        return {
            "TRS": round(trs, 2),
            "Ecart_Production": gap,
            "Statut": "Critique" if trs < 80 else ("Acceptable" if trs < 90 else "Optimal")
        }
        
    def generate_roadmap(self, nlp_history=None):
        """
        Génère un plan d'investissement sur 3 ans dynamique basé sur l'IA.
        """
        roadmap = []
        if nlp_history and any("capteur" in str(h).lower() or "alarme" in str(h).lower() for h in nlp_history):
            roadmap.append({"Année": "Année 1", "Action": "Fiabilisation du réseau de capteurs et des seuils d'alerte", "Budget Estimé": "35 000 EUR"})
            roadmap.append({"Année": "Année 2", "Action": "Renforcement du suivi conditionnel des actifs critiques", "Budget Estimé": "45 000 EUR"})
            roadmap.append({"Année": "Année 3", "Action": "Déploiement d'un monitoring prédictif élargi", "Budget Estimé": "80 000 EUR"})
        elif nlp_history and any("ligne" in str(h).lower() or "production" in str(h).lower() for h in nlp_history):
            roadmap.append({"Année": "Année 1", "Action": "Sécurisation des lignes de production prioritaires", "Budget Estimé": "50 000 EUR"})
            roadmap.append({"Année": "Année 2", "Action": "Optimisation des fenêtres d'arrêt et des interventions", "Budget Estimé": "35 000 EUR"})
            roadmap.append({"Année": "Année 3", "Action": "Automatisation de la collecte des données d'exploitation", "Budget Estimé": "60 000 EUR"})
        else:
            roadmap.append({"Année": "Année 1", "Action": "Cartographie des actifs critiques et priorisation des risques", "Budget Estimé": "40 000 EUR"})
            roadmap.append({"Année": "Année 2", "Action": "Plan de fiabilisation basé sur les historiques d'intervention", "Budget Estimé": "35 000 EUR"})
            roadmap.append({"Année": "Année 3", "Action": "Extension du pilotage prédictif à l'ensemble du site", "Budget Estimé": "80 000 EUR"})
        return roadmap
