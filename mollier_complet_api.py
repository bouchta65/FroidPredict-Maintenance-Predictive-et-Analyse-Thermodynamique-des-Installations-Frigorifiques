"""
API pour le diagramme de Mollier complet et responsive
Intégration avec l'application Flask existante
"""

from mollier_complet_responsive import CompleteMollierDiagram
import base64
import io
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif pour serveur web
import matplotlib.pyplot as plt

def generate_complete_mollier_api():
    """Génère le diagramme complet et retourne les données pour l'API"""
    try:
        # Création du générateur complet
        generator = CompleteMollierDiagram()
        
        # Génération du diagramme en mémoire
        generator.create_figure_layout()
        generator.add_title()
        s_liquid, h_liquid, s_vapor, h_vapor = generator.plot_saturation_curves_zones()
        generator.plot_isotherms_isobars()
        generator.plot_refrigeration_cycle()
        generator.plot_latent_heat_arrow()
        generator.plot_producer_data_points()
        generator.create_corner_diagrams()
        generator.create_legend()
        generator.finalize_diagram()
        
        # Conversion en base64 pour l'API
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none', pad_inches=0.2)
        buffer.seek(0)
        
        # Encodage base64
        diagram_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Fermeture des figures matplotlib
        plt.close(generator.fig)
        
        # Données de métadonnées enrichies
        metadata = {
            'type': 'complete_mollier_responsive',
            'title': 'Diagramme de Mollier complet pour le fluide Frayo – Données du producteur',
            'fluid': 'Frayo',
            'specifications': {
                'axes': {
                    'x': 'Entropie spécifique s [kJ/kg·K]',
                    'y': 'Enthalpie spécifique h [kJ/kg]'
                },
                'zones': {
                    'liquid': 'Rouge clair (#FFE6E6) - Liquide sous-refroidi',
                    'vapor': 'Bleu clair (#E6F3FF) - Vapeur surchauffée', 
                    'mixture': 'Violet clair (#F0E6FF) - Mélange liquide + vapeur'
                },
                'curves': {
                    'bubble': 'Rouge (#CC0000) - Courbe de bulle',
                    'dew': 'Bleu (#0066CC) - Courbe de rosée',
                    'critical_point': 'Point critique visible et annoté'
                },
                'cycle': {
                    'color': 'Orange (#FF6600)',
                    'points': ['Sortie évaporateur', 'Compression', 'Sortie condenseur', 'Sortie détendeur'],
                    'arrows': 'Flèches nettes et propres',
                    'numbering': 'Points numérotés (1,2,3,4) avec étiquettes encadrées'
                },
                'features': {
                    'latent_heat': 'Flèche horizontale grise',
                    'legend': 'Légende à gauche claire',
                    'corner_diagrams': ['Variation T-P', 'Données producteur'],
                    'producer_data': 'Points jaunes avec données expérimentales'
                },
                'style': {
                    'resolution': '300 DPI haute résolution',
                    'background': 'Fond blanc avec léger dégradé',
                    'responsive': 'Design adaptatif et scientifique',
                    'font': 'Police claire sans surcharge visuelle'
                }
            },
            'ranges': {
                'entropy': [0.8, 2.4],  # kJ/kg·K
                'enthalpy': [150, 500]  # kJ/kg
            },
            'producer_data': {
                'temperatures': generator.frayo.producer_data['temperatures'],
                'pressures': generator.frayo.producer_data['pressures'],
                'description': 'Données expérimentales fournies par le producteur'
            },
            'generation_info': {
                'version': '2.0',
                'type': 'complete_responsive',
                'features_count': 12,
                'zones_count': 3,
                'cycle_points': 4,
                'corner_diagrams': 2
            }
        }
        
        return {
            'status': 'success',
            'message': 'Diagramme de Mollier complet généré avec succès',
            'diagram_base64': diagram_base64,
            'metadata': metadata,
            'file_info': {
                'format': 'PNG',
                'resolution': '300 DPI',
                'size_bytes': len(buffer.getvalue()),
                'compression': 'Optimisée'
            }
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Erreur génération diagramme complet: {str(e)}',
            'error_type': type(e).__name__
        }

