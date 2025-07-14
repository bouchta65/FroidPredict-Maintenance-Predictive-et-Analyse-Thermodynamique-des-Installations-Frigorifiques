"""
API endpoint pour générer le diagramme de Mollier Frayo
Intégration avec l'application Flask existante
"""

from mollier_diagram_frayo import MollierDiagramGenerator
import base64
import io
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif pour serveur web
import matplotlib.pyplot as plt

def generate_mollier_diagram_api():
    """Génère le diagramme de Mollier et retourne les données pour l'API"""
    try:
        # Création du générateur
        generator = MollierDiagramGenerator()
        
        # Génération du diagramme en mémoire
        generator.create_base_diagram()
        generator.plot_saturation_curve()
        generator.plot_isobars()
        generator.plot_isotherms()
        generator.plot_compression_cycle()
        generator.add_reservoir_data_points()
        generator.finalize_diagram()
        
        # Conversion en base64 pour l'API
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        
        # Encodage base64
        diagram_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Fermeture des figures matplotlib
        plt.close(generator.fig)
        
        # Données de métadonnées
        metadata = {
            'fluid_name': 'Frayo',
            'diagram_type': 'Mollier (h-s)',
            'temperature_range': '-20°C à 60°C',
            'pressure_range': '0.5 à 20 bar',
            'zones': ['Liquide (bleu)', 'Vapeur (rouge)', 'Mélange liquide-vapeur (violet)'],
            'features': [
                'Courbe de saturation',
                'Isobares (lignes de pression constante)', 
                'Isothermes (lignes de température constante)',
                'Cycle frigorifique typique',
                'Points de données réservoir simulés'
            ]
        }
        
        return {
            'status': 'success',
            'diagram_base64': diagram_base64,
            'metadata': metadata,
            'mime_type': 'image/png'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Erreur génération diagramme Mollier: {str(e)}'
        }

def get_frayo_properties_data():
    """Retourne les propriétés thermodynamiques du fluide Frayo"""
    from mollier_diagram_frayo import FrayoProperties
    
    frayo = FrayoProperties()
    
    # Calcul de quelques propriétés de référence
    reference_data = []
    temperatures = [-20, -10, 0, 10, 20, 30, 40, 50, 60]
    
    for T in temperatures:
        try:
            P_sat = frayo.saturation_pressure(T)
            h_liquid = frayo.enthalpy_saturated_liquid(T)
            h_vapor = frayo.enthalpy_saturated_vapor(T)
            s_liquid = frayo.entropy_saturated_liquid(T)
            s_vapor = frayo.entropy_saturated_vapor(T)
            
            reference_data.append({
                'temperature_celsius': T,
                'saturation_pressure_bar': round(P_sat, 3),
                'enthalpy_liquid_kj_kg': round(h_liquid, 2),
                'enthalpy_vapor_kj_kg': round(h_vapor, 2),
                'entropy_liquid_kj_kg_k': round(s_liquid, 4),
                'entropy_vapor_kj_kg_k': round(s_vapor, 4)
            })
        except:
            continue
    
    return {
        'fluid_properties': {
            'name': 'Frayo',
            'critical_temperature_celsius': frayo.Tc,
            'critical_pressure_bar': frayo.Pc,
            'molar_mass_g_mol': frayo.M,
            'gas_constant_kj_kg_k': frayo.R
        },
        'saturation_properties': reference_data
    }

if __name__ == "__main__":
    # Test de l'API
    print("🧪 Test de l'API Diagramme Mollier Frayo...")
    
    result = generate_mollier_diagram_api()
    if result['status'] == 'success':
        print("✅ Diagramme généré avec succès")
        print(f"📊 Métadonnées: {result['metadata']}")
        print(f"📁 Taille base64: {len(result['diagram_base64'])} caractères")
    else:
        print(f"❌ Erreur: {result['message']}")
    
    print("\n🔍 Test propriétés Frayo...")
    props = get_frayo_properties_data()
    print(f"🧊 Propriétés fluide: {props['fluid_properties']}")
    print(f"📈 Nombre de points de saturation: {len(props['saturation_properties'])}")
