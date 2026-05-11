"""Page de paramètres et configuration pour AURA."""
import tkinter as tk
from tkinter import ttk, messagebox


def build_settings_page(self, page):
    """Construire la page de paramètres LLM et RAG."""
    page.grid_columnconfigure(0, weight=1)
    page.grid_rowconfigure(1, weight=1)
    
    # Titre
    header = self.create_card(page, "Configuration du système", "Paramètres LLM, RAG et intégrations")
    header.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 16))
    tk.Label(
        header,
        text="Configurez les clés API, préférences LLM et chemins de documents",
        bg="#F8F9FA",
        fg="#333",
        font=("Segoe UI", 11)
    ).pack(anchor="w", padx=20, pady=(0, 14))
    
    # Contenu dans un scrollable frame
    content_card = self.create_card(page, "Paramètres LLM", "Configurez Ollama et Groq API")
    content_card.grid(row=1, column=0, sticky="nsew")
    content_frame = tk.Frame(content_card, bg="#FFFFFF")
    content_frame.pack(fill="both", expand=True, padx=20, pady=16)
    
    # ===== OLLAMA =====
    ollama_frame = tk.Frame(content_frame, bg="#FFFFFF")
    ollama_frame.pack(fill="x", pady=(0, 20))
    tk.Label(
        ollama_frame,
        text="📍 Ollama (LLM Local)",
        bg="#FFFFFF",
        fg="#2C3E50",
        font=("Segoe UI", 12, "bold")
    ).pack(anchor="w", pady=(0, 8))
    
    sub_frame = tk.Frame(ollama_frame, bg="#F8F9FA")
    sub_frame.pack(fill="x", padx=12, pady=(0, 8))
    
    tk.Label(sub_frame, text="URL Ollama:", bg="#F8F9FA", font=("Segoe UI", 10)).pack(anchor="w", padx=8, pady=4)
    self.ent_ollama_url = ttk.Entry(sub_frame, width=50)
    self.ent_ollama_url.insert(0, "http://127.0.0.1:11434")
    self.ent_ollama_url.pack(anchor="w", padx=8, pady=4, fill="x")
    
    tk.Label(sub_frame, text="Modèle Ollama:", bg="#F8F9FA", font=("Segoe UI", 10)).pack(anchor="w", padx=8, pady=4)
    self.ent_ollama_model = ttk.Entry(sub_frame, width=50)
    self.ent_ollama_model.insert(0, "llama3.1:8b")
    self.ent_ollama_model.pack(anchor="w", padx=8, pady=4, fill="x")
    
    test_button = ttk.Button(
        sub_frame,
        text="🔍 Tester Ollama",
        command=self.test_ollama_connection
    )
    test_button.pack(anchor="w", padx=8, pady=8)
    self.lbl_ollama_status = tk.Label(sub_frame, text="", bg="#F8F9FA", fg="#27AE60", font=("Segoe UI", 9))
    self.lbl_ollama_status.pack(anchor="w", padx=8)
    
    # ===== GROQ API =====
    groq_frame = tk.Frame(content_frame, bg="#FFFFFF")
    groq_frame.pack(fill="x", pady=(0, 20))
    tk.Label(
        groq_frame,
        text="☁️  Groq API (LLM Cloud - Gratuit)",
        bg="#FFFFFF",
        fg="#2C3E50",
        font=("Segoe UI", 12, "bold")
    ).pack(anchor="w", pady=(0, 8))
    
    sub_frame = tk.Frame(groq_frame, bg="#F8F9FA")
    sub_frame.pack(fill="x", padx=12, pady=(0, 8))
    
    info_text = tk.Label(
        sub_frame,
        text="Inscription gratuite: https://console.groq.com\nLimites: Assez pour développement/tests",
        bg="#F8F9FA",
        fg="#7F8C8D",
        font=("Segoe UI", 9),
        justify="left"
    )
    info_text.pack(anchor="w", padx=8, pady=(0, 8))
    
    tk.Label(sub_frame, text="Clé API Groq:", bg="#F8F9FA", font=("Segoe UI", 10)).pack(anchor="w", padx=8, pady=4)
    self.ent_groq_key = ttk.Entry(sub_frame, width=50, show="*")
    self.ent_groq_key.pack(anchor="w", padx=8, pady=4, fill="x")
    
    tk.Label(sub_frame, text="Modèle Groq:", bg="#F8F9FA", font=("Segoe UI", 10)).pack(anchor="w", padx=8, pady=4)
    self.cmb_groq_model = ttk.Combobox(
        sub_frame,
        values=["mixtral-8x7b-32768", "llama2-70b-4096", "gemma-7b-it"],
        state="readonly"
    )
    self.cmb_groq_model.set("mixtral-8x7b-32768")
    self.cmb_groq_model.pack(anchor="w", padx=8, pady=4, fill="x")
    
    test_button = ttk.Button(
        sub_frame,
        text="🔍 Tester Groq API",
        command=self.test_groq_connection
    )
    test_button.pack(anchor="w", padx=8, pady=8)
    self.lbl_groq_status = tk.Label(sub_frame, text="", bg="#F8F9FA", fg="#E74C3C", font=("Segoe UI", 9))
    self.lbl_groq_status.pack(anchor="w", padx=8)
    
    # ===== LLM PRÉFÉRENCE =====
    pref_frame = tk.Frame(content_frame, bg="#FFFFFF")
    pref_frame.pack(fill="x", pady=(0, 20))
    tk.Label(
        pref_frame,
        text="Préférence LLM par défaut",
        bg="#FFFFFF",
        fg="#2C3E50",
        font=("Segoe UI", 12, "bold")
    ).pack(anchor="w", pady=(0, 8))
    
    sub_frame = tk.Frame(pref_frame, bg="#F8F9FA")
    sub_frame.pack(fill="x", padx=12, pady=(0, 8))
    
    tk.Label(sub_frame, text="Provider:", bg="#F8F9FA", font=("Segoe UI", 10)).pack(anchor="w", padx=8, pady=4)
    self.cmb_llm_prov = ttk.Combobox(
        sub_frame,
        values=["ollama", "groq"],
        state="readonly"
    )
    self.cmb_llm_prov.set("ollama")
    self.cmb_llm_prov.pack(anchor="w", padx=8, pady=4, fill="x")
    
    # Boutons d'action
    button_frame = tk.Frame(content_frame, bg="#FFFFFF")
    button_frame.pack(fill="x", pady=(16, 0))
    
    ttk.Button(
        button_frame,
        text="💾 Enregistrer Configuration",
        command=self.save_llm_config
    ).pack(side="left", padx=(0, 8))
    
    ttk.Button(
        button_frame,
        text="🔄 Réinitialiser",
        command=self.reset_llm_config
    ).pack(side="left")
    
    self.lbl_config_status = tk.Label(button_frame, text="", bg="#FFFFFF", fg="#27AE60", font=("Segoe UI", 10, "bold"))
    self.lbl_config_status.pack(side="right", padx=8)