def get_complete_frayo_properties():
    """Retourne les propriétés complètes du fluide Frayo avec données producteur"""
    try:
        from mollier_complet_responsive import FrayoProperties
        
        frayo = FrayoProperties()
        
        # Calcul des propriétés pour toutes les températures du producteur
        complete_data = []
        for i, T in enumerate(frayo.producer_data['temperatures']):
            P_sat = frayo.producer_data['pressures'][i]
            h_liquid = frayo.enthalpy_saturated_liquid(T)
            h_vapor = frayo.enthalpy_saturated_vapor(T)
            s_liquid = frayo.entropy_saturated_liquid(T)
            s_vapor = frayo.entropy_saturated_vapor(T)
            latent_heat = h_vapor - h_liquid
            
            complete_data.append({
                'temperature_celsius': T,
                'saturation_pressure_bar': P_sat,
                'enthalpy_liquid_kj_kg': round(h_liquid, 2),
                'enthalpy_vapor_kj_kg': round(h_vapor, 2),
                'entropy_liquid_kj_kg_k': round(s_liquid, 4),
                'entropy_vapor_kj_kg_k': round(s_vapor, 4),
                'latent_heat_kj_kg': round(latent_heat, 2),
                'source': 'producer_data'
            })
        
        return {
            'status': 'success',
            'fluid_properties': {
                'name': 'Frayo',
                'critical_temperature_celsius': frayo.Tc,
                'critical_pressure_bar': frayo.Pc,
                'critical_enthalpy_kj_kg': frayo.h_crit,
                'critical_entropy_kj_kg_k': frayo.s_crit,
                'molar_mass_g_mol': frayo.M,
                'gas_constant_kj_kg_k': frayo.R,
                'description': 'Fluide frigorigène avec données expérimentales du producteur'
            },
            'producer_data': complete_data,
            'data_info': {
                'source': 'Données expérimentales du producteur',
                'temperature_range': f"{min(frayo.producer_data['temperatures'])}°C à {max(frayo.producer_data['temperatures'])}°C",
                'pressure_range': f"{min(frayo.producer_data['pressures'])} à {max(frayo.producer_data['pressures'])} bar",
                'points_count': len(complete_data)
            }
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Erreur propriétés complètes: {str(e)}'
        }

