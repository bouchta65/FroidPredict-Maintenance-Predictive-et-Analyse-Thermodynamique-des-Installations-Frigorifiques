"""
Générateur de Diagramme de Mollier (h-s) Complet et Responsive pour le fluide frigorigène Frayo
Version améliorée avec spécifications complètes
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import warnings
warnings.filterwarnings('ignore')

class FrayoProperties:
    """Propriétés thermodynamiques avancées du fluide frigorigène Frayo"""
    
    def __init__(self):
        # Constantes critiques du fluide Frayo
        self.R = 0.08314  # Constante des gaz parfaits [kJ/kg·K]
        self.Tc = 101.06  # Température critique [°C]
        self.Pc = 37.29   # Pression critique [bar]
        self.M = 97.6     # Masse molaire [g/mol]
        self.h_crit = 420 # Enthalpie critique [kJ/kg]
        self.s_crit = 1.85 # Entropie critique [kJ/kg·K]
        
        # Coefficients pour les corrélations thermodynamiques
        self.cp_liquid_coeff = [2.85, 0.0045, -1.2e-6]
        self.cp_vapor_coeff = [0.95, 0.0032, -8.5e-7]
        
        # Données du producteur (températures et pressions expérimentales)
        self.producer_data = {
            'temperatures': [-25, -20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60],
            'pressures': [0.85, 1.12, 1.45, 1.84, 2.31, 2.87, 3.53, 4.31, 5.22, 6.27, 7.48, 8.87, 10.46, 12.27, 14.32, 16.63, 19.23, 22.15]
        }
        
    def saturation_pressure(self, T):
        """Pression de saturation selon données producteur [bar]"""
        if -25 <= T <= 60:
            # Interpolation des données producteur
            temps = np.array(self.producer_data['temperatures'])
            press = np.array(self.producer_data['pressures'])
            return np.interp(T, temps, press)
        else:
            # Équation d'Antoine modifiée pour extrapolation
            A, B, C = 8.07131, 1730.63, -39.724
            return np.exp(A - B / (T + 273.15 + C)) * 0.001
        
    def saturation_temperature(self, P):
        """Température de saturation [°C]"""
        temps = np.array(self.producer_data['temperatures'])
        press = np.array(self.producer_data['pressures'])
        return np.interp(P, press, temps)
        
    def enthalpy_saturated_liquid(self, T):
        """Enthalpie du liquide saturé selon données producteur [kJ/kg]"""
        return 195 + 4.25 * T + 0.0048 * T**2
        
    def enthalpy_saturated_vapor(self, T):
        """Enthalpie de la vapeur saturée [kJ/kg]"""
        h_liquid = self.enthalpy_saturated_liquid(T)
        latent_heat = 255 - 1.75 * T - 0.002 * T**2
        return h_liquid + latent_heat
        
    def entropy_saturated_liquid(self, T):
        """Entropie du liquide saturé [kJ/kg·K]"""
        return 0.98 + 0.0042 * T + 1.1e-5 * T**2
        
    def entropy_saturated_vapor(self, T):
        """Entropie de la vapeur saturée [kJ/kg·K]"""
        s_liquid = self.entropy_saturated_liquid(T)
        T_abs = T + 273.15
        latent_heat = 255 - 1.75 * T - 0.002 * T**2
        return s_liquid + latent_heat / T_abs

class CompleteMollierDiagram:
    """Générateur de diagramme de Mollier complet selon spécifications"""
    
    def __init__(self):
        self.frayo = FrayoProperties()
        
        # Couleurs selon spécifications
        self.colors = {
            'liquid_zone': '#FFE6E6',      # Rouge clair pour zone liquide
            'vapor_zone': '#E6F3FF',       # Bleu clair pour zone vapeur
            'mixture_zone': '#F0E6FF',     # Violet clair pour mélange
            'bubble_curve': '#CC0000',     # Rouge pour courbe de bulle
            'dew_curve': '#0066CC',        # Bleu pour courbe de rosée
            'cycle_lines': '#FF6600',      # Orange pour cycle frigorifique
            'isotherms': '#888888',        # Gris pour isothermes
            'isobars': '#AAAAAA',          # Gris clair pour isobares
            'producer_data': '#FFD700',    # Jaune pour données producteur
            'latent_heat': '#999999'       # Gris pour chaleur latente
        }
        
        # Plages du diagramme
        self.s_range = [0.8, 2.4]  # Entropie [kJ/kg·K]
        self.h_range = [150, 500]  # Enthalpie [kJ/kg]
        
    def create_figure_layout(self):
        """Création de la figure avec disposition responsive"""
        # Figure principale avec subplots pour encarts
        self.fig = plt.figure(figsize=(16, 12), dpi=300)
        
        # Grille pour disposition des éléments
        gs = gridspec.GridSpec(4, 4, figure=self.fig, 
                              height_ratios=[0.2, 2.5, 0.8, 0.3],
                              width_ratios=[2.5, 0.8, 0.8, 0.2])
        
        # Diagramme principal
        self.ax_main = self.fig.add_subplot(gs[1, 0])
        
        # Encarts dans les coins
        self.ax_temp_press = self.fig.add_subplot(gs[1, 1])  # T-P
        self.ax_producer = self.fig.add_subplot(gs[1, 2])    # Données producteur
        
        # Zone pour légende à gauche
        self.ax_legend = self.fig.add_subplot(gs[1, 3])
        self.ax_legend.axis('off')
        
        # Zone titre en haut
        self.ax_title = self.fig.add_subplot(gs[0, :])
        self.ax_title.axis('off')
        
        # Configuration du diagramme principal
        self.ax_main.set_xlim(self.s_range)
        self.ax_main.set_ylim(self.h_range)
        self.ax_main.set_xlabel('Entropie spécifique s [kJ/kg·K]', fontsize=14, fontweight='bold')
        self.ax_main.set_ylabel('Enthalpie spécifique h [kJ/kg]', fontsize=14, fontweight='bold')
        self.ax_main.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        
        # Fond très léger dégradé
        gradient = np.linspace(0, 1, 256).reshape(1, -1)
        self.ax_main.imshow(gradient, extent=self.s_range + self.h_range, 
                           aspect='auto', alpha=0.05, cmap='Blues')
        
    def plot_saturation_curves_zones(self):
        """Tracé des courbes de saturation et zones colorées"""
        print("🔵 Tracé des courbes de saturation et zones...")
        
        # Températures pour les courbes
        T_range = np.linspace(-25, self.frayo.Tc, 100)
        
        # Courbes de saturation
        s_liquid = []
        h_liquid = []
        s_vapor = []
        h_vapor = []
        
        for T in T_range:
            if T < self.frayo.Tc:
                s_l = self.frayo.entropy_saturated_liquid(T)
                h_l = self.frayo.enthalpy_saturated_liquid(T)
                s_v = self.frayo.entropy_saturated_vapor(T)
                h_v = self.frayo.enthalpy_saturated_vapor(T)
                
                s_liquid.append(s_l)
                h_liquid.append(h_l)
                s_vapor.append(s_v)
                h_vapor.append(h_v)
        
        s_liquid = np.array(s_liquid)
        h_liquid = np.array(h_liquid)
        s_vapor = np.array(s_vapor)
        h_vapor = np.array(h_vapor)
        
        # Zones colorées
        self.fill_phase_zones(s_liquid, h_liquid, s_vapor, h_vapor)
        
        # Courbes de saturation
        self.ax_main.plot(s_liquid, h_liquid, color=self.colors['bubble_curve'], 
                         linewidth=3, label='Courbe de bulle (liquide)', zorder=5)
        self.ax_main.plot(s_vapor, h_vapor, color=self.colors['dew_curve'], 
                         linewidth=3, label='Courbe de rosée (vapeur)', zorder=5)
        
        # Point critique
        self.ax_main.plot(self.frayo.s_crit, self.frayo.h_crit, 'ko', 
                         markersize=10, markerfacecolor='red', 
                         markeredgecolor='black', markeredgewidth=2,
                         label='Point critique', zorder=10)
        
        # Annotation point critique
        self.ax_main.annotate(f'Point critique\n({self.frayo.Tc:.1f}°C, {self.frayo.Pc:.1f} bar)',
                             xy=(self.frayo.s_crit, self.frayo.h_crit),
                             xytext=(self.frayo.s_crit + 0.15, self.frayo.h_crit + 20),
                             fontsize=10, fontweight='bold',
                             bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.8),
                             arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
        
        return s_liquid, h_liquid, s_vapor, h_vapor
        
    def fill_phase_zones(self, s_liquid, h_liquid, s_vapor, h_vapor):
        """Remplissage des zones de phases avec couleurs spécifiées"""
        
        # Zone liquide sous-refroidi (à gauche de la courbe de bulle)
        s_left = np.linspace(self.s_range[0], s_liquid.min(), 50)
        h_bottom = np.full_like(s_left, self.h_range[0])
        h_top = np.full_like(s_left, self.h_range[1])
        
        # Interpolation pour la frontière droite de la zone liquide
        h_boundary = np.interp(s_left, s_liquid, h_liquid)
        h_boundary = np.maximum(h_boundary, self.h_range[0])
        h_boundary = np.minimum(h_boundary, self.h_range[1])
        
        self.ax_main.fill_between(s_left, self.h_range[0], h_boundary,
                                 color=self.colors['liquid_zone'], alpha=0.3, 
                                 label='Zone liquide sous-refroidi', zorder=1)
        
        # Zone mélange (entre les courbes de saturation)
        self.ax_main.fill_between(s_liquid, h_liquid, 
                                 np.interp(s_liquid, s_vapor, h_vapor),
                                 color=self.colors['mixture_zone'], alpha=0.3,
                                 label='Zone mélange liquide + vapeur', zorder=2)
        
        # Zone vapeur surchauffée (à droite de la courbe de rosée)
        s_right = np.linspace(s_vapor.max(), self.s_range[1], 50)
        h_boundary_vapor = np.interp(s_right, s_vapor[::-1], h_vapor[::-1])
        h_boundary_vapor = np.maximum(h_boundary_vapor, self.h_range[0])
        h_boundary_vapor = np.minimum(h_boundary_vapor, self.h_range[1])
        
        self.ax_main.fill_between(s_right, h_boundary_vapor, self.h_range[1],
                                 color=self.colors['vapor_zone'], alpha=0.3,
                                 label='Zone vapeur surchauffée', zorder=1)
    
    def plot_isotherms_isobars(self):
        """Tracé des isothermes et isobares"""
        print("🌡️ Tracé des isothermes et isobares...")
        
        # Isothermes
        isotherms = [-20, -10, 0, 10, 20, 30, 40, 50, 60, 80]
        for T in isotherms:
            s_isotherm = []
            h_isotherm = []
            
            # Points dans la zone vapeur surchauffée
            pressures = np.linspace(0.5, 15, 30)
            for P in pressures:
                if P < self.frayo.saturation_pressure(T):
                    try:
                        s = self.frayo.entropy_saturated_vapor(T) + 0.1 * np.log(P/self.frayo.saturation_pressure(T))
                        h = self.frayo.enthalpy_saturated_vapor(T) + 0.5 * (T - self.frayo.saturation_temperature(P))
                        if self.s_range[0] <= s <= self.s_range[1] and self.h_range[0] <= h <= self.h_range[1]:
                            s_isotherm.append(s)
                            h_isotherm.append(h)
                    except:
                        continue
            
            if len(s_isotherm) > 2:
                self.ax_main.plot(s_isotherm, h_isotherm, color=self.colors['isotherms'],
                                 linestyle='--', linewidth=1, alpha=0.7, zorder=3)
                
                # Étiquettes de température
                if len(s_isotherm) > 5:
                    mid_idx = len(s_isotherm) // 2
                    self.ax_main.text(s_isotherm[mid_idx], h_isotherm[mid_idx] + 5,
                                     f'{T}°C', fontsize=8, ha='center',
                                     bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
        
        # Isobares
        isobars = [1, 2, 5, 10, 15, 20, 25, 30]
        for P in isobars:
            s_isobar = []
            h_isobar = []
            
            # Points dans différentes zones
            temperatures = np.linspace(-30, 100, 50)
            for T in temperatures:
                try:
                    T_sat = self.frayo.saturation_temperature(P)
                    if T > T_sat:  # Zone vapeur
                        s = self.frayo.entropy_saturated_vapor(T_sat) + 0.02 * (T - T_sat)
                        h = self.frayo.enthalpy_saturated_vapor(T_sat) + 0.9 * (T - T_sat)
                    else:  # Zone liquide
                        s = self.frayo.entropy_saturated_liquid(T_sat) - 0.01 * (T_sat - T)
                        h = self.frayo.enthalpy_saturated_liquid(T_sat) - 4.0 * (T_sat - T)
                    
                    if self.s_range[0] <= s <= self.s_range[1] and self.h_range[0] <= h <= self.h_range[1]:
                        s_isobar.append(s)
                        h_isobar.append(h)
                except:
                    continue
            
            if len(s_isobar) > 2:
                self.ax_main.plot(s_isobar, h_isobar, color=self.colors['isobars'],
                                 linestyle=':', linewidth=1, alpha=0.7, zorder=3)
                
                # Étiquettes de pression
                if len(s_isobar) > 5:
                    mid_idx = len(s_isobar) // 2
                    self.ax_main.text(s_isobar[mid_idx] + 0.02, h_isobar[mid_idx],
                                     f'{P}bar', fontsize=8, rotation=45,
                                     bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
    
    def plot_refrigeration_cycle(self):
        """Tracé du cycle frigorifique avec points numérotés et flèches propres"""
        print("🔄 Tracé du cycle frigorifique...")
        
        # Points du cycle (bien dans les zones appropriées)
        cycle_points = {
            '1': {'s': 1.75, 'h': 410, 'label': 'Sortie évaporateur\n(vapeur surchauffée)'},
            '2': {'s': 1.85, 'h': 440, 'label': 'Sortie compresseur\n(compression)'},
            '3': {'s': 1.25, 'h': 260, 'label': 'Sortie condenseur\n(liquide)'},
            '4': {'s': 1.25, 'h': 220, 'label': 'Sortie détendeur\n(mélange)'}
        }
        
        # Tracé des lignes du cycle (EN ÉVITANT LE TITRE)
        # Ligne 1→2 (compression)
        s_12 = [cycle_points['1']['s'], cycle_points['2']['s']]
        h_12 = [cycle_points['1']['h'], cycle_points['2']['h']]
        
        # Ligne 2→3 (condensation) - courbe pour éviter le titre
        s_23 = np.linspace(cycle_points['2']['s'], cycle_points['3']['s'], 20)
        h_23 = np.linspace(cycle_points['2']['h'], cycle_points['3']['h'], 20)
        # Ajustement pour passer en dessous du titre (h < 480)
        h_23 = np.minimum(h_23, 470)
        
        # Ligne 3→4 (détente)
        s_34 = [cycle_points['3']['s'], cycle_points['4']['s']]
        h_34 = [cycle_points['3']['h'], cycle_points['4']['h']]
        
        # Ligne 4→1 (évaporation)
        s_41 = np.linspace(cycle_points['4']['s'], cycle_points['1']['s'], 20)
        h_41 = np.linspace(cycle_points['4']['h'], cycle_points['1']['h'], 20)
        
        # Tracé des lignes
        self.ax_main.plot(s_12, h_12, color=self.colors['cycle_lines'], 
                         linewidth=4, zorder=7, label='Cycle frigorifique')
        self.ax_main.plot(s_23, h_23, color=self.colors['cycle_lines'], 
                         linewidth=4, zorder=7)
        self.ax_main.plot(s_34, h_34, color=self.colors['cycle_lines'], 
                         linewidth=4, zorder=7)
        self.ax_main.plot(s_41, h_41, color=self.colors['cycle_lines'], 
                         linewidth=4, zorder=7)
        
        # Flèches directionnelles (bien positionnées)
        arrow_props = dict(arrowstyle='->', color=self.colors['cycle_lines'], 
                          lw=3, mutation_scale=20)
        
        # Flèche 1→2
        self.ax_main.annotate('', xy=(s_12[1]-0.02, h_12[1]-3), xytext=(s_12[0]+0.02, h_12[0]+3),
                             arrowprops=arrow_props, zorder=8)
        
        # Flèche 2→3 (au milieu de la courbe)
        mid_23 = len(s_23) // 2
        self.ax_main.annotate('', xy=(s_23[mid_23+2], h_23[mid_23+2]), 
                             xytext=(s_23[mid_23-2], h_23[mid_23-2]),
                             arrowprops=arrow_props, zorder=8)
        
        # Flèche 3→4
        self.ax_main.annotate('', xy=(s_34[1], h_34[1]+2), xytext=(s_34[0], h_34[0]-2),
                             arrowprops=arrow_props, zorder=8)
        
        # Flèche 4→1
        mid_41 = len(s_41) // 2
        self.ax_main.annotate('', xy=(s_41[mid_41+2], h_41[mid_41+2]), 
                             xytext=(s_41[mid_41-2], h_41[mid_41-2]),
                             arrowprops=arrow_props, zorder=8)
        
        # Points numérotés avec étiquettes encadrées
        for point_num, data in cycle_points.items():
            self.ax_main.plot(data['s'], data['h'], 'o', color='white', 
                             markersize=15, markeredgecolor=self.colors['cycle_lines'], 
                             markeredgewidth=3, zorder=9)
            
            self.ax_main.text(data['s'], data['h'], point_num, fontsize=12, 
                             fontweight='bold', ha='center', va='center', 
                             color=self.colors['cycle_lines'], zorder=10)
            
            # Étiquettes explicatives (bien positionnées)
            offset_x = 0.15 if data['s'] < 1.5 else -0.15
            offset_y = 15 if data['h'] < 350 else -15
            
            self.ax_main.annotate(data['label'],
                                 xy=(data['s'], data['h']),
                                 xytext=(data['s'] + offset_x, data['h'] + offset_y),
                                 fontsize=9, fontweight='bold',
                                 bbox=dict(boxstyle='round,pad=0.4', 
                                          facecolor='white', 
                                          edgecolor=self.colors['cycle_lines'], 
                                          alpha=0.9),
                                 arrowprops=dict(arrowstyle='->', 
                                               color=self.colors['cycle_lines'], 
                                               lw=1.5),
                                 zorder=8)
    
    def plot_latent_heat_arrow(self):
        """Flèche horizontale pour la chaleur latente de vaporisation"""
        print("➡️ Ajout de la flèche de chaleur latente...")
        
        # Position pour la flèche (dans la zone de mélange)
        s_pos = 1.4
        h_liquid_pos = 240
        h_vapor_pos = 380
        
        # Flèche horizontale
        self.ax_main.annotate('', xy=(s_pos, h_vapor_pos), xytext=(s_pos, h_liquid_pos),
                             arrowprops=dict(arrowstyle='<->', color=self.colors['latent_heat'], 
                                           lw=3, mutation_scale=15), zorder=6)
        
        # Étiquette
        self.ax_main.text(s_pos + 0.05, (h_liquid_pos + h_vapor_pos) / 2,
                         'Chaleur latente\nde vaporisation', 
                         fontsize=10, fontweight='bold', rotation=90,
                         ha='left', va='center',
                         bbox=dict(boxstyle='round,pad=0.3', 
                                  facecolor='white', 
                                  edgecolor=self.colors['latent_heat'], 
                                  alpha=0.9))
    
    def plot_producer_data_points(self):
        """Ajout des données expérimentales du producteur"""
        print("📊 Ajout des données du producteur...")
        
        s_producer = []
        h_producer = []
        
        for T in self.frayo.producer_data['temperatures']:
            if -25 <= T <= 60:
                s = self.frayo.entropy_saturated_liquid(T)
                h = self.frayo.enthalpy_saturated_liquid(T)
                if self.s_range[0] <= s <= self.s_range[1] and self.h_range[0] <= h <= self.h_range[1]:
                    s_producer.append(s)
                    h_producer.append(h)
        
        if s_producer:
            self.ax_main.scatter(s_producer, h_producer, 
                               color=self.colors['producer_data'], 
                               s=60, marker='s', edgecolors='black', 
                               linewidth=1, alpha=0.8, zorder=6,
                               label='Données producteur')
    
    def create_corner_diagrams(self):
        """Création des diagrammes complémentaires dans les coins"""
        print("📈 Création des encarts complémentaires...")
        
        # Encart 1: Variation T-P
        temps = np.array(self.frayo.producer_data['temperatures'])
        press = np.array(self.frayo.producer_data['pressures'])
        
        self.ax_temp_press.plot(temps, press, 'b-o', linewidth=2, markersize=4)
        self.ax_temp_press.set_xlabel('T [°C]', fontsize=10)
        self.ax_temp_press.set_ylabel('P [bar]', fontsize=10)
        self.ax_temp_press.set_title('Variation T-P\n(Données producteur)', fontsize=10, fontweight='bold')
        self.ax_temp_press.grid(True, alpha=0.3)
        self.ax_temp_press.tick_params(labelsize=8)
        
        # Encart 2: Données expérimentales simplifiées
        h_exp = [self.frayo.enthalpy_saturated_liquid(T) for T in temps[:10]]
        
        self.ax_producer.bar(range(len(h_exp)), h_exp, color=self.colors['producer_data'], alpha=0.7)
        self.ax_producer.set_xlabel('Points mesure', fontsize=10)
        self.ax_producer.set_ylabel('h [kJ/kg]', fontsize=10)
        self.ax_producer.set_title('Enthalpies mesurées\n(Échantillon)', fontsize=10, fontweight='bold')
        self.ax_producer.tick_params(labelsize=8)
        
    def create_legend(self):
        """Création de la légende à gauche"""
        print("📋 Création de la légende...")
        
        # Éléments de légende
        legend_elements = [
            '🔴 Zone liquide sous-refroidi',
            '🔵 Zone vapeur surchauffée', 
            '🟣 Zone mélange liquide + vapeur',
            '━ Courbe de bulle (liquide)',
            '━ Courbe de rosée (vapeur)',
            '🟠 Cycle frigorifique',
            '📊 Données producteur',
            '⬌ Chaleur latente',
            '••• Isothermes',
            '··· Isobares'
        ]
        
        colors_legend = [
            self.colors['liquid_zone'],
            self.colors['vapor_zone'],
            self.colors['mixture_zone'],
            self.colors['bubble_curve'],
            self.colors['dew_curve'],
            self.colors['cycle_lines'],
            self.colors['producer_data'],
            self.colors['latent_heat'],
            self.colors['isotherms'],
            self.colors['isobars']
        ]
        
        # Placement de la légende
        self.ax_legend.text(0.05, 0.95, 'LÉGENDE', fontsize=14, fontweight='bold',
                           transform=self.ax_legend.transAxes, va='top')
        
        for i, (element, color) in enumerate(zip(legend_elements, colors_legend)):
            y_pos = 0.87 - i * 0.08
            
            # Carré de couleur
            rect = patches.Rectangle((0.05, y_pos-0.02), 0.08, 0.04, 
                                   facecolor=color, alpha=0.7, 
                                   transform=self.ax_legend.transAxes)
            self.ax_legend.add_patch(rect)
            
            # Texte
            self.ax_legend.text(0.16, y_pos, element, fontsize=10,
                               transform=self.ax_legend.transAxes, va='center')
    
    def add_title(self):
        """Ajout du titre centré en haut"""
        title_text = "Diagramme de Mollier pour le fluide Frayo – Données du producteur"
        
        self.ax_title.text(0.5, 0.5, title_text, 
                          fontsize=20, fontweight='bold', ha='center', va='center',
                          transform=self.ax_title.transAxes,
                          bbox=dict(boxstyle='round,pad=0.8', 
                                   facecolor='lightblue', alpha=0.3,
                                   edgecolor='navy', linewidth=2))
    
    def finalize_diagram(self):
        """Finalisation du diagramme avec style scientifique"""
        print("🎨 Finalisation du diagramme...")
        
        # Ajustements visuels
        self.ax_main.tick_params(labelsize=12)
        self.ax_main.set_aspect('auto')
        
        # Amélioration de la grille
        self.ax_main.grid(True, alpha=0.4, linestyle='-', linewidth=0.5)
        self.ax_main.set_axisbelow(True)
        
        # Bordures du diagramme principal
        for spine in self.ax_main.spines.values():
            spine.set_linewidth(2)
            spine.set_color('navy')
        
        # Ajustement de la mise en page
        plt.tight_layout()
        
    def generate_complete_diagram(self, save_path='mollier_frayo_complet.png'):
        """Génération complète du diagramme selon spécifications"""
        print("🚀 Génération du diagramme de Mollier complet pour Frayo...")
        
        # 1. Création de la figure et disposition
        self.create_figure_layout()
        
        # 2. Ajout du titre (en premier pour éviter les conflits)
        self.add_title()
        
        # 3. Tracé des courbes de saturation et zones
        s_liquid, h_liquid, s_vapor, h_vapor = self.plot_saturation_curves_zones()
        
        # 4. Isothermes et isobares
        self.plot_isotherms_isobars()
        
        # 5. Cycle frigorifique (lignes évitent le titre)
        self.plot_refrigeration_cycle()
        
        # 6. Flèche chaleur latente
        self.plot_latent_heat_arrow()
        
        # 7. Données producteur
        self.plot_producer_data_points()
        
        # 8. Diagrammes complémentaires
        self.create_corner_diagrams()
        
        # 9. Légende
        self.create_legend()
        
        # 10. Finalisation
        self.finalize_diagram()
        
        # 11. Sauvegarde haute résolution
        print(f"💾 Sauvegarde: {save_path}")
        plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none', 
                   pad_inches=0.2)
        
        print("✅ Diagramme de Mollier complet généré avec succès!")
        print("📊 Caractéristiques:")
        print("   • Style: Scientifique et responsive")
        print("   • Zones: Rouge liquide, bleu vapeur, violet mélange")
        print("   • Cycle: Orange avec flèches nettes")
        print("   • Encarts: T-P et données producteur")
        print("   • Résolution: 300 DPI haute qualité")
        
        return save_path

def main():
    """Fonction principale de démonstration"""
    generator = CompleteMollierDiagram()
    diagram_path = generator.generate_complete_diagram()
    
    # Affichage
    plt.show()
    
    print(f"\n🎯 Diagramme sauvegardé: {diagram_path}")
    return diagram_path

if __name__ == "__main__":
    main()