def test_ollama_connection(self):
    """Tester la connexion à Ollama."""
    url = self.ent_ollama_url.get().strip()
    if not url:
        self.lbl_ollama_status.config(text="❌ URL manquante", fg="#E74C3C")
        return
    
    self.set_status("Test Ollama en cours...")
    self.lbl_ollama_status.config(text="Vérification...", fg="#3498DB")
    self.update()
    
    try:
        from src.llm_service import OllamaService
        service = OllamaService(url, "test")
        if service.is_available():
            self.lbl_ollama_status.config(text="✅ Ollama est actif!", fg="#27AE60")
            self.set_status("Ollama est disponible")
        else:
            self.lbl_ollama_status.config(text="❌ Ollama ne répond pas", fg="#E74C3C")
            self.set_status("Erreur: Ollama ne répond pas")
    except Exception as e:
        self.lbl_ollama_status.config(text=f"❌ Erreur: {str(e)[:30]}", fg="#E74C3C")
        self.set_status("Erreur lors de la vérification")


def test_groq_connection(self):
    """Tester la connexion à Groq."""
    key = self.ent_groq_key.get().strip()
    if not key:
        self.lbl_groq_status.config(text="❌ Clé API manquante", fg="#E74C3C")
        messagebox.showwarning("Clé API manquante", "Veuillez entrer votre clé API Groq")
        return
    
    self.set_status("Test Groq en cours...")
    self.lbl_groq_status.config(text="Vérification...", fg="#3498DB")
    self.update()
    
    try:
        from src.llm_manager import GroqService
        service = GroqService(key, self.cmb_groq_model.get())
        if service.is_available():
            self.lbl_groq_status.config(text="✅ Groq API est active!", fg="#27AE60")
            self.set_status("Groq API est disponible")
        else:
            self.lbl_groq_status.config(text="❌ Clé API invalide", fg="#E74C3C")
            self.set_status("Erreur: Clé API invalide")
    except Exception as e:
        self.lbl_groq_status.config(text=f"❌ Erreur: {str(e)[:30]}", fg="#E74C3C")
        self.set_status("Erreur lors de la vérification")


