import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from dashboards import DashboardManager
from nlp_engine import NLPEngine
from prompt_generator import PromptGenerator
from planning import MaintenancePlanner
from scheduling import TaskScheduler
from app_config import (
    APP_BG,
    APP_GEOMETRY,
    APP_THEME,
    APP_TITLE,
    DB_PATH,
    FONT_BUTTON,
    FONT_HEADER,
    FONT_MAIN,
    FONT_SUBHEADER,
    LOG_PATH,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    DEFAULT_ADMIN_HINT,
)
from app_logger import setup_logger
from storage import EventStore
from auth_manager import AuthManager
from llm_service import OllamaService
from theme import (
    APP_BG as THEME_BG,
    PANEL_BG,
    SIDEBAR_BG,
    TOPBAR_BG,
    PRIMARY,
    ACCENT,
    SUCCESS,
    DANGER,
    TEXT,
    MUTED,
    BORDER,
    FONT_BODY,
    FONT_TITLE,
    FONT_SECTION,
    FONT_SMALL,
    NAV_ITEMS,
)


class AuraApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.configure(bg=THEME_BG)
        self.minsize(1180, 780)

        self.style = ttk.Style()
        self.style.theme_use(APP_THEME)
        self.style.configure("TFrame", background=THEME_BG)
        self.style.configure("TLabel", background=THEME_BG, foreground=TEXT, font=FONT_BODY)
        self.style.configure("Header.TLabel", background=THEME_BG, foreground=PRIMARY, font=FONT_HEADER)
        self.style.configure("SubHeader.TLabel", background=THEME_BG, foreground=MUTED, font=FONT_SUBHEADER)
        self.style.configure("Section.TLabel", background=PANEL_BG, foreground=PRIMARY, font=FONT_SECTION)
        self.style.configure("TEntry", padding=8)
        self.style.configure("TCombobox", padding=6)
        self.style.configure("Treeview", rowheight=28, font=FONT_BODY)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        self.logger = setup_logger(LOG_PATH)
        self.store = EventStore(DB_PATH)
        self.auth_manager = AuthManager(DB_PATH)
        self.llm_service = OllamaService(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)
        self.prompt_generator = PromptGenerator(llm_service=self.llm_service)
        self.planner = MaintenancePlanner()
        self.scheduler = TaskScheduler()
        self.current_user = None
        self.current_role = None
        self.active_page = "home"
        self.page_title_var = tk.StringVar(value="Accueil")
        self.status_var = tk.StringVar(value="Connexion requise")

        self.show_login_page()

    def _clear_root(self):
        for widget in self.winfo_children():
            widget.destroy()

    def create_card(self, parent, title, subtitle=None, padx=0, pady=0):
        card = tk.Frame(
            parent,
            bg=PANEL_BG,
            bd=1,
            relief="solid",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=BORDER,
        )
        if padx or pady:
            card.pack_propagate(False)
        header = tk.Frame(card, bg=PANEL_BG)
        header.pack(fill="x", padx=20, pady=(16, 8))
        tk.Label(header, text=title, bg=PANEL_BG, fg=PRIMARY, font=("Segoe UI", 13, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(header, text=subtitle, bg=PANEL_BG, fg=MUTED, font=FONT_SMALL).pack(anchor="w", pady=(2, 0))
        return card

    def create_metric_card(self, parent, title, value_var, accent=PRIMARY, subtitle=None):
        card = tk.Frame(
            parent,
            bg=PANEL_BG,
            bd=1,
            relief="solid",
            highlightthickness=1,
            highlightbackground=BORDER,
        )
        tk.Label(card, text=title, bg=PANEL_BG, fg=MUTED, font=FONT_SMALL).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(card, textvariable=value_var, bg=PANEL_BG, fg=accent, font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=16)
        if subtitle:
            tk.Label(card, text=subtitle, bg=PANEL_BG, fg=MUTED, font=FONT_SMALL, wraplength=220, justify="left").pack(anchor="w", padx=16, pady=(4, 12))
        return card

    def show_login_page(self):
        self._clear_root()
        self.configure(bg=THEME_BG)

        shell = tk.Frame(self, bg=THEME_BG)
        shell.pack(fill="both", expand=True)

        login_card = tk.Frame(shell, bg=PANEL_BG, bd=1, relief="solid", highlightthickness=1, highlightbackground=BORDER)
        login_card.place(relx=0.5, rely=0.5, anchor="center", width=540, height=340)

        tk.Label(login_card, text="AURA", bg=PANEL_BG, fg=PRIMARY, font=("Segoe UI", 26, "bold")).pack(pady=(26, 0))
        tk.Label(login_card, text="Industrial Intelligence Command Center", bg=PANEL_BG, fg=MUTED, font=FONT_SUBHEADER).pack(pady=(2, 18))

        form = tk.Frame(login_card, bg=PANEL_BG)
        form.pack(fill="x", padx=36)

        tk.Label(form, text="Nom d'utilisateur", bg=PANEL_BG, fg=TEXT, font=FONT_SMALL).pack(anchor="w")
        self.ent_login_user = ttk.Entry(form)
        self.ent_login_user.pack(fill="x", pady=(4, 14))
        self.ent_login_user.insert(0, "admin")

        tk.Label(form, text="Mot de passe", bg=PANEL_BG, fg=TEXT, font=FONT_SMALL).pack(anchor="w")
        self.ent_login_password = ttk.Entry(form, show="*")
        self.ent_login_password.pack(fill="x", pady=(4, 10))

        tk.Label(form, text=DEFAULT_ADMIN_HINT, bg=PANEL_BG, fg=MUTED, font=FONT_SMALL).pack(anchor="w", pady=(2, 16))

        ttk.Button(form, text="Se connecter", command=self.login_action, style="Primary.TButton").pack(fill="x")

        self.ent_login_password.bind("<Return>", lambda _: self.login_action())
        self.ent_login_user.focus_set()

    def login_action(self):
        username = self.ent_login_user.get().strip()
        password = self.ent_login_password.get()
        if not username or not password:
            messagebox.showwarning("Attention", "Veuillez saisir le nom d'utilisateur et le mot de passe.")
            return

        auth = self.auth_manager.authenticate(username, password)
        if not auth:
            self.record_event("login_failed", {"username": username})
            messagebox.showerror("Erreur", "Identifiants invalides.")
            return

        self.current_user, self.current_role = auth
        self._clear_root()
        self.create_shell()
        self.set_status(f"Connecté en tant que {self.current_user} ({self.current_role})")
        self.record_event("login_success", {"username": self.current_user, "role": self.current_role})
        self.show_page("home")

    def logout_action(self):
        if self.current_user:
            self.record_event("logout", {"username": self.current_user})
        self.current_user = None
        self.current_role = None
        self.show_login_page()

    def create_shell(self):
        self.shell = tk.Frame(self, bg=THEME_BG)
        self.shell.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(self.shell, bg=SIDEBAR_BG, width=250, bd=0, highlightthickness=1, highlightbackground=BORDER)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand = tk.Frame(self.sidebar, bg=SIDEBAR_BG)
        brand.pack(fill="x", padx=20, pady=(20, 14))
        tk.Label(brand, text="AURA", bg=SIDEBAR_BG, fg=PRIMARY, font=("Segoe UI", 24, "bold")).pack(anchor="w")
        tk.Label(brand, text="Command Center", bg=SIDEBAR_BG, fg=MUTED, font=FONT_SMALL).pack(anchor="w")

        self.sidebar_status = tk.Label(self.sidebar, text="Navigation", bg=SIDEBAR_BG, fg=TEXT, font=("Segoe UI", 10, "bold"))
        self.sidebar_status.pack(anchor="w", padx=20, pady=(10, 6))

        nav_container = tk.Frame(self.sidebar, bg=SIDEBAR_BG)
        nav_container.pack(fill="both", expand=True, padx=16)

        self.nav_buttons = {}
        nav_buttons = [("Accueil", "home")] + NAV_ITEMS
        for label, page in nav_buttons:
            btn = tk.Button(
                nav_container,
                text=label,
                command=lambda p=page: self.show_page(p),
                bg=SIDEBAR_BG,
                fg=TEXT,
                activebackground="#EAF2F8",
                activeforeground=PRIMARY,
                relief="flat",
                bd=0,
                highlightthickness=0,
                anchor="w",
                padx=16,
                pady=12,
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
            )
            btn.pack(fill="x", pady=3)
            self.nav_buttons[page] = btn

        bottom = tk.Frame(self.sidebar, bg=SIDEBAR_BG)
        bottom.pack(fill="x", padx=16, pady=16)
        tk.Label(bottom, text=f"{self.current_user} • {self.current_role}", bg=SIDEBAR_BG, fg=TEXT, font=FONT_SMALL).pack(anchor="w", pady=(0, 8))
        ttk.Button(bottom, text="Déconnexion", command=self.logout_action, style="Secondary.TButton").pack(fill="x")

        self.main_area = tk.Frame(self.shell, bg=THEME_BG)
        self.main_area.pack(side="right", fill="both", expand=True)

        self.topbar = tk.Frame(self.main_area, bg=TOPBAR_BG, bd=0, highlightthickness=1, highlightbackground=BORDER)
        self.topbar.pack(fill="x", padx=18, pady=(18, 10))

        title_box = tk.Frame(self.topbar, bg=TOPBAR_BG)
        title_box.pack(side="left", padx=16, pady=10)
        tk.Label(title_box, text="AURA Platform", bg=TOPBAR_BG, fg=PRIMARY, font=FONT_TITLE).pack(anchor="w")
        tk.Label(title_box, textvariable=self.page_title_var, bg=TOPBAR_BG, fg=MUTED, font=FONT_SMALL).pack(anchor="w")

        info_box = tk.Frame(self.topbar, bg=TOPBAR_BG)
        info_box.pack(side="right", padx=16, pady=10)
        tk.Label(info_box, textvariable=self.status_var, bg=TOPBAR_BG, fg=MUTED, font=FONT_SMALL).pack(anchor="e")
        tk.Label(info_box, text=f"Utilisateur: {self.current_user}", bg=TOPBAR_BG, fg=TEXT, font=FONT_SMALL).pack(anchor="e")

        self.content_shell = tk.Frame(self.main_area, bg=THEME_BG)
        self.content_shell.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.pages = {}
        for name in ["home", "tab_dashboards", "tab_nlp", "tab_prompt", "tab_planning", "tab_scheduling", "tab_history"]:
            frame = tk.Frame(self.content_shell, bg=THEME_BG)
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.pages[name] = frame

        self.build_home_page(self.pages["home"])
        self.build_dashboards_page(self.pages["tab_dashboards"])
        self.build_nlp_page(self.pages["tab_nlp"])
        self.build_prompt_page(self.pages["tab_prompt"])
        self.build_planning_page(self.pages["tab_planning"])
        self.build_scheduling_page(self.pages["tab_scheduling"])
        self.build_history_page(self.pages["tab_history"])

    def set_status(self, message):
        self.status_var.set(message)

    def record_event(self, event_type, payload):
        self.store.log_event(event_type, payload)
        self.logger.info("event=%s payload=%s", event_type, payload)
        if hasattr(self, "tree_history") and self.tree_history.winfo_exists():
            self.refresh_history()
        if hasattr(self, "home_metrics_ready") and self.home_metrics_ready:
            self.refresh_home_metrics()

    def show_page(self, page_name):
        if page_name not in self.pages:
            return

        self.active_page = page_name
        self.page_title_var.set(self.page_titles().get(page_name, ""))
        for name, button in getattr(self, "nav_buttons", {}).items():
            if name == page_name:
                button.configure(bg="#EAF2F8", fg=PRIMARY)
            else:
                button.configure(bg=SIDEBAR_BG, fg=TEXT)

        self.pages[page_name].tkraise()
        if page_name == "home":
            self.refresh_home_metrics()

    def page_titles(self):
        return {
            "home": "Vue d'ensemble synthétique",
            "tab_dashboards": "Tableau de bord des actifs",
            "tab_nlp": "Intelligence documentaire et RCA",
            "tab_prompt": "Aide à la décision et instructions",
            "tab_planning": "Planification stratégique et TRS",
            "tab_scheduling": "Orchestration des équipes",
            "tab_history": "Journal et audit des actions",
        }

    def build_home_page(self, page):
        page.grid_columnconfigure(0, weight=2)
        page.grid_columnconfigure(1, weight=1)
        page.grid_rowconfigure(2, weight=1)

        header = self.create_card(page, "Vue d'ensemble", "Synthèse opérationnelle de la plateforme AURA")
        header.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=0, pady=(0, 16))
        tk.Label(header, text="Command Center industriel pour la maintenance prédictive et la prise de décision", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 12)).pack(anchor="w", padx=20, pady=(0, 14))

        metrics = tk.Frame(page, bg=THEME_BG)
        metrics.grid(row=1, column=0, sticky="nsew", padx=(0, 16), pady=(0, 16))
        metrics.grid_columnconfigure(0, weight=1)
        metrics.grid_columnconfigure(1, weight=1)
        metrics.grid_rowconfigure(0, weight=1)
        metrics.grid_rowconfigure(1, weight=1)

        self.home_user_var = tk.StringVar(value="-")
        self.home_role_var = tk.StringVar(value="-")
        self.home_events_var = tk.StringVar(value="-")
        self.home_trs_var = tk.StringVar(value="-")
        self.home_last_event_var = tk.StringVar(value="-")
        self.home_page_var = tk.StringVar(value="-")
        self.home_metrics_ready = True

        self.create_metric_card(metrics, "Utilisateur", self.home_user_var, accent=PRIMARY, subtitle="Session active").grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        self.create_metric_card(metrics, "Rôle", self.home_role_var, accent=ACCENT, subtitle="Accès système").grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))
        self.create_metric_card(metrics, "Événements enregistrés", self.home_events_var, accent=SUCCESS, subtitle="Historique SQLite").grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(10, 0))
        self.create_metric_card(metrics, "TRS actuel", self.home_trs_var, accent=DANGER, subtitle="TRS calculé à partir des valeurs de démonstration").grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=(10, 0))

        quick = self.create_card(page, "Accès rapides", "Navigation et actions fréquentes")
        quick.grid(row=1, column=1, sticky="nsew", pady=(0, 16))
        quick_btns = tk.Frame(quick, bg=PANEL_BG)
        quick_btns.pack(fill="x", padx=20, pady=(0, 18))
        for label, page_name in [("Tableau de bord", "tab_dashboards"), ("NLP", "tab_nlp"), ("Planification", "tab_planning"), ("Équipes", "tab_scheduling")]:
            tk.Button(quick_btns, text=label, command=lambda p=page_name: self.show_page(p), bg=PRIMARY, fg="white", activebackground="#233140", activeforeground="white", relief="flat", padx=12, pady=10, cursor="hand2").pack(fill="x", pady=4)

        activity = self.create_card(page, "Activité récente", "Derniers événements enregistrés")
        activity.grid(row=2, column=0, sticky="nsew", padx=(0, 16))
        self.home_activity_box = tk.Text(activity, height=14, bg=PANEL_BG, fg=TEXT, relief="flat", wrap="word", padx=14, pady=12)
        self.home_activity_box.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        self.home_activity_box.configure(state="disabled")

        status_card = self.create_card(page, "Statut de session", "Informations de contexte")
        status_card.grid(row=2, column=1, sticky="nsew")
        status_lines = tk.Frame(status_card, bg=PANEL_BG)
        status_lines.pack(fill="both", expand=True, padx=20, pady=(0, 18))
        self.home_page_var.set(self.page_titles()["home"])
        for label_text, var in [("Page active", self.home_page_var), ("Dernier événement", self.home_last_event_var)]:
            row = tk.Frame(status_lines, bg=PANEL_BG)
            row.pack(fill="x", pady=6)
            tk.Label(row, text=label_text, bg=PANEL_BG, fg=MUTED, font=FONT_SMALL).pack(anchor="w")
            tk.Label(row, textvariable=var, bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 11, "bold"), wraplength=280, justify="left").pack(anchor="w", pady=(2, 0))

        self.refresh_home_metrics()

    def refresh_home_metrics(self):
        if not hasattr(self, "home_user_var"):
            return
        self.home_user_var.set(self.current_user or "Non connecté")
        self.home_role_var.set(self.current_role or "-")
        events = self.store.list_events(limit=200)
        self.home_events_var.set(str(len(events)))
        self.home_page_var.set(self.page_titles().get(self.active_page, ""))
        if events:
            last = events[0]
            self.home_last_event_var.set(f"{last['event_type']} • {last['created_at']}")
            trs_text = "85%"
            for event in events:
                payload = event.get("payload", {})
                if event["event_type"] == "planning_updated" and isinstance(payload, dict):
                    trs_text = f"{payload.get('trs', 85)}%"
                    break
            self.home_trs_var.set(trs_text)
            if hasattr(self, "home_activity_box"):
                lines = []
                for event in events[:8]:
                    payload = event.get("payload", {})
                    if isinstance(payload, dict):
                        details = ", ".join(f"{k}={v}" for k, v in payload.items())
                    else:
                        details = str(payload)
                    lines.append(f"• {event['created_at']} | {event['event_type']} | {details[:120]}")
                self.home_activity_box.configure(state="normal")
                self.home_activity_box.delete("1.0", "end")
                self.home_activity_box.insert("1.0", "\n".join(lines) if lines else "Aucune activité enregistrée.")
                self.home_activity_box.configure(state="disabled")
        else:
            self.home_last_event_var.set("Aucun événement")
            self.home_trs_var.set("85%")
            if hasattr(self, "home_activity_box"):
                self.home_activity_box.configure(state="normal")
                self.home_activity_box.delete("1.0", "end")
                self.home_activity_box.insert("1.0", "Aucune activité enregistrée.")
                self.home_activity_box.configure(state="disabled")

    def build_dashboards_page(self, page):
        page.grid_columnconfigure(0, weight=1)
        page.grid_columnconfigure(1, weight=3)
        page.grid_rowconfigure(1, weight=1)

        self.dash_display = self.create_card(page, "État de santé de l'actif", "Radar, Gantt et heatmap sont intégrés ici")
        self.dash_display.grid(row=0, column=1, rowspan=2, sticky="nsew")
        self.dash_display_content = tk.Frame(self.dash_display, bg=PANEL_BG)
        self.dash_display_content.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.dash_manager = DashboardManager(self.dash_display_content)

        controls = self.create_card(page, "Commandes tableau de bord", "Visualisation des actifs et des indicateurs")
        controls.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 16), pady=(0, 0))

        control_body = tk.Frame(controls, bg=PANEL_BG)
        control_body.pack(fill="both", expand=True, padx=20, pady=(0, 18))

        tk.Label(control_body, text="Actif sélectionné", bg=PANEL_BG, fg=TEXT, font=FONT_SMALL).pack(anchor="w")
        self.cmb_machine = ttk.Combobox(control_body, values=["Actif A", "Actif B", "Ligne de production 1", "Poste critique"], state="readonly")
        self.cmb_machine.set("Actif A")
        self.cmb_machine.pack(fill="x", pady=(4, 12))
        self.cmb_machine.bind("<<ComboboxSelected>>", lambda e: self.simulate_dashboards())

        ttk.Button(control_body, text="Radar de fiabilité", command=self.show_dashboard_radar, style="Primary.TButton").pack(fill="x", pady=4)
        ttk.Button(control_body, text="Timeline de maintenance", command=self.show_dashboard_gantt, style="Secondary.TButton").pack(fill="x", pady=4)
        ttk.Button(control_body, text="Heatmap des défaillances", command=self.show_dashboard_heatmap, style="Secondary.TButton").pack(fill="x", pady=4)
        ttk.Separator(control_body, orient="horizontal").pack(fill="x", pady=14)
        ttk.Button(control_body, text="Générer données aléatoires", command=self.simulate_dashboards, style="Primary.TButton").pack(fill="x")

        self.dash_manager.draw_radar_chart(machine_name=self.cmb_machine.get())

    def simulate_dashboards(self):
        import random
        if not hasattr(self, "dash_manager"):
            return
        nouvelles_valeurs = [random.randint(40, 100) for _ in range(5)]
        machine = self.cmb_machine.get()
        self.dash_manager.draw_radar_chart(valeurs_actuelles=nouvelles_valeurs, machine_name=machine)

    def show_dashboard_radar(self):
        if hasattr(self, "dash_manager"):
            self.dash_manager.draw_radar_chart(machine_name=self.cmb_machine.get())

    def show_dashboard_gantt(self):
        if hasattr(self, "dash_manager"):
            self.dash_manager.draw_gantt_chart()

    def show_dashboard_heatmap(self):
        if hasattr(self, "dash_manager"):
            self.dash_manager.draw_heatmap()

    def build_nlp_page(self, page):
        page.grid_columnconfigure(0, weight=1)
        page.grid_columnconfigure(1, weight=1)
        page.grid_rowconfigure(1, weight=1)

        manual = self.create_card(page, "Documentation technique", "Importer un manuel PDF, DOCX ou TXT")
        manual.grid(row=0, column=0, sticky="nsew", padx=(0, 16), pady=(0, 16))
        manual_body = tk.Frame(manual, bg=PANEL_BG)
        manual_body.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        ttk.Button(manual_body, text="Charger un manuel", command=self.load_manual, style="Primary.TButton").pack(anchor="w", pady=(0, 10))
        self.lbl_manual_status = tk.Label(manual_body, text="Aucun fichier chargé.", bg=PANEL_BG, fg=MUTED, font=FONT_SMALL)
        self.lbl_manual_status.pack(anchor="w", pady=(0, 10))
        self.txt_manual_result = tk.Text(manual_body, height=6, font=("Consolas", 10), bg="#FFFFFF", fg=TEXT, relief="flat", wrap="word")
        self.txt_manual_result.pack(fill="both", expand=True)

        rca = self.create_card(page, "Analyse d'intervention", "Extraction de causes racines et signaux faibles")
        rca.grid(row=0, column=1, sticky="nsew", pady=(0, 16))
        rca_body = tk.Frame(rca, bg=PANEL_BG)
        rca_body.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        self.txt_nlp_input = tk.Text(rca_body, height=10, font=("Consolas", 11), bg="#FFFFFF", fg=TEXT, relief="flat", wrap="word")
        self.txt_nlp_input.pack(fill="both", expand=True, pady=(0, 10))
        self.txt_nlp_input.insert("1.0", "Exemple: L'actif de production s'est arrêté brutalement suite à une hausse de vibrations et à une température anormale. Le rapport d'intervention mentionne une alerte capteur et une baisse de rendement.")
        ttk.Button(rca_body, text="Lancer l'analyse sémantique", command=self.run_nlp_analysis, style="Primary.TButton").pack(anchor="e")

        output = self.create_card(page, "Résultat de l'analyse", "Cause racine et score de confiance")
        output.grid(row=1, column=0, sticky="nsew", padx=(0, 16))
        output_body = tk.Frame(output, bg=PANEL_BG)
        output_body.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        self.lbl_nlp_result = tk.Label(output_body, text="En attente d'analyse...", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 12), justify="left", anchor="w")
        self.lbl_nlp_result.pack(fill="both", expand=True)

        learning = self.create_card(page, "Apprentissage continu", "Ajouter une nouvelle cause à la base")
        learning.grid(row=1, column=1, sticky="nsew")
        learning_body = tk.Frame(learning, bg=PANEL_BG)
        learning_body.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        self.ent_new_cause = ttk.Entry(learning_body)
        self.ent_new_cause.pack(fill="x", pady=(0, 10))
        ttk.Button(learning_body, text="Ajouter la cause", command=self.add_new_cause, style="Secondary.TButton").pack(anchor="w")

    def build_prompt_page(self, page):
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)

        card = self.create_card(page, "Aide à la décision", "Interrogation de la base de connaissances technique")
        card.grid(row=0, column=0, sticky="nsew", pady=(0, 16))
        body = tk.Frame(card, bg=PANEL_BG)
        body.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        tk.Label(body, text="Exemple: 'Donne-moi la procédure à suivre pour l'actif critique de la ligne de production 1'", bg=PANEL_BG, fg=MUTED, font=FONT_SMALL).pack(anchor="w", pady=(0, 10))
        self.ent_prompt = ttk.Entry(body)
        self.ent_prompt.pack(fill="x", pady=(0, 10))
        btn_row = tk.Frame(body, bg=PANEL_BG)
        btn_row.pack(fill="x", pady=(0, 10))
        ttk.Button(btn_row, text="Générer les instructions", command=self.generate_prompt_action, style="Primary.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Exporter en PDF", command=self.export_pdf_action, style="Secondary.TButton").pack(side="left")
        self.txt_prompt_result = tk.Text(body, height=14, font=("Consolas", 11), bg="#FFFFFF", fg=TEXT, relief="flat", wrap="word")
        self.txt_prompt_result.pack(fill="both", expand=True)

    def build_planning_page(self, page):
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(2, weight=1)

        input_card = self.create_card(page, "Analyse d'écart de performance", "Calcul du TRS et de l'écart de production")
        input_card.grid(row=0, column=0, sticky="nsew", pady=(0, 16))
        input_body = tk.Frame(input_card, bg=PANEL_BG)
        input_body.pack(fill="x", expand=True, padx=20, pady=(0, 16))

        grid = tk.Frame(input_body, bg=PANEL_BG)
        grid.pack(fill="x")
        grid.grid_columnconfigure(1, weight=1)
        grid.grid_columnconfigure(3, weight=1)

        tk.Label(grid, text="Production réelle", bg=PANEL_BG, fg=TEXT, font=FONT_SMALL).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 6))
        self.ent_prod = ttk.Entry(grid, width=12)
        self.ent_prod.insert(0, "850")
        self.ent_prod.grid(row=0, column=1, sticky="ew", padx=(0, 16), pady=(0, 6))

        tk.Label(grid, text="Capacité théorique", bg=PANEL_BG, fg=TEXT, font=FONT_SMALL).grid(row=0, column=2, sticky="w", padx=(0, 8), pady=(0, 6))
        self.ent_cap = ttk.Entry(grid, width=12)
        self.ent_cap.insert(0, "1000")
        self.ent_cap.grid(row=0, column=3, sticky="ew", pady=(0, 6))

        ttk.Button(input_body, text="Calculer TRS", command=self.update_planning, style="Primary.TButton").pack(anchor="e", pady=(12, 0))
        self.lbl_trs_res = tk.Label(input_body, text="", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 12, "bold"), anchor="w")
        self.lbl_trs_res.pack(fill="x", pady=(10, 0))

        roadmap = self.create_card(page, "Roadmap de modernisation des actifs", "Plan d'investissement 3 ans basé sur le contexte NLP")
        roadmap.grid(row=2, column=0, sticky="nsew")
        self.frame_roadmap = tk.Frame(roadmap, bg=PANEL_BG)
        self.frame_roadmap.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.update_planning()

    def build_scheduling_page(self, page):
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)

        input_card = self.create_card(page, "Orchestration des équipes de maintenance", "Affectation des actions selon urgence et compétences")
        input_card.grid(row=0, column=0, sticky="nsew", pady=(0, 16))
        input_body = tk.Frame(input_card, bg=PANEL_BG)
        input_body.pack(fill="x", expand=True, padx=20, pady=(0, 16))

        form = tk.Frame(input_body, bg=PANEL_BG)
        form.pack(fill="x")
        form.grid_columnconfigure(1, weight=1)

        tk.Label(form, text="Action de maintenance", bg=PANEL_BG, fg=TEXT, font=FONT_SMALL).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=5)
        self.ent_task = ttk.Entry(form)
        self.ent_task.insert(0, "Intervention corrective sur actif critique")
        self.ent_task.grid(row=0, column=1, sticky="ew", pady=5)

        tk.Label(form, text="Compétence requise", bg=PANEL_BG, fg=TEXT, font=FONT_SMALL).grid(row=1, column=0, sticky="w", padx=(0, 8), pady=5)
        self.ent_skill = ttk.Combobox(form, values=["Électrique", "Automatisme", "Instrumentation", "Maintenance"], state="readonly")
        self.ent_skill.set("Maintenance")
        self.ent_skill.grid(row=1, column=1, sticky="ew", pady=5)

        tk.Label(form, text="Urgence", bg=PANEL_BG, fg=TEXT, font=FONT_SMALL).grid(row=2, column=0, sticky="w", padx=(0, 8), pady=5)
        self.ent_urgency = ttk.Combobox(form, values=["Faible", "Moyenne", "Haute", "Critique"], state="readonly")
        self.ent_urgency.set("Haute")
        self.ent_urgency.grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Button(input_body, text="Assigner l'action", command=self.do_schedule_action, style="Primary.TButton").pack(anchor="e", pady=(12, 0))
        self.lbl_schedule_res = tk.Label(input_body, text="", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 12, "bold"), anchor="w")
        self.lbl_schedule_res.pack(fill="x", pady=(10, 0))

        workload = self.create_card(page, "Charge de travail des techniciens", "Répartition temps réel des compétences")
        workload.grid(row=1, column=0, sticky="nsew")
        frame_workload = tk.Frame(workload, bg=PANEL_BG)
        frame_workload.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        columns = ("Nom", "Compétences", "Disponibilité", "Charge")
        self.tree_workload = ttk.Treeview(frame_workload, columns=columns, show="headings", height=8)
        for col, title, width in [("Nom", "Nom", 120), ("Compétences", "Compétences", 240), ("Disponibilité", "Disponibilité", 120), ("Charge", "Charge de travail", 120)]:
            self.tree_workload.heading(col, text=title)
            self.tree_workload.column(col, width=width)
        self.tree_workload.pack(fill="both", expand=True)
        self.update_workload_table()

    def build_history_page(self, page):
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)

        card = self.create_card(page, "Journal et audit", "Dernières actions enregistrées dans SQLite")
        card.grid(row=0, column=0, sticky="nsew", pady=(0, 16))
        toolbar = tk.Frame(card, bg=PANEL_BG)
        toolbar.pack(fill="x", padx=20, pady=(0, 12))
        ttk.Button(toolbar, text="Rafraîchir", command=self.refresh_history, style="Primary.TButton").pack(side="left")

        table_card = self.create_card(page, "Historique des événements", "Traçabilité des actions utilisateur")
        table_card.grid(row=1, column=0, sticky="nsew")
        frame = tk.Frame(table_card, bg=PANEL_BG)
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        columns = ("Date", "Type", "Détails")
        self.tree_history = ttk.Treeview(frame, columns=columns, show="headings", height=14)
        self.tree_history.heading("Date", text="Date")
        self.tree_history.heading("Type", text="Type")
        self.tree_history.heading("Détails", text="Détails")
        self.tree_history.column("Date", width=180)
        self.tree_history.column("Type", width=180)
        self.tree_history.column("Détails", width=720)
        self.tree_history.pack(fill="both", expand=True)
        self.refresh_history()

    def refresh_history(self):
        if not hasattr(self, "tree_history") or not self.tree_history.winfo_exists():
            return
        for row in self.tree_history.get_children():
            self.tree_history.delete(row)
        events = self.store.list_events(limit=50)
        for event in events:
            payload = event.get("payload", {})
            details = ", ".join(f"{k}={v}" for k, v in payload.items()) if isinstance(payload, dict) else str(payload)
            self.tree_history.insert("", "end", values=(event["created_at"], event["event_type"], details[:200]))

    def load_manual(self):
        filepath = filedialog.askopenfilename(filetypes=[("Documents", "*.pdf *.docx *.txt"), ("All Files", "*.*")])
        if filepath:
            self.set_status(f"Chargement du manuel : {os.path.basename(filepath)}")
            self.lbl_manual_status.config(text=f"Fichier : {os.path.basename(filepath)}")
            if not hasattr(self, "nlp_engine"):
                self.nlp_engine = NLPEngine()

            data = self.nlp_engine.extract_manual_data(filepath)
            res_str = f"Composants critiques: {', '.join(data['composants_critiques']) or 'Aucun'}\n"
            res_str += f"Fréquences lubrification: {', '.join(data['frequences_lubrification']) or 'Aucun'}\n"
            res_str += f"Seuils d'alerte: {', '.join(data['seuils_alerte']) or 'Aucun'}"
            self.txt_manual_result.delete("1.0", "end")
            self.txt_manual_result.insert("1.0", res_str)
            self.record_event("manual_loaded", {"file": os.path.basename(filepath)})
            self.set_status("Manuel chargé et analysé")

    def run_nlp_analysis(self):
        text = self.txt_nlp_input.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("Attention", "Veuillez saisir un rapport d'intervention avant l'analyse.")
            return

        if not hasattr(self, "nlp_engine"):
            self.lbl_nlp_result.config(text="Chargement des modèles NLP... Veuillez patienter.")
            self.update()
            self.nlp_engine = NLPEngine()

        self.set_status("Analyse NLP en cours")
        res = self.nlp_engine.root_cause_analysis(text)
        if isinstance(res, dict):
            msg = f"Cause Racine Identifiée : {res['cause_racine']}\nNiveau de confiance : {res['confiance']}%"
            self.update_planning()
            self.record_event("nlp_analysis", {"confidence": res["confiance"], "cause": res["cause_racine"]})
        else:
            msg = res
            self.record_event("nlp_analysis", {"result": str(res)[:120]})
        self.lbl_nlp_result.config(text=msg)
        self.set_status("Analyse NLP terminée")

    def add_new_cause(self):
        cause = self.ent_new_cause.get().strip()
        if len(cause) < 8:
            messagebox.showwarning("Attention", "Veuillez saisir une cause plus descriptive (minimum 8 caractères).")
            return
        if not hasattr(self, "nlp_engine"):
            self.nlp_engine = NLPEngine()
        if self.nlp_engine.add_to_knowledge_base(cause):
            messagebox.showinfo("Succès", "Nouvelle cause ajoutée à la base d'apprentissage continu.")
            self.ent_new_cause.delete(0, "end")
            self.set_status("Nouvelle cause ajoutée à la base de connaissances")
            self.record_event("knowledge_base_updated", {"cause": cause[:120]})
        else:
            messagebox.showwarning("Info", "Cause déjà existante ou erreur.")

    def generate_prompt_action(self):
        query = self.ent_prompt.get().strip()
        if not query:
            messagebox.showwarning("Attention", "Veuillez saisir une requête.")
            return
        result = self.prompt_generator.generate_prompt(query)
        self.txt_prompt_result.delete("1.0", "end")
        self.txt_prompt_result.insert("1.0", result["text"])
        self.set_status(f"Instruction générée (source: {result['source']})")
        self.record_event("prompt_generated", {"query": query[:120], "source": result["source"]})

    def export_pdf_action(self):
        text = self.txt_prompt_result.get("1.0", "end-1c")
        if not text.strip():
            messagebox.showwarning("Attention", "Aucune instruction à exporter.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Fichier PDF", "*.pdf")])
        if filepath:
            success = self.prompt_generator.export_to_pdf(text, filepath)
            if success:
                messagebox.showinfo("Succès", f"Fiche d'intervention exportée: {filepath}")
                self.set_status(f"PDF exporté : {os.path.basename(filepath)}")
                self.record_event("pdf_exported", {"file": os.path.basename(filepath)})
            else:
                messagebox.showerror("Erreur", "L'export a échoué. Assurez-vous que reportlab est installé.")

    def update_planning(self):
        if not hasattr(self, "ent_prod") or not hasattr(self, "ent_cap"):
            return
        try:
            prod = float(self.ent_prod.get())
            cap = float(self.ent_cap.get())
        except ValueError:
            messagebox.showwarning("Attention", "Production et capacité doivent être des valeurs numériques.")
            self.set_status("Valeurs de planification invalides")
            return

        if cap <= 0 or prod < 0:
            messagebox.showwarning("Attention", "Capacité doit être > 0 et production >= 0.")
            self.set_status("Valeurs de planification hors limites")
            return

        res = self.planner.performance_gap_analysis(real_production=prod, theoretical_capacity=cap)
        color = DANGER if res["Statut"] == "Critique" else (ACCENT if res["Statut"] == "Acceptable" else SUCCESS)
        self.lbl_trs_res.config(text=f"TRS Actuel : {res['TRS']}%  |  Statut : {res['Statut']}  |  Écart : {res['Ecart_Production']} unités", fg=color)
        self.set_status(f"Planification mise à jour - statut {res['Statut']}")
        self.record_event("planning_updated", {"production": prod, "capacity": cap, "trs": res["TRS"], "status": res["Statut"]})

        for widget in self.frame_roadmap.winfo_children():
            widget.destroy()

        nlp_hist = self.nlp_engine.rca_history if hasattr(self, "nlp_engine") else None
        roadmap = self.planner.generate_roadmap(nlp_history=nlp_hist)
        for item in roadmap:
            row = tk.Frame(self.frame_roadmap, bg=PANEL_BG)
            row.pack(fill="x", pady=6)
            tk.Label(row, text=item["Année"], bg=PANEL_BG, fg=PRIMARY, font=("Segoe UI", 11, "bold"), width=12, anchor="w").pack(side="left")
            tk.Label(row, text=item["Action"], bg=PANEL_BG, fg=TEXT, font=FONT_BODY, anchor="w", wraplength=720, justify="left").pack(side="left", fill="x", expand=True)
            tk.Label(row, text=item["Budget Estimé"], bg=PANEL_BG, fg=MUTED, font=FONT_BODY, width=14, anchor="e").pack(side="right")

    def update_workload_table(self):
        if not hasattr(self, "tree_workload"):
            return
        for row in self.tree_workload.get_children():
            self.tree_workload.delete(row)
        for t in self.scheduler.get_all_technicians():
            disp = "Oui" if t["disponible"] else "Non"
            self.tree_workload.insert("", "end", values=(t["nom"], ", ".join(t["competences"]), disp, str(t.get("charge", 0))))

    def do_schedule_action(self):
        task = self.ent_task.get().strip()
        skill = self.ent_skill.get().strip()
        urgency = self.ent_urgency.get()
        if not task:
            messagebox.showwarning("Attention", "Veuillez saisir une tâche.")
            return
        if not skill:
            messagebox.showwarning("Attention", "Veuillez choisir une compétence requise.")
            return

        res = self.scheduler.assign_task(task, skill, urgency)
        color = SUCCESS if res["statut"] == "Assigné" else DANGER
        self.lbl_schedule_res.config(text=f"Résultat: {res['statut']} -> {res['assigne_a']}", fg=color)
        self.update_workload_table()
        self.set_status(f"Tâche traitée : {res['statut']}")
        self.record_event("task_assignment", {"task": task[:100], "skill": skill, "urgency": urgency, "assigned_to": res["assigne_a"], "status": res["statut"]})


if __name__ == "__main__":
    app = AuraApp()
    app.mainloop()
