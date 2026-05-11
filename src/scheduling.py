class TaskScheduler:
    def __init__(self):
        self.technicians = [
            {"nom": "Ahmed", "competences": ["Maintenance", "Instrumentation"], "disponible": True, "charge": 1},
            {"nom": "Sarah", "competences": ["Électrique", "Automatisme"], "disponible": True, "charge": 0},
            {"nom": "Karim", "competences": ["Maintenance", "Électrique"], "disponible": False, "charge": 3},
            {"nom": "Youssef", "competences": ["Instrumentation", "Maintenance", "Automatisme"], "disponible": True, "charge": 2}
        ]
        
    def assign_task(self, task_name, required_skill, urgency):
        """
        Algorithme d'optimisation: sélectionne le technicien disponible, 
        possédant la compétence requise, ayant la charge de travail la plus faible.
        """
        available_techs = [t for t in self.technicians if t["disponible"] and required_skill in t["competences"]]
        
        if not available_techs:
            return {"tache": task_name, "assigne_a": "Aucun (En attente)", "urgence": urgency, "statut": "Échec"}
            
        available_techs.sort(key=lambda x: x["charge"])
        assigned_tech = available_techs[0]
        assigned_tech["charge"] += 1
        
        return {"tache": task_name, "assigne_a": assigned_tech["nom"], "urgence": urgency, "statut": "Assigné"}

    def get_all_technicians(self):
        return self.technicians
