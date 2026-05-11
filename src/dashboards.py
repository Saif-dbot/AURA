import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
import datetime

class DashboardManager:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        # Colors: light theme
        self.bg_color = "#ffffff"
        self.text_color = "#333333"
        self.accent_color = "#3498db"
        plt.style.use('seaborn-v0_8-whitegrid')
        
    def clear_frame(self):
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

    def draw_radar_chart(self, valeurs_actuelles=None, machine_name="M-01"):
        self.clear_frame()
        fig = Figure(figsize=(6, 5), dpi=100, facecolor=self.bg_color)
        ax = fig.add_subplot(111, polar=True)
        ax.set_facecolor(self.bg_color)
        
        # Data
        categories = ['Vibrations', 'Température', 'Pression', 'Bruit', 'Lubrification']
        N = len(categories)
        
        if valeurs_actuelles is None:
            valeurs_actuelles = [80, 90, 70, 85, 60]
        valeurs_nominales = [50, 50, 50, 50, 50]
        
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        valeurs_actuelles += valeurs_actuelles[:1]
        valeurs_nominales += valeurs_nominales[:1]
        angles += angles[:1]
        
        ax.plot(angles, valeurs_nominales, 'g-', linewidth=2, label="Nominal")
        ax.fill(angles, valeurs_nominales, 'g', alpha=0.1)
        
        ax.plot(angles, valeurs_actuelles, 'r-', linewidth=2, label="Actuel")
        ax.fill(angles, valeurs_actuelles, 'r', alpha=0.25)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, color=self.text_color, size=10)
        ax.set_title(f"Radar de Fiabilité (Machine {machine_name})", color=self.text_color, size=14, weight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        
        canvas = FigureCanvasTkAgg(fig, master=self.parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    def draw_gantt_chart(self, tasks=None, start_dates=None, durations=None):
        self.clear_frame()
        fig = Figure(figsize=(8, 4), dpi=100, facecolor=self.bg_color)
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.bg_color)
        
        if tasks is None:
            tasks = ['Inspection qualité de l’actif', 'Lubrification préventive', 'Validation capteurs', 'Mise à jour automate']
            start_dates = [datetime.date(2023, 10, 1), datetime.date(2023, 10, 5), datetime.date(2023, 10, 10), datetime.date(2023, 10, 15)]
            durations = [3, 1, 2, 1]
        
        colors = ['#e74c3c', '#2ecc71', '#f39c12', '#3498db']
        
        for i, task in enumerate(tasks):
            ax.barh(task, durations[i], left=start_dates[i].toordinal(), color=colors[i % len(colors)], alpha=0.8)
            
        ax.set_xlabel('Date', color=self.text_color)
        ax.set_title('Timeline de Maintenance (Gantt)', color=self.text_color, size=14, weight='bold')
        
        # Format x-axis dates
        xticks = ax.get_xticks()
        ax.set_xticks(xticks)
        ax.set_xticklabels([datetime.date.fromordinal(int(d)).strftime('%Y-%m-%d') for d in xticks], rotation=45, ha='right', color=self.text_color)
        ax.tick_params(axis='y', colors=self.text_color)
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    def draw_heatmap(self, data=None):
        self.clear_frame()
        fig = Figure(figsize=(7, 5), dpi=100, facecolor=self.bg_color)
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.bg_color)
        
        if data is None:
            data = np.random.rand(5, 7) * 100
            
        components = ['Actif critique', "Système d'entraînement", 'Module process', 'Ligne de production', 'Capteur']
        days = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
        
        sns.heatmap(data, ax=ax, cmap="Blues", xticklabels=days, yticklabels=components, annot=True, fmt=".0f", cbar=False)
        
        ax.set_title("Heatmap des Défaillances / Stress Thermique", color=self.text_color, size=14, weight='bold', pad=15)
        ax.tick_params(axis='x', colors=self.text_color)
        ax.tick_params(axis='y', colors=self.text_color, rotation=0)
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
