"""
API pour le diagramme de Mollier pédagogique
Version simplifiée pour usage académique
"""

from mollier_pedagogique import MollierDiagramPedagogique
import base64
import io
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif
import matplotlib.pyplot as plt

def generate_pedagogical_mollier_api():
    """Génère le diagramme pédagogique et retourne les données API"""
    try:
        # Création du générateur pédagogique
        generator = MollierDiagramPedagogique()
        
        # Génération en mémoire
        fig, ax = generator.create_simplified_diagram()
        s_liquid, h_liquid, s_vapor, h_vapor, s_crit, h_crit = generator.create_saturation_curves(ax)
        generator.create_zones(ax, s_liquid, h_liquid, s_vapor, h_vapor)
        generator.add_latent_heat_arrow(ax)
        generator.add_temperature_lines(ax)
        generator.add_pressure_lines(ax)
        generator.finalize_diagram(ax)
        
        # Conversion en base64
        buffer = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        
        diagram_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        
        # Métadonnées pédagogiques
        metadata = {
            'type': 'Diagramme de Mollier Pédagogique',
            'fluid': 'Frayo',
            'style': 'Académique simplifié',
            'zones': {
                'liquide': 'Rouge clair - Liquide sous-refroidi',
                'mélange': 'Violet clair - Mélange liquide-vapeur',
                'vapeur': 'Bleu clair - Vapeur surchauffée'
            },
            'courbes': {
                'liquide_sature': 'Rouge - Courbe de bulle',
                'vapeur_sature': 'Bleu - Courbe de rosée'
            },
            'elements_pedagogiques': [
                'Point critique clairement identifié',
                'Flèche chaleur latente de vaporisation',
                'Isothermes de référence (0°C, 20°C, 40°C)',
                'Isobares de référence (2, 5, 10 bar)',
                'Zones colorées distinctes',
                'Labels explicites pour chaque zone'
            ],
            'usage': 'Cours, présentations, manuels académiques'
        }
        
        return {
            'status': 'success',
            'diagram_base64': diagram_base64,
            'metadata': metadata,
            'mime_type': 'image/png',
            'resolution': '300 DPI',
            'background': 'Blanc'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Erreur génération diagramme pédagogique: {str(e)}'
        }

def get_pedagogical_explanation():
    """Retourne une explication pédagogique du diagramme"""
    return {
        'titre': 'Diagramme de Mollier (h-s) - Explication pédagogique',
        'description': 'Le diagramme de Mollier représente les propriétés thermodynamiques d\'un fluide en fonction de son enthalpie (h) et de son entropie (s).',
        'axes': {
            'x': 'Entropie spécifique s [kJ/kg·K] - Mesure du désordre moléculaire',
            'y': 'Enthalpie spécifique h [kJ/kg] - Énergie thermique totale par unité de masse'
        },
        'zones_explication': {
            'liquide': {
                'position': 'À gauche du dôme',
                'couleur': 'Rouge clair',
                'etat': 'Liquide sous-refroidi',
                'description': 'Le fluide est entièrement liquide, à une température inférieure à la température de saturation'
            },
            'mélange': {
                'position': 'Sous le dôme',
                'couleur': 'Violet clair', 
                'etat': 'Mélange liquide-vapeur',
                'description': 'Coexistence des phases liquide et vapeur à la même température et pression'
            },
            'vapeur': {
                'position': 'À droite du dôme',
                'couleur': 'Bleu clair',
                'etat': 'Vapeur surchauffée',
                'description': 'Le fluide est entièrement gazeux, à une température supérieure à la température de saturation'
            }
        },
        'courbes_importantes': {
            'courbe_bulle': 'Limite gauche du dôme - Début de la vaporisation',
            'courbe_rosee': 'Limite droite du dôme - Fin de la condensation',
            'point_critique': 'Sommet du dôme - Au-delà, plus de distinction liquide/vapeur'
        },
        'applications': [
            'Analyse des cycles thermodynamiques',
            'Calcul des bilans énergétiques',
            'Optimisation des systèmes frigorifiques',
            'Enseignement de la thermodynamique'
        ]
    }

if __name__ == "__main__":
    # Test de l'API pédagogique
    print("📚 Test API Diagramme Pédagogique...")
    
    result = generate_pedagogical_mollier_api()
    if result['status'] == 'success':
        print("✅ Diagramme pédagogique généré")
        print(f"📊 Type: {result['metadata']['type']}")
        print(f"📁 Taille: {len(result['diagram_base64'])} caractères")
        
        explanation = get_pedagogical_explanation()
        print(f"\n📖 Explication: {explanation['titre']}")
        print(f"🎯 Applications: {len(explanation['applications'])} domaines")
    else:
        print(f"❌ Erreur: {result['message']}")