def get_diagram_specifications():
    """Retourne les spécifications détaillées du diagramme"""
    return {
        'status': 'success',
        'specifications': {
            'title': 'Diagramme de Mollier pour le fluide Frayo – Données du producteur',
            'axes': {
                'x_axis': {
                    'label': 'Entropie spécifique s [kJ/kg·K]',
                    'range': [0.8, 2.4],
                    'unit': 'kJ/kg·K'
                },
                'y_axis': {
                    'label': 'Enthalpie spécifique h [kJ/kg]',
                    'range': [150, 500],
                    'unit': 'kJ/kg'
                }
            },
            'zones': {
                'liquid_subcooled': {
                    'color': '#FFE6E6',
                    'description': 'Zone liquide sous-refroidi',
                    'location': 'À gauche de la courbe de bulle'
                },
                'vapor_superheated': {
                    'color': '#E6F3FF',
                    'description': 'Zone vapeur surchauffée',
                    'location': 'À droite de la courbe de rosée'
                },
                'mixture': {
                    'color': '#F0E6FF',
                    'description': 'Zone mélange liquide + vapeur',
                    'location': 'Entre les courbes de saturation'
                }
            },
            'saturation_curves': {
                'bubble_curve': {
                    'color': '#CC0000',
                    'description': 'Courbe de bulle (liquide)',
                    'line_width': 3
                },
                'dew_curve': {
                    'color': '#0066CC',
                    'description': 'Courbe de rosée (vapeur)',
                    'line_width': 3
                },
                'critical_point': {
                    'visible': True,
                    'annotated': True,
                    'description': 'Point critique bien visible'
                }
            },
            'refrigeration_cycle': {
                'color': '#FF6600',
                'line_width': 4,
                'points': {
                    '1': 'Sortie évaporateur (vapeur surchauffée)',
                    '2': 'Compression',
                    '3': 'Sortie condenseur (liquide)',
                    '4': 'Sortie détendeur (mélange)'
                },
                'arrows': 'Flèches nettes et propres',
                'numbering': 'Points numérotés avec étiquettes encadrées',
                'path_design': 'Lignes évitent le titre du diagramme'
            },
            'additional_elements': {
                'latent_heat_arrow': {
                    'color': '#999999',
                    'description': 'Flèche horizontale pour chaleur latente de vaporisation',
                    'style': 'Flèche bidirectionnelle'
                },
                'isotherms': {
                    'color': '#888888',
                    'style': 'Lignes pointillées',
                    'temperatures': [-20, -10, 0, 10, 20, 30, 40, 50, 60, 80]
                },
                'isobars': {
                    'color': '#AAAAAA',
                    'style': 'Lignes pointillées',
                    'pressures': [1, 2, 5, 10, 15, 20, 25, 30]
                },
                'producer_data_points': {
                    'color': '#FFD700',
                    'marker': 'Square',
                    'description': 'Données expérimentales du producteur'
                }
            },
            'corner_diagrams': {
                'temperature_pressure': {
                    'location': 'Coin supérieur droit',
                    'description': 'Variation de température en fonction de la pression',
                    'data_source': 'Données producteur'
                },
                'experimental_data': {
                    'location': 'Coin supérieur gauche',
                    'description': 'Données expérimentales sous forme de graphe simplifié',
                    'data_source': 'Échantillon mesures producteur'
                }
            },
            'legend': {
                'location': 'À gauche du diagramme principal',
                'content': [
                    'Zones (liquide, vapeur, diphasique)',
                    'Courbes de saturation',
                    'Données réservoir (points jaunes)',
                    'Cycle frigorifique',
                    'Chaleur latente',
                    'Isothermes et isobares'
                ],
                'style': 'Claire et complète'
            },
            'style_general': {
                'responsive': True,
                'scientific': True,
                'readable': True,
                'resolution': '300 DPI haute résolution',
                'background': 'Fond blanc ou très léger dégradé',
                'font': 'Police claire, sans surcharge visuelle'
            }
        }
    }

if __name__ == "__main__":
    # Test de l'API complète
    print("🧪 Test de l'API Diagramme Mollier Complet...")
    
    # Test génération
    result = generate_complete_mollier_api()
    if result['status'] == 'success':
        print("✅ Diagramme complet généré avec succès")
        print(f"📊 Type: {result['metadata']['type']}")
        print(f"📁 Taille: {result['file_info']['size_bytes']} bytes")
        print(f"🎯 Fonctionnalités: {result['metadata']['generation_info']['features_count']}")
    else:
        print(f"❌ Erreur: {result['message']}")
    
    # Test propriétés
    print("\n🔍 Test propriétés complètes...")
    props = get_complete_frayo_properties()
    if props['status'] == 'success':
        print(f"🧊 Propriétés fluide: {props['fluid_properties']['name']}")
        print(f"📈 Points de données: {props['data_info']['points_count']}")
        print(f"🌡️ Plage température: {props['data_info']['temperature_range']}")
    else:
        print(f"❌ Erreur propriétés: {props['message']}")
    
    # Test spécifications
    print("\n📋 Test spécifications...")
    specs = get_diagram_specifications()
    print(f"📊 Titre: {specs['specifications']['title']}")
    print(f"🎨 Zones: {len(specs['specifications']['zones'])}")
    print(f"🔄 Points cycle: {len(specs['specifications']['refrigeration_cycle']['points'])}")
