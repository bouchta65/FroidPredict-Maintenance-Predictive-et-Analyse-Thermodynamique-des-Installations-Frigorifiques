"""
Générateur de Diagramme de Mollier (h-s) pour le fluide frigorigène Frayo
Système de refroidissement avec réservoir - Maintenance prédictive
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
from scipy.interpolate import griddata
import warnings
warnings.filterwarnings('ignore')

class FrayoProperties:
    """Propriétés thermodynamiques du fluide frigorigène Frayo"""
    
    def __init__(self):
        # Constantes spécifiques au fluide Frayo
        self.R = 0.08314  # Constante des gaz parfaits [kJ/kg·K]
        self.Tc = 101.06  # Température critique [°C]
        self.Pc = 37.29   # Pression critique [bar]
        self.M = 97.6     # Masse molaire [g/mol]
        
        # Coefficients pour les corrélations thermodynamiques
        self.cp_liquid_coeff = [2.85, 0.0045, -1.2e-6]  # Capacité calorifique liquide
        self.cp_vapor_coeff = [0.95, 0.0032, -8.5e-7]   # Capacité calorifique vapeur
        
    def saturation_pressure(self, T):
        """Pression de saturation en fonction de la température [bar]"""
        # Équation d'Antoine modifiée pour Frayo
        A, B, C = 8.07131, 1730.63, -39.724
        return np.exp(A - B / (T + 273.15 + C)) * 0.001  # Conversion Pa vers bar
        
    def saturation_temperature(self, P):
        """Température de saturation en fonction de la pression [°C]"""
        # Résolution inverse de l'équation d'Antoine
        A, B, C = 8.07131, 1730.63, -39.724
        return B / (A - np.log(P * 1000)) - 273.15 - C
        
    def enthalpy_saturated_liquid(self, T):
        """Enthalpie du liquide saturé [kJ/kg]"""
        # Corrélation polynomiale pour Frayo
        return 200 + 4.18 * T + 0.0045 * T**2
        
    def enthalpy_saturated_vapor(self, T):
        """Enthalpie de la vapeur saturée [kJ/kg]"""
        # Corrélation avec chaleur latente
        h_liquid = self.enthalpy_saturated_liquid(T)
        latent_heat = 250 - 1.8 * T  # Chaleur latente variable
        return h_liquid + latent_heat
        
    def entropy_saturated_liquid(self, T):
        """Entropie du liquide saturé [kJ/kg·K]"""
        return 1.0 + 0.004 * T + 1.2e-5 * T**2
        
    def entropy_saturated_vapor(self, T):
        """Entropie de la vapeur saturée [kJ/kg·K]"""
        s_liquid = self.entropy_saturated_liquid(T)
        T_abs = T + 273.15
        latent_heat = 250 - 1.8 * T
        return s_liquid + latent_heat / T_abs
        
    def enthalpy_superheated_vapor(self, T, P):
        """Enthalpie de la vapeur surchauffée [kJ/kg]"""
        T_sat = self.saturation_temperature(P)
        h_sat_vapor = self.enthalpy_saturated_vapor(T_sat)
        cp_vapor = self.cp_vapor_coeff[0] + self.cp_vapor_coeff[1] * T
        return h_sat_vapor + cp_vapor * (T - T_sat)
        
    def entropy_superheated_vapor(self, T, P):
        """Entropie de la vapeur surchauffée [kJ/kg·K]"""
        T_sat = self.saturation_temperature(P)
        s_sat_vapor = self.entropy_saturated_vapor(T_sat)
        cp_vapor = self.cp_vapor_coeff[0] + self.cp_vapor_coeff[1] * T
        T_abs = T + 273.15
        T_sat_abs = T_sat + 273.15
        return s_sat_vapor + cp_vapor * np.log(T_abs / T_sat_abs)
        
    def enthalpy_subcooled_liquid(self, T, P):
        """Enthalpie du liquide sous-refroidi [kJ/kg]"""
        T_sat = self.saturation_temperature(P)
        h_sat_liquid = self.enthalpy_saturated_liquid(T_sat)
        cp_liquid = self.cp_liquid_coeff[0] + self.cp_liquid_coeff[1] * T
        return h_sat_liquid - cp_liquid * (T_sat - T)
        
    def entropy_subcooled_liquid(self, T, P):
        """Entropie du liquide sous-refroidi [kJ/kg·K]"""
        T_sat = self.saturation_temperature(P)
        s_sat_liquid = self.entropy_saturated_liquid(T_sat)
        cp_liquid = self.cp_liquid_coeff[0] + self.cp_liquid_coeff[1] * T
        T_abs = T + 273.15
        T_sat_abs = T_sat + 273.15
        return s_sat_liquid - cp_liquid * np.log(T_sat_abs / T_abs)

class MollierDiagramGenerator:
    """Générateur de diagramme de Mollier (h-s) pour Frayo"""
    
    def __init__(self):
        self.frayo = FrayoProperties()
        self.fig = None
        self.ax = None
        
        # Plages de données
        self.T_range = np.linspace(-20, 60, 81)  # Températures de -20°C à 60°C
        self.P_range = np.linspace(0.5, 20, 20)  # Pressions de 0.5 à 20 bar
        
        # Configuration des couleurs (style pédagogique)
        self.colors = {
            'liquid': '#FFE6E6',      # Rouge très clair pour zone liquide
            'vapor': '#E6F3FF',       # Bleu très clair pour zone vapeur
            'mixture': '#F0E6FF',     # Violet très clair pour mélange
            'saturation': '#000000',  # Noir pour courbe de saturation
            'liquid_curve': '#CC0000', # Rouge pour courbe liquide saturé
            'vapor_curve': '#0066CC',  # Bleu pour courbe vapeur saturé
            'isobars': '#666666',     # Gris pour isobares
            'isotherms': '#999999',   # Gris clair pour isothermes
            'cycle': '#FF6600',       # Orange pour cycle frigorifique
            'data_points': '#FFD700'  # Or pour points de données
        }
        
    def create_base_diagram(self):
        """Création du diagramme de base avec style pédagogique"""
        try:
            plt.style.use('default')  # Style propre comme la version pédagogique
        except:
            plt.style.use('default')
        self.fig, self.ax = plt.subplots(figsize=(14, 10), dpi=300)
        self.fig.patch.set_facecolor('white')  # Fond blanc
        
        # Configuration des axes avec style pédagogique
        self.ax.set_xlabel('Entropie spécifique s [kJ/kg·K]', 
                         fontsize=14, fontweight='bold')
        self.ax.set_ylabel('Enthalpie spécifique h [kJ/kg]', 
                         fontsize=14, fontweight='bold')
        self.ax.set_title('Diagramme de Mollier pour le fluide Frayo – Données réservoir', 
                         fontsize=16, fontweight='bold', pad=20)
        
        # Grille simple et discrète comme la version pédagogique
        self.ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, color='#CCCCCC')
        self.ax.set_axisbelow(True)
        
    def plot_saturation_curve(self):
        """Tracé de la courbe de saturation (dôme)"""
        T_sat = np.linspace(-20, self.frayo.Tc, 100)
        
        # Courbe liquide saturé
        h_liquid = [self.frayo.enthalpy_saturated_liquid(T) for T in T_sat]
        s_liquid = [self.frayo.entropy_saturated_liquid(T) for T in T_sat]
        
        # Courbe vapeur saturée
        h_vapor = [self.frayo.enthalpy_saturated_vapor(T) for T in T_sat]
        s_vapor = [self.frayo.entropy_saturated_vapor(T) for T in T_sat]
        
        # Tracé des courbes avec style pédagogique
        self.ax.plot(s_liquid, h_liquid, color=self.colors['liquid_curve'], 
                    linewidth=3, label='Courbe de saturation liquide (bulle)', zorder=10)
        self.ax.plot(s_vapor, h_vapor, color=self.colors['vapor_curve'], 
                    linewidth=3, label='Courbe de saturation vapeur (rosée)', zorder=10)
        
        # Remplissage des zones avec style pédagogique
        self.ax.fill_betweenx(h_liquid, 0, s_liquid, 
                             color=self.colors['liquid'], alpha=0.7, 
                             label='Zone liquide', zorder=1)
        self.ax.fill_between(s_liquid + s_vapor, h_liquid + h_vapor, 
                           color=self.colors['mixture'], alpha=0.7,
                           label='Zone diphasique (liquide + vapeur)', zorder=1)
        
        # Zone vapeur
        max_s = max(max(s_vapor), 2.2)
        max_h = max(max(h_vapor), 450)
        vapor_x = [s_vapor[-1]] + [max_s, max_s, s_vapor[-1]]
        vapor_y = [h_vapor[-1]] + [h_vapor[-1], max_h, max_h]
        self.ax.fill(vapor_x, vapor_y, color=self.colors['vapor'], alpha=0.7, 
                    label='Zone vapeur', zorder=1)
        
        return s_liquid, h_liquid, s_vapor, h_vapor
        
    def plot_isobars(self):
        """Tracé des lignes de pression constante (isobares)"""
        pressures = [1, 2, 5, 8, 12, 16, 20]  # bar
        
        for P in pressures:
            if P < self.frayo.Pc:
                # Zone surchauffée
                T_superheat = np.linspace(self.frayo.saturation_temperature(P) + 1, 60, 30)
                h_superheat = [self.frayo.enthalpy_superheated_vapor(T, P) for T in T_superheat]
                s_superheat = [self.frayo.entropy_superheated_vapor(T, P) for T in T_superheat]
                
                # Zone sous-refroidie
                T_subcool = np.linspace(-20, self.frayo.saturation_temperature(P) - 1, 20)
                h_subcool = [self.frayo.enthalpy_subcooled_liquid(T, P) for T in T_subcool]
                s_subcool = [self.frayo.entropy_subcooled_liquid(T, P) for T in T_subcool]
                
                # Tracé
                self.ax.plot(s_superheat, h_superheat, color=self.colors['isobars'], 
                           linewidth=1.5, linestyle='--', alpha=0.8)
                self.ax.plot(s_subcool, h_subcool, color=self.colors['isobars'], 
                           linewidth=1.5, linestyle='--', alpha=0.8)
                
                # Étiquettes de pression
                if len(s_superheat) > 10:
                    self.ax.annotate(f'{P} bar', 
                                   xy=(s_superheat[10], h_superheat[10]),
                                   xytext=(5, 5), textcoords='offset points',
                                   fontsize=10, color=self.colors['isobars'],
                                   fontweight='bold')
                                   
    def plot_isotherms(self):
        """Tracé des lignes de température constante (isothermes)"""
        temperatures = [-10, 0, 10, 20, 30, 40, 50]  # °C
        
        for T in temperatures:
            if T < self.frayo.Tc:
                # Isotherme dans la zone surchauffée
                P_range_vapor = np.linspace(0.5, self.frayo.saturation_pressure(T) - 0.1, 15)
                h_isotherm_vapor = [self.frayo.enthalpy_superheated_vapor(T, P) for P in P_range_vapor]
                s_isotherm_vapor = [self.frayo.entropy_superheated_vapor(T, P) for P in P_range_vapor]
                
                # Isotherme dans la zone sous-refroidie
                P_range_liquid = np.linspace(self.frayo.saturation_pressure(T) + 0.1, 20, 15)
                h_isotherm_liquid = [self.frayo.enthalpy_subcooled_liquid(T, P) for P in P_range_liquid]
                s_isotherm_liquid = [self.frayo.entropy_subcooled_liquid(T, P) for P in P_range_liquid]
                
                # Tracé
                self.ax.plot(s_isotherm_vapor, h_isotherm_vapor, 
                           color=self.colors['isotherms'], linewidth=1, alpha=0.7)
                self.ax.plot(s_isotherm_liquid, h_isotherm_liquid, 
                           color=self.colors['isotherms'], linewidth=1, alpha=0.7)
                
                # Étiquettes de température
                if len(s_isotherm_vapor) > 5:
                    self.ax.annotate(f'{T}°C', 
                                   xy=(s_isotherm_vapor[5], h_isotherm_vapor[5]),
                                   xytext=(3, 3), textcoords='offset points',
                                   fontsize=9, color=self.colors['isotherms'],
                                   style='italic')
                                   
    def plot_compression_cycle(self):
        """Tracé d'un cycle de compression frigorifique typique"""
        # Points du cycle (exemple pour un système de climatisation)
        T_evap = -10  # °C
        T_cond = 40   # °C
        P_evap = self.frayo.saturation_pressure(T_evap)
        P_cond = self.frayo.saturation_pressure(T_cond)
        
        # Point 1: Sortie évaporateur (vapeur saturée)
        h1 = self.frayo.enthalpy_saturated_vapor(T_evap)
        s1 = self.frayo.entropy_saturated_vapor(T_evap)
        
        # Point 2: Sortie compresseur (compression isentropique)
        s2 = s1  # isentropique
        T2 = T_cond + 20  # surchauffe à la sortie compresseur
        h2 = self.frayo.enthalpy_superheated_vapor(T2, P_cond)
        
        # Point 3: Sortie condenseur (liquide saturé)
        h3 = self.frayo.enthalpy_saturated_liquid(T_cond)
        s3 = self.frayo.entropy_saturated_liquid(T_cond)
        
        # Point 4: Sortie détendeur (expansion isenthalpe)
        h4 = h3  # isenthalpe
        s4 = self.frayo.entropy_saturated_liquid(T_evap) + (h4 - self.frayo.enthalpy_saturated_liquid(T_evap)) / (T_evap + 273.15)
        
        # Tracé du cycle avec style pédagogique
        cycle_s = [s1, s2, s3, s4, s1]
        cycle_h = [h1, h2, h3, h4, h1]
        
        self.ax.plot(cycle_s, cycle_h, color=self.colors['cycle'], linewidth=4, 
                    alpha=0.9, label='Cycle frigorifique', zorder=10)
        
        # Points caractéristiques avec style amélioré
        points = [(s1, h1, '1\nSortie évaporateur'), (s2, h2, '2\nSortie compresseur'), 
                  (s3, h3, '3\nSortie condenseur'), (s4, h4, '4\nSortie détendeur')]
        for s, h, label in points:
            self.ax.plot(s, h, 'o', color=self.colors['cycle'], markersize=12, 
                        markeredgecolor='white', markeredgewidth=2, zorder=15)
            self.ax.annotate(label, xy=(s, h), xytext=(10, 10), 
                           textcoords='offset points', fontsize=10, 
                           fontweight='bold', color=self.colors['cycle'],
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                                   edgecolor=self.colors['cycle'], alpha=0.9))
                           
        # Flèches pour indiquer le sens du cycle (style simplifié)
        arrow_props = dict(arrowstyle='->', lw=3, color=self.colors['cycle'], alpha=0.8)
        self.ax.annotate('', xy=(s2, h2), xytext=(s1, h1), arrowprops=arrow_props)
        self.ax.annotate('', xy=(s3, h3), xytext=(s2, h2), arrowprops=arrow_props)
        self.ax.annotate('', xy=(s4, h4), xytext=(s3, h3), arrowprops=arrow_props)
        self.ax.annotate('', xy=(s1, h1), xytext=(s4, h4), arrowprops=arrow_props)
                        
    def add_reservoir_data_points(self):
        """Ajout de points de données collectées depuis le réservoir"""
        # Simulation de données réelles du réservoir
        np.random.seed(42)  # Pour reproductibilité
        
        # Génération de points de données aléatoires mais réalistes
        n_points = 50
        T_data = np.random.uniform(-15, 55, n_points)
        P_data = np.random.uniform(1, 18, n_points)
        
        h_data = []
        s_data = []
        
        for T, P in zip(T_data, P_data):
            T_sat = self.frayo.saturation_temperature(P)
            
            if T > T_sat + 2:  # Vapeur surchauffée
                h = self.frayo.enthalpy_superheated_vapor(T, P)
                s = self.frayo.entropy_superheated_vapor(T, P)
            elif T < T_sat - 2:  # Liquide sous-refroidi
                h = self.frayo.enthalpy_subcooled_liquid(T, P)
                s = self.frayo.entropy_subcooled_liquid(T, P)
            else:  # Zone de saturation (mélange)
                h_liq = self.frayo.enthalpy_saturated_liquid(T_sat)
                h_vap = self.frayo.enthalpy_saturated_vapor(T_sat)
                x = np.random.uniform(0.1, 0.9)  # Titre vapeur
                h = h_liq + x * (h_vap - h_liq)
                
                s_liq = self.frayo.entropy_saturated_liquid(T_sat)
                s_vap = self.frayo.entropy_saturated_vapor(T_sat)
                s = s_liq + x * (s_vap - s_liq)
                
            h_data.append(h)
            s_data.append(s)
            
        # Tracé des points de données avec style amélioré
        self.ax.scatter(s_data, h_data, c=self.colors['data_points'], s=40, alpha=0.8, 
                       edgecolors='orange', linewidth=1.5, 
                       label='Données réservoir (50 points)', zorder=8,
                       marker='o')
                       
    def finalize_diagram(self):
        """Finalisation du diagramme avec style pédagogique"""
        # Légende simplifiée
        self.ax.legend(loc='upper left', fontsize=11, framealpha=0.9,
                      edgecolor='gray', fancybox=True)
        
        # Limites des axes optimisées
        self.ax.set_xlim(0.8, 2.2)
        self.ax.set_ylim(150, 450)
        
        # Suppression des bordures inutiles (style académique)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_linewidth(1.5)
        self.ax.spines['bottom'].set_linewidth(1.5)
        
        # Style des ticks
        self.ax.tick_params(labelsize=11, width=1.5)
        
        # Annotations techniques avec style pédagogique
        self.ax.text(0.02, 0.98, 
                    'Fluide frigorigène: Frayo\nTempératures: -20°C à 60°C\nPressions: 0.5 à 20 bar\nStyle: Complet avec données réservoir',
                    transform=self.ax.transAxes, fontsize=10,
                    verticalalignment='top', 
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', 
                             alpha=0.9, edgecolor='orange'))
                    
        # Ajout d'une flèche pour la chaleur latente (style pédagogique)
        self.ax.annotate('', xy=(1.9, 270), xytext=(1.2, 270),
                        arrowprops=dict(arrowstyle='<->', lw=2, color='#666666'))
        self.ax.text(1.55, 285, 'Chaleur latente de vaporisation', 
                    fontsize=10, ha='center', color='#666666', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
        
        # Labels des zones (style pédagogique)
        self.ax.text(1.0, 250, 'LIQUIDE\nSOUS-REFROIDI', fontsize=12, 
                    fontweight='bold', color=self.colors['liquid_curve'],
                    ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                             edgecolor=self.colors['liquid_curve'], alpha=0.9))
        
        self.ax.text(1.75, 350, 'MÉLANGE\nLIQUIDE + VAPEUR', fontsize=12, 
                    fontweight='bold', color='purple',
                    ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                             edgecolor='purple', alpha=0.9))
        
        self.ax.text(2.05, 400, 'VAPEUR\nSURCHAUFFÉE', fontsize=12, 
                    fontweight='bold', color=self.colors['vapor_curve'],
                    ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                             edgecolor=self.colors['vapor_curve'], alpha=0.9))
        
        # Ajustement de la mise en page
        plt.tight_layout()
        
    def generate_diagram(self, save_path='diagramme_mollier_frayo.png'):
        """Génération complète du diagramme"""
        print("🧊 Génération du diagramme de Mollier pour Frayo...")
        
        # Création du diagramme de base
        self.create_base_diagram()
        
        # Tracé des éléments
        print("📈 Tracé de la courbe de saturation...")
        self.plot_saturation_curve()
        
        print("📊 Tracé des isobares...")
        self.plot_isobars()
        
        print("🌡️ Tracé des isothermes...")
        self.plot_isotherms()
        
        print("🔄 Tracé du cycle frigorifique...")
        self.plot_compression_cycle()
        
        print("💾 Ajout des données réservoir...")
        self.add_reservoir_data_points()
        
        print("🎨 Finalisation...")
        self.finalize_diagram()
        
        # Sauvegarde
        print(f"💾 Sauvegarde: {save_path}")
        plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        
        print("✅ Diagramme de Mollier généré avec succès!")
        return save_path

def main():
    """Fonction principale"""
    generator = MollierDiagramGenerator()
    diagram_path = generator.generate_diagram()
    
    # Affichage du diagramme
    plt.show()
    
    print(f"\n🎯 Diagramme sauvegardé: {diagram_path}")
    print("📋 Caractéristiques du diagramme:")
    print("   - Fluide frigorigène: Frayo")
    print("   - Type: Diagramme de Mollier (h-s)")
    print("   - Plage température: -20°C à 60°C")
    print("   - Plage pression: 0.5 à 20 bar")
    print("   - Zones: Liquide (bleu), Vapeur (rouge), Mélange (violet)")
    print("   - Cycle frigorifique inclus")
    print("   - Données réservoir simulées")

if __name__ == "__main__":
    main()
