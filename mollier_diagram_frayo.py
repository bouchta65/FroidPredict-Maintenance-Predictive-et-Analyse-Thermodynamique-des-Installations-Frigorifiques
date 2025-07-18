"""
Générateur de Diagramme de Mollier (h-s) pour le fluide frigorigène Frayo
Système de refroidissement avec capteurs réels - Maintenance prédictive
Intégration des conditions normales et anormales selon spécifications PDF
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
from scipy.interpolate import griddata
import warnings
warnings.filterwarnings('ignore')

# Import du système de capteurs réels
from sensor_system_real import RefrigerationSensors

class FrayoProperties:
    """Propriétés thermodynamiques du fluide frigorigène Frayo avec capteurs réels"""
    
    def __init__(self):
        # Constantes spécifiques au fluide Frayo
        self.R = 0.08314  # Constante des gaz parfaits [kJ/kg·K]
        self.Tc = 101.06  # Température critique [°C]
        self.Pc = 37.29   # Pression critique [bar]
        self.M = 97.6     # Masse molaire [g/mol]
        
        # Données typiques selon spécifications PDF
        self.typical_operating_conditions = {
            "temp_evaporation": -10.0,  # t0 selon PDF
            "temp_condensation": 30.0,  # tc selon PDF
            "superheat_functional": 5.0,  # Surchauffe fonctionnelle
            "superheat_aspiration": 10.0,  # Surchauffe ligne aspiration
            "temp_point_1": 5.0,  # Température aspiration (Point 1)
            "temp_point_3": 48.0,  # Température refoulement (Point 3)
            "subcooling": 5.0,  # Sous-refroidissement
            "enthalpy_h8": 395.69,  # Entrée évaporateur [kJ/kg]
            "enthalpy_h9": 404.45   # Sortie évaporateur [kJ/kg]
        }
        
        # Coefficients pour les corrélations thermodynamiques
        self.cp_liquid_coeff = [2.85, 0.0045, -1.2e-6]  # Capacité calorifique liquide
        self.cp_vapor_coeff = [0.95, 0.0032, -8.5e-7]   # Capacité calorifique vapeur
        
        # Initialisation du système de capteurs réels
        self.sensor_system = RefrigerationSensors()
        
        # Données du producteur (selon spécifications)
        self.producer_data = {
            'temperatures': [-25, -20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60],
            'pressures': [0.85, 1.12, 1.45, 1.84, 2.31, 2.87, 3.53, 4.31, 5.22, 6.27, 7.48, 8.87, 10.46, 12.27, 14.32, 16.63, 19.23, 22.15]
        }

    def saturation_pressure(self, T):
        """Pression de saturation en fonction de la température [bar]"""
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
        """Température de saturation en fonction de la pression [°C]"""
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
        return h_sat_liquid + cp_liquid * (T - T_sat)

    def entropy_subcooled_liquid(self, T, P):
        """Entropie du liquide sous-refroidi [kJ/kg·K]"""
        T_sat = self.saturation_temperature(P)
        s_sat_liquid = self.entropy_saturated_liquid(T_sat)
        cp_liquid = self.cp_liquid_coeff[0] + self.cp_liquid_coeff[1] * T
        T_abs = T + 273.15
        T_sat_abs = T_sat + 273.15
        return s_sat_liquid - cp_liquid * np.log(T_sat_abs / T_abs)

class MollierDiagramGenerator:
    """Générateur de diagramme de Mollier (h-s) pour Frayo avec capteurs réels"""
    
    def __init__(self):
        self.frayo = FrayoProperties()
        self.fig = None
        self.ax = None
        
        # Configuration des couleurs pour conditions normales/anormales
        self.colors = {
            'normal': {
                'liquid': '#E6F3FF',      # Bleu clair pour zone liquide normale
                'vapor': '#FFE6E6',       # Rouge clair pour zone vapeur normale
                'mixture': '#F0E6FF',     # Violet clair pour mélange normal
                'cycle': '#0066CC'        # Bleu pour cycle normal
            },
            'warning': {
                'liquid': '#FFF3CD',      # Jaune clair pour conditions d'alerte
                'vapor': '#F8D7DA',       # Rouge clair pour conditions d'alerte
                'mixture': '#E2E3E5',     # Gris pour conditions d'alerte
                'cycle': '#FFC107'        # Jaune pour cycle en alerte
            },
            'critical': {
                'liquid': '#F8D7DA',      # Rouge clair pour conditions critiques
                'vapor': '#F5C6CB',       # Rouge pour conditions critiques
                'mixture': '#F1B0B7',     # Rouge foncé pour conditions critiques
                'cycle': '#DC3545'        # Rouge pour cycle critique
            },
            'sensors': {
                'normal': '#28A745',      # Vert pour capteurs normaux
                'warning': '#FFC107',     # Jaune pour capteurs en alerte
                'critical': '#DC3545',    # Rouge pour capteurs critiques
                'error': '#6C757D'       # Gris pour capteurs en erreur
            }
        }

    def create_base_diagram(self, sensor_data=None):
        """Création du diagramme de base avec adaptation aux conditions des capteurs"""
        
        # Détermination du niveau de criticité basé sur les capteurs
        if sensor_data:
            abnormal_sensors = sensor_data.get('abnormal_sensors', [])
            if len(abnormal_sensors) > 3:
                color_scheme = 'critical'
            elif len(abnormal_sensors) > 0:
                color_scheme = 'warning'
            else:
                color_scheme = 'normal'
        else:
            color_scheme = 'normal'
        
        plt.style.use('default')
        self.fig, self.ax = plt.subplots(figsize=(16, 12), dpi=300)
        self.fig.patch.set_facecolor('white')
        
        # Titre adapté aux conditions
        if sensor_data:
            condition = sensor_data.get('operating_condition', 'normal')
            title = f"Diagramme de Mollier - Fluide Frayo | Machine: {sensor_data.get('machine_id', 'N/A')} | Condition: {condition.upper()}"
        else:
            title = "Diagramme de Mollier pour le fluide Frayo – Capteurs réels"
        
        self.ax.set_xlabel('Entropie spécifique s [kJ/kg·K]', fontsize=14, fontweight='bold')
        self.ax.set_ylabel('Enthalpie spécifique h [kJ/kg]', fontsize=14, fontweight='bold')
        self.ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Grille adaptée aux conditions
        alpha = 0.6 if color_scheme == 'critical' else 0.3
        self.ax.grid(True, alpha=alpha, linestyle='-', linewidth=0.5, color='#CCCCCC')
        self.ax.set_axisbelow(True)
        
        return color_scheme

    def plot_saturation_curve_with_sensors(self, sensor_data=None):
        """Tracé de la courbe de saturation avec points des capteurs réels"""
        
        T_sat = np.linspace(-25, self.frayo.Tc, 100)
        
        # Courbes de saturation
        h_liquid = [self.frayo.enthalpy_saturated_liquid(T) for T in T_sat]
        s_liquid = [self.frayo.entropy_saturated_liquid(T) for T in T_sat]
        h_vapor = [self.frayo.enthalpy_saturated_vapor(T) for T in T_sat]
        s_vapor = [self.frayo.entropy_saturated_vapor(T) for T in T_sat]
        
        # Tracé des courbes
        self.ax.plot(s_liquid, h_liquid, color='#CC0000', linewidth=3, 
                    label='Courbe de saturation liquide (bulle)', zorder=10)
        self.ax.plot(s_vapor, h_vapor, color='#0066CC', linewidth=3, 
                    label='Courbe de saturation vapeur (rosée)', zorder=10)
        
        # Ajout des points de capteurs réels si disponibles
        if sensor_data:
            self.plot_sensor_points(sensor_data)
        
        # Remplissage des zones
        self.ax.fill_betweenx(h_liquid, 0, s_liquid, color='#E6F3FF', alpha=0.7, 
                             label='Zone liquide', zorder=1)
        self.ax.fill_between(s_liquid + s_vapor, h_liquid + h_vapor, 
                           color='#F0E6FF', alpha=0.7, label='Zone diphasique', zorder=1)
        
        # Zone vapeur
        max_s = max(max(s_vapor), 2.2)
        max_h = max(max(h_vapor), 450)
        vapor_x = [s_vapor[-1]] + [max_s, max_s, s_vapor[-1]]
        vapor_y = [h_vapor[-1]] + [h_vapor[-1], max_h, max_h]
        self.ax.fill(vapor_x, vapor_y, color='#FFE6E6', alpha=0.7, 
                    label='Zone vapeur', zorder=1)
        
        return s_liquid, h_liquid, s_vapor, h_vapor

    def plot_sensor_points(self, sensor_data):
        """Tracé des points correspondant aux capteurs réels"""
        
        # Extraction des données des capteurs
        temp_evap = sensor_data['sensors']['temperature']['evaporation']
        temp_cond = sensor_data['sensors']['temperature']['condensation']
        temp_aspiration = sensor_data['sensors']['temperature']['aspiration']
        temp_refoulement = sensor_data['sensors']['temperature']['refoulement']
        temp_liquid = sensor_data['sensors']['temperature']['liquid']
        
        pressure_hp = sensor_data['sensors']['pressure']['high']
        pressure_bp = sensor_data['sensors']['pressure']['low']
        
        # Calcul des points du cycle selon données réelles
        # Point 1: Aspiration (vapeur surchauffée)
        h1 = self.frayo.enthalpy_superheated_vapor(temp_aspiration, pressure_bp)
        s1 = self.frayo.entropy_superheated_vapor(temp_aspiration, pressure_bp)
        
        # Point 2: Refoulement (vapeur surchauffée HP)
        h2 = self.frayo.enthalpy_superheated_vapor(temp_refoulement, pressure_hp)
        s2 = self.frayo.entropy_superheated_vapor(temp_refoulement, pressure_hp)
        
        # Point 3: Sortie condenseur (liquide sous-refroidi)
        h3 = self.frayo.enthalpy_subcooled_liquid(temp_liquid, pressure_hp)
        s3 = self.frayo.entropy_subcooled_liquid(temp_liquid, pressure_hp)
        
        # Point 4: Entrée évaporateur (détente isenthalpique)
        h4 = h3
        s4 = self.frayo.entropy_saturated_liquid(temp_evap)
        
        # Points du cycle réel
        points = [
            (s1, h1, '1\nAspiration', temp_aspiration),
            (s2, h2, '2\nRefoulement', temp_refoulement),
            (s3, h3, '3\nLiquide', temp_liquid),
            (s4, h4, '4\nDétente', temp_evap)
        ]
        
        # Tracé du cycle
        cycle_s = [s1, s2, s3, s4, s1]
        cycle_h = [h1, h2, h3, h4, h1]
        
        # Couleur selon la condition
        condition = sensor_data.get('operating_condition', 'normal')
        if condition == 'normal':
            cycle_color = '#0066CC'
        elif 'warning' in condition or len(sensor_data.get('abnormal_sensors', [])) > 0:
            cycle_color = '#FFC107'
        else:
            cycle_color = '#DC3545'
        
        self.ax.plot(cycle_s, cycle_h, color=cycle_color, linewidth=4, 
                    alpha=0.9, label=f'Cycle réel - {condition}', zorder=10)
        
        # Points avec couleurs selon statut des capteurs
        for i, (s, h, label, temp) in enumerate(points):
            # Détermination du statut du capteur pour ce point
            sensor_status = 'normal'
            if f'temp_{["aspiration", "refoulement", "liquid", "evaporation"][i]}' in sensor_data.get('abnormal_sensors', []):
                sensor_status = 'critical'
            elif len(sensor_data.get('abnormal_sensors', [])) > 0:
                sensor_status = 'warning'
            
            point_color = self.colors['sensors'][sensor_status]
            
            self.ax.plot(s, h, 'o', color=point_color, markersize=12, 
                        markeredgecolor='white', markeredgewidth=2, zorder=15)
            
            # Annotation avec température réelle
            self.ax.annotate(f'{label}\n{temp:.1f}°C', xy=(s, h), xytext=(10, 10), 
                           textcoords='offset points', fontsize=10, 
                           fontweight='bold', color=point_color,
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                                   edgecolor=point_color, alpha=0.9))
        
        # Calcul et affichage des performances réelles
        derived_params = sensor_data.get('derived_parameters', {})
        if derived_params:
            cop = derived_params.get('cop', 0)
            cooling_effect = derived_params.get('cooling_effect', 0)
            
            # Affichage des performances
            perf_text = f"COP: {cop:.2f}\nEffet frigorifique: {cooling_effect:.1f} kJ/kg"
            self.ax.text(0.02, 0.85, perf_text, transform=self.ax.transAxes, 
                        fontsize=12, bbox=dict(boxstyle='round,pad=0.5', 
                        facecolor='lightblue', alpha=0.8))

    def plot_sensor_status_indicators(self, sensor_data):
        """Affichage des indicateurs de statut des capteurs"""
        
        if not sensor_data:
            return
        
        # Récupération des statuts des capteurs
        sensor_status = sensor_data.get('sensor_status', {})
        abnormal_sensors = sensor_data.get('abnormal_sensors', [])
        
        # Création d'un panneau d'état des capteurs
        status_text = "ÉTAT DES CAPTEURS:\n"
        
        # Capteurs de pression
        status_text += "Pressions:\n"
        for sensor in ['pressure_hp', 'pressure_bp', 'pressure_intermediate', 'pressure_differential']:
            status = sensor_status.get(sensor, 'normal')
            emoji = {'normal': '✅', 'warning': '⚠️', 'critical': '🔴', 'error': '❌'}[status]
            status_text += f"  {emoji} {sensor}: {status}\n"
        
        # Capteurs de température
        status_text += "Températures:\n"
        for sensor in ['temp_aspiration', 'temp_refoulement', 'temp_condensation', 'temp_evaporation']:
            status = sensor_status.get(sensor, 'normal')
            emoji = {'normal': '✅', 'warning': '⚠️', 'critical': '🔴', 'error': '❌'}[status]
            status_text += f"  {emoji} {sensor}: {status}\n"
        
        # Affichage du panneau
        self.ax.text(0.75, 0.98, status_text, transform=self.ax.transAxes, 
                    fontsize=9, verticalalignment='top',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', 
                             alpha=0.9, edgecolor='orange'))

    def generate_diagram_with_real_data(self, sensor_data=None, save_path='mollier_frayo_real_sensors.png'):
        """Génération complète du diagramme avec données de capteurs réels"""
        
        if not sensor_data:
            # Génération de données d'exemple avec capteurs réels
            sensor_system = RefrigerationSensors()
            readings = sensor_system.generate_normal_readings("DEMO_MACHINE")
            derived_params = sensor_system.calculate_derived_parameters(readings)
            
            sensor_data = {
                'machine_id': 'DEMO_MACHINE',
                'operating_condition': 'normal',
                'sensors': {
                    'temperature': {
                        'evaporation': readings['temp_evaporation'].value,
                        'condensation': readings['temp_condensation'].value,
                        'aspiration': readings['temp_aspiration'].value,
                        'refoulement': readings['temp_refoulement'].value,
                        'liquid': readings['temp_liquid'].value
                    },
                    'pressure': {
                        'high': readings['pressure_hp'].value,
                        'low': readings['pressure_bp'].value,
                        'intermediate': readings['pressure_intermediate'].value,
                        'differential': readings['pressure_differential'].value
                    }
                },
                'derived_parameters': derived_params,
                'sensor_status': {k: v.status for k, v in readings.items()},
                'abnormal_sensors': [k for k, v in readings.items() if v.status != 'normal']
            }
        
        print(f"🔧 Génération du diagramme avec capteurs réels...")
        print(f"   Machine: {sensor_data['machine_id']}")
        print(f"   Condition: {sensor_data['operating_condition']}")
        print(f"   Capteurs anormaux: {len(sensor_data.get('abnormal_sensors', []))}")
        
        # Création du diagramme
        color_scheme = self.create_base_diagram(sensor_data)
        
        # Tracé des courbes avec points des capteurs
        s_liquid, h_liquid, s_vapor, h_vapor = self.plot_saturation_curve_with_sensors(sensor_data)
        
        # Tracé des lignes de référence
        self.plot_isobars()
        self.plot_isotherms()
        
        # Affichage des indicateurs de capteurs
        self.plot_sensor_status_indicators(sensor_data)
        
        # Finalisation
        self.finalize_diagram(sensor_data)
        
        # Sauvegarde
        plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        
        print(f"✅ Diagramme de Mollier avec capteurs réels généré: {save_path}")
        return save_path

    def plot_isobars(self):
        """Tracé des lignes de pression constante selon données producteur"""
        # Utilisation des pressions du producteur
        pressures = [1, 2, 5, 8, 12, 16, 20]
        
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
                self.ax.plot(s_superheat, h_superheat, color='#666666', 
                           linewidth=1.5, linestyle='--', alpha=0.8)
                self.ax.plot(s_subcool, h_subcool, color='#666666', 
                           linewidth=1.5, linestyle='--', alpha=0.8)
                
                # Étiquettes
                if len(s_superheat) > 10:
                    self.ax.annotate(f'{P} bar', 
                                   xy=(s_superheat[10], h_superheat[10]),
                                   xytext=(5, 5), textcoords='offset points',
                                   fontsize=10, color='#666666', fontweight='bold')

    def plot_isotherms(self):
        """Tracé des lignes de température constante selon données producteur"""
        # Utilisation des températures du producteur
        temperatures = [-10, 0, 10, 20, 30, 40, 50]
        
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
                           color='#999999', linewidth=1, alpha=0.7)
                self.ax.plot(s_isotherm_liquid, h_isotherm_liquid, 
                           color='#999999', linewidth=1, alpha=0.7)
                
                # Étiquettes
                if len(s_isotherm_vapor) > 5:
                    self.ax.annotate(f'{T}°C', 
                                   xy=(s_isotherm_vapor[5], h_isotherm_vapor[5]),
                                   xytext=(3, 3), textcoords='offset points',
                                   fontsize=9, color='#999999', style='italic')

    def finalize_diagram(self, sensor_data=None):
        """Finalisation du diagramme avec informations des capteurs"""
        
        # Légende
        self.ax.legend(loc='upper left', fontsize=11, framealpha=0.9,
                      edgecolor='gray', fancybox=True)
        
        # Limites des axes
        self.ax.set_xlim(0.8, 2.2)
        self.ax.set_ylim(150, 450)
        
        # Style des axes
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_linewidth(1.5)
        self.ax.spines['bottom'].set_linewidth(1.5)
        self.ax.tick_params(labelsize=11, width=1.5)
        
        # Informations des capteurs
        if sensor_data:
            info_text = f"Machine: {sensor_data['machine_id']}\n"
            info_text += f"Condition: {sensor_data['operating_condition']}\n"
            info_text += f"Capteurs surveillés: {len(sensor_data.get('sensor_status', {}))}\n"
            info_text += f"Capteurs anormaux: {len(sensor_data.get('abnormal_sensors', []))}"
            
            self.ax.text(0.02, 0.98, info_text, transform=self.ax.transAxes, 
                        fontsize=10, verticalalignment='top',
                        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightcyan', 
                                 alpha=0.9, edgecolor='teal'))
        
        # Ajustement de la mise en page
        plt.tight_layout()

def main():
    """Fonction principale avec démonstration des capteurs réels"""
    
    # Initialisation du générateur
    generator = MollierDiagramGenerator()
    
    # Génération avec capteurs réels en conditions normales
    print("📊 Génération avec conditions normales...")
    diagram_path_normal = generator.generate_diagram_with_real_data(
        save_path='mollier_frayo_normal_sensors.png'
    )
    
    # Génération avec capteurs réels en conditions anormales
    print("\n⚠️ Génération avec conditions anormales...")
    sensor_system = RefrigerationSensors()
    abnormal_readings = sensor_system.generate_abnormal_readings("MACHINE_CRITICAL", "inefficient_condensation")
    derived_params = sensor_system.calculate_derived_parameters(abnormal_readings)
    
    abnormal_sensor_data = {
        'machine_id': 'MACHINE_CRITICAL',
        'operating_condition': 'inefficient_condensation',
        'sensors': {
            'temperature': {
                'evaporation': abnormal_readings['temp_evaporation'].value,
                'condensation': abnormal_readings['temp_condensation'].value,
                'aspiration': abnormal_readings['temp_aspiration'].value,
                'refoulement': abnormal_readings['temp_refoulement'].value,
                'liquid': abnormal_readings['temp_liquid'].value
            },
            'pressure': {
                'high': abnormal_readings['pressure_hp'].value,
                'low': abnormal_readings['pressure_bp'].value,
                'intermediate': abnormal_readings['pressure_intermediate'].value,
                'differential': abnormal_readings['pressure_differential'].value
            }
        },
        'derived_parameters': derived_params,
        'sensor_status': {k: v.status for k, v in abnormal_readings.items()},
        'abnormal_sensors': [k for k, v in abnormal_readings.items() if v.status != 'normal']
    }
    
    diagram_path_abnormal = generator.generate_diagram_with_real_data(
        sensor_data=abnormal_sensor_data,
        save_path='mollier_frayo_abnormal_sensors.png'
    )
    
    # Affichage
    plt.show()
    
    print(f"\n🎯 Diagrammes générés:")
    print(f"   • Conditions normales: {diagram_path_normal}")
    print(f"   • Conditions anormales: {diagram_path_abnormal}")
    
    return diagram_path_normal, diagram_path_abnormal

if __name__ == "__main__":
    main()
