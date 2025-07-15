"""
Diagramme de Mollier pédagogique simplifié pour le fluide Frayo
Style académique clair pour cours et présentations
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import warnings
warnings.filterwarnings('ignore')

class MollierDiagramPedagogique:
    """Générateur de diagramme de Mollier pédagogique pour Frayo"""
    
    def __init__(self):
        # Configuration des couleurs académiques
        self.colors = {
            'liquid_zone': '#FFE6E6',      # Rouge très clair pour zone liquide
            'vapor_zone': '#E6F3FF',       # Bleu très clair pour zone vapeur
            'mixture_zone': '#F0E6FF',     # Violet très clair pour mélange
            'liquid_curve': '#CC0000',     # Rouge pour courbe liquide saturé
            'vapor_curve': '#0066CC',      # Bleu pour courbe vapeur saturé
            'critical_point': '#FF6600',   # Orange pour point critique
            'grid': '#CCCCCC',             # Gris clair pour grille
            'text': '#000000',             # Noir pour texte
            'arrow': '#666666'             # Gris pour flèches
        }
        
        # Configuration du style
        self.font_sizes = {
            'title': 16,
            'labels': 14,
            'zones': 12,
            'annotations': 10
        }
        
    def create_simplified_diagram(self):
        """Création du diagramme simplifié"""
        # Configuration matplotlib pour style académique
        plt.style.use('default')  # Style par défaut propre
        fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
        fig.patch.set_facecolor('white')
        
        # Configuration des axes
        ax.set_xlabel('Entropie spécifique s [kJ/kg·K]', 
                     fontsize=self.font_sizes['labels'], fontweight='bold')
        ax.set_ylabel('Enthalpie spécifique h [kJ/kg]', 
                     fontsize=self.font_sizes['labels'], fontweight='bold')
        ax.set_title('Diagramme de Mollier (h-s) - Fluide Frayo', 
                    fontsize=self.font_sizes['title'], fontweight='bold', pad=20)
        
        # Grille simple et discrète
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, color=self.colors['grid'])
        ax.set_axisbelow(True)
        
        return fig, ax
        
    def create_saturation_curves(self, ax):
        """Création des courbes de saturation simplifiées"""
        # Points pour les courbes de saturation (simplifiées mais réalistes)
        
        # Courbe liquide saturé (courbe de bulle)
        s_liquid = np.array([1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.55])  # kJ/kg·K
        h_liquid = np.array([200, 220, 240, 260, 280, 300, 310])    # kJ/kg
        
        # Courbe vapeur saturé (courbe de rosée)
        s_vapor = np.array([1.55, 1.65, 1.75, 1.85, 1.95, 2.05, 2.1])  # kJ/kg·K
        h_vapor = np.array([310, 330, 350, 370, 390, 410, 420])         # kJ/kg
        
        # Point critique
        s_critical = 1.55
        h_critical = 310
        
        # Tracé des courbes avec style académique
        ax.plot(s_liquid, h_liquid, color=self.colors['liquid_curve'], 
               linewidth=3, label='Courbe de saturation liquide', zorder=10)
        ax.plot(s_vapor, h_vapor, color=self.colors['vapor_curve'], 
               linewidth=3, label='Courbe de saturation vapeur', zorder=10)
        
        # Point critique
        ax.plot(s_critical, h_critical, 'o', color=self.colors['critical_point'], 
               markersize=10, zorder=15)
        ax.annotate('Point critique', xy=(s_critical, h_critical), 
                   xytext=(s_critical + 0.1, h_critical + 15),
                   fontsize=self.font_sizes['annotations'], fontweight='bold',
                   color=self.colors['critical_point'],
                   arrowprops=dict(arrowstyle='->', color=self.colors['critical_point']))
        
        return s_liquid, h_liquid, s_vapor, h_vapor, s_critical, h_critical
        
    def create_zones(self, ax, s_liquid, h_liquid, s_vapor, h_vapor):
        """Création des zones colorées avec labels"""
        
        # Zone liquide (à gauche)
        liquid_vertices = np.array([
            [0.8, 150], [s_liquid[0], 150], [s_liquid[-1], h_liquid[-1]], [0.8, h_liquid[-1]]
        ])
        liquid_patch = patches.Polygon(liquid_vertices, closed=True, 
                                     facecolor=self.colors['liquid_zone'], 
                                     alpha=0.7, zorder=1)
        ax.add_patch(liquid_patch)
        
        # Zone vapeur (à droite)  
        vapor_vertices = np.array([
            [s_vapor[-1], h_vapor[-1]], [2.3, h_vapor[-1]], [2.3, 450], [s_vapor[-1], 450]
        ])
        vapor_patch = patches.Polygon(vapor_vertices, closed=True,
                                    facecolor=self.colors['vapor_zone'],
                                    alpha=0.7, zorder=1)
        ax.add_patch(vapor_patch)
        
        # Zone mélange (au centre - dôme)
        mixture_vertices = np.concatenate([
            np.column_stack([s_liquid, h_liquid]),
            np.column_stack([s_vapor[::-1], h_vapor[::-1]])
        ])
        mixture_patch = patches.Polygon(mixture_vertices, closed=True,
                                      facecolor=self.colors['mixture_zone'],
                                      alpha=0.7, zorder=1)
        ax.add_patch(mixture_patch)
        
        # Labels des zones avec style académique
        ax.text(1.0, 250, 'LIQUIDE', fontsize=self.font_sizes['zones'], 
               fontweight='bold', color=self.colors['liquid_curve'],
               ha='center', va='center',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        ax.text(1.8, 350, 'LIQUIDE\n+\nVAPEUR', fontsize=self.font_sizes['zones'], 
               fontweight='bold', color='purple',
               ha='center', va='center',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        ax.text(2.15, 400, 'VAPEUR', fontsize=self.font_sizes['zones'], 
               fontweight='bold', color=self.colors['vapor_curve'],
               ha='center', va='center',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
    def add_latent_heat_arrow(self, ax):
        """Ajout de la flèche pour la chaleur latente"""
        # Ligne horizontale pour la chaleur latente à température constante
        s_start = 1.2
        s_end = 1.9
        h_constant = 270
        
        # Flèche horizontale
        ax.annotate('', xy=(s_end, h_constant), xytext=(s_start, h_constant),
                   arrowprops=dict(arrowstyle='<->', lw=2, color=self.colors['arrow']))
        
        # Label chaleur latente
        ax.text((s_start + s_end)/2, h_constant + 15, 'Chaleur latente de vaporisation',
               fontsize=self.font_sizes['annotations'], ha='center',
               color=self.colors['arrow'], fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
        
    def add_temperature_lines(self, ax):
        """Ajout de quelques isothermes pour la pédagogie"""
        temperatures = [0, 20, 40]  # °C
        colors_temp = ['#CCCCCC', '#BBBBBB', '#AAAAAA']
        
        for i, T in enumerate(temperatures):
            # Isotherme simplifiée dans la zone liquide
            s_iso_liquid = np.linspace(0.9, 1.4, 10)
            h_iso_liquid = 200 + T * 4 + (s_iso_liquid - 0.9) * 20
            
            # Isotherme simplifiée dans la zone vapeur
            s_iso_vapor = np.linspace(1.7, 2.2, 10)
            h_iso_vapor = 340 + T * 3 + (s_iso_vapor - 1.7) * 30
            
            ax.plot(s_iso_liquid, h_iso_liquid, '--', color=colors_temp[i], 
                   alpha=0.6, linewidth=1)
            ax.plot(s_iso_vapor, h_iso_vapor, '--', color=colors_temp[i], 
                   alpha=0.6, linewidth=1)
            
            # Label température
            ax.text(2.15, h_iso_vapor[-1], f'{T}°C', fontsize=8, 
                   color=colors_temp[i], ha='left')
                   
    def add_pressure_lines(self, ax):
        """Ajout de quelques isobares pour la pédagogie"""
        pressures = [2, 5, 10]  # bar
        
        for P in pressures:
            # Isobare simplifiée (approximation)
            if P == 2:
                s_iso = np.array([1.0, 1.3, 1.8, 2.1])
                h_iso = np.array([210, 250, 320, 380])
            elif P == 5:
                s_iso = np.array([1.1, 1.4, 1.7, 2.0])
                h_iso = np.array([240, 280, 340, 390])
            else:  # P == 10
                s_iso = np.array([1.2, 1.45, 1.65, 1.9])
                h_iso = np.array([270, 300, 350, 400])
                
            ax.plot(s_iso, h_iso, ':', color='gray', alpha=0.5, linewidth=1)
            ax.text(s_iso[-1] + 0.02, h_iso[-1], f'{P} bar', fontsize=8, 
                   color='gray', ha='left')
                   
    def finalize_diagram(self, ax):
        """Finalisation du diagramme"""
        # Limites des axes pour une vue claire
        ax.set_xlim(0.8, 2.3)
        ax.set_ylim(150, 450)
        
        # Légende simple
        ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
        
        # Suppression des bordures inutiles
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Style des ticks
        ax.tick_params(labelsize=10)
        
        # Note pédagogique
        ax.text(0.02, 0.98, 
               'Fluide: Frayo\nDiagramme h-s (Mollier)\nÀ des fins pédagogiques',
               transform=ax.transAxes, fontsize=9,
               verticalalignment='top', 
               bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))
               
    def generate_pedagogical_diagram(self, save_path='mollier_frayo_pedagogique.png'):
        """Génération du diagramme pédagogique complet"""
        print("📚 Génération du diagramme de Mollier pédagogique...")
        
        # Création du diagramme
        fig, ax = self.create_simplified_diagram()
        
        # Création des courbes de saturation
        s_liquid, h_liquid, s_vapor, h_vapor, s_crit, h_crit = self.create_saturation_curves(ax)
        
        # Zones colorées
        self.create_zones(ax, s_liquid, h_liquid, s_vapor, h_vapor)
        
        # Flèche chaleur latente
        self.add_latent_heat_arrow(ax)
        
        # Lignes de référence
        self.add_temperature_lines(ax)
        self.add_pressure_lines(ax)
        
        # Finalisation
        self.finalize_diagram(ax)
        
        # Sauvegarde haute résolution
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        
        print(f"✅ Diagramme pédagogique sauvegardé: {save_path}")
        return save_path, fig
        
def main():
    """Fonction principale"""
    generator = MollierDiagramPedagogique()
    
    # Génération du diagramme pédagogique
    path, fig = generator.generate_pedagogical_diagram()
    
    # Affichage
    plt.show()
    
    print("\n📚 Diagramme pédagogique généré avec succès!")
    print("🎯 Caractéristiques:")
    print("   • Style académique simplifié")
    print("   • Zones clairement délimitées et colorées")
    print("   • Courbes de saturation mises en évidence")
    print("   • Point critique identifié")
    print("   • Flèche chaleur latente")
    print("   • Fond blanc pour présentation")
    print("   • Haute résolution (300 DPI)")

if __name__ == "__main__":
    main()