def save_llm_config(self):
    """Enregistrer la configuration LLM."""
    config = {
        "ollama_url": self.ent_ollama_url.get().strip(),
        "ollama_model": self.ent_ollama_model.get().strip(),
        "groq_key": self.ent_groq_key.get().strip(),
        "groq_model": self.cmb_groq_model.get(),
        "primary_provider": self.cmb_llm_prov.get(),
    }
    
    # Validation
    if not config["ollama_url"]:
        messagebox.showwarning("Configuration", "URL Ollama manquante")
        return
    
    # Sauvegarder dans les variables d'environnement/config
    import os
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    
    lines = []
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            lines = f.readlines()
    
    config_lines = {
        "OLLAMA_BASE_URL": f"{config['ollama_url']}\n",
        "OLLAMA_MODEL": f"{config['ollama_model']}\n",
        "GROQ_API_KEY": f"{config['groq_key']}\n" if config['groq_key'] else "",
        "GROQ_MODEL": f"{config['groq_model']}\n",
        "LLM_PRIMARY_PROVIDER": f"{config['primary_provider']}\n",
    }
    
    updated_lines = []
    processed_keys = set()
    
    for line in lines:
        if "=" in line:
            key = line.split("=")[0].strip()
            if key in config_lines:
                processed_keys.add(key)
                if config_lines[key]:
                    updated_lines.append(f"{key}={config_lines[key]}")
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)
    
    # Ajouter les clés manquantes
    for key, value in config_lines.items():
        if key not in processed_keys and value:
            updated_lines.append(f"{key}={value}")
    
    with open(env_file, "w") as f:
        f.writelines(updated_lines)
    
    self.lbl_config_status.config(text="✅ Configuration enregistrée!", fg="#27AE60")
    self.set_status("Configuration LLM enregistrée")
    self.record_event("llm_config_updated", config)
    
    messagebox.showinfo("Configuration", "Paramètres LLM enregistrés avec succès!")


def reset_llm_config(self):
    """Réinitialiser la configuration par défaut."""
    self.ent_ollama_url.delete(0, "end")
    self.ent_ollama_url.insert(0, "http://127.0.0.1:11434")
    
    self.ent_ollama_model.delete(0, "end")
    self.ent_ollama_model.insert(0, "llama3.1:8b")
    
    self.ent_groq_key.delete(0, "end")
    self.cmb_groq_model.set("mixtral-8x7b-32768")
    self.cmb_llm_prov.set("ollama")
    
    self.lbl_ollama_status.config(text="", fg="#27AE60")
    self.lbl_groq_status.config(text="", fg="#E74C3C")
    self.lbl_config_status.config(text="", fg="#27AE60")
    
    self.set_status("Configuration réinitialisée")
