"""
Script de comparaison des diagrammes de Mollier
Version complète vs Version pédagogique
"""

import matplotlib.pyplot as plt
from mollier_diagram_frayo import MollierDiagramGenerator
from mollier_pedagogique import MollierDiagramPedagogique

def generate_comparison():
    """Génère une comparaison des deux versions"""
    
    # Configuration pour 2 sous-graphiques
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8), dpi=300)
    fig.suptitle('Comparaison des Diagrammes de Mollier pour Frayo', 
                fontsize=18, fontweight='bold')
    
    print("🔄 Génération du diagramme complet...")
    
    # Diagramme complet (version simplifiée pour comparaison)
    try:
        # Version simplifiée du diagramme complet
        ax1.set_title('Version Complète\n(Avec données réservoir et cycle)', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Entropie spécifique s [kJ/kg·K]', fontsize=12)
        ax1.set_ylabel('Enthalpie spécifique h [kJ/kg]', fontsize=12)
        
        # Simulation courbes de saturation
        import numpy as np
        s_liquid = np.linspace(1.0, 1.55, 20)
        h_liquid = 200 + 70 * (s_liquid - 1.0) / 0.55
        s_vapor = np.linspace(1.55, 2.1, 20)
        h_vapor = 310 + 110 * (s_vapor - 1.55) / 0.55
        
        # Tracé courbes
        ax1.plot(s_liquid, h_liquid, 'r-', linewidth=2, label='Liquide saturé')
        ax1.plot(s_vapor, h_vapor, 'b-', linewidth=2, label='Vapeur saturée')
        
        # Zones
        ax1.fill_between(s_liquid, 150, h_liquid, alpha=0.3, color='red', label='Zone liquide')
        ax1.fill_between(s_vapor, h_vapor, 450, alpha=0.3, color='blue', label='Zone vapeur')
        
        # Simulation cycle frigorifique
        cycle_s = [1.8, 1.8, 1.3, 1.6, 1.8]
        cycle_h = [350, 400, 280, 300, 350]
        ax1.plot(cycle_s, cycle_h, 'k-', linewidth=3, alpha=0.8, label='Cycle frigorifique')
        
        # Simulation points réservoir
        np.random.seed(42)
        s_data = np.random.uniform(1.1, 2.0, 25)
        h_data = np.random.uniform(250, 380, 25)
        ax1.scatter(s_data, h_data, c='gold', s=20, alpha=0.7, label='Données réservoir')
        
        ax1.set_xlim(0.9, 2.2)
        ax1.set_ylim(150, 450)
        ax1.grid(True, alpha=0.3)
        ax1.legend(fontsize=10)
        
    except Exception as e:
        print(f"Erreur diagramme complet: {e}")
    
    print("📚 Génération du diagramme pédagogique...")
    
    # Diagramme pédagogique
    try:
        generator_pedago = MollierDiagramPedagogique()
        
        ax2.set_title('Version Pédagogique\n(Style académique simplifié)', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Entropie spécifique s [kJ/kg·K]', fontsize=12)
        ax2.set_ylabel('Enthalpie spécifique h [kJ/kg]', fontsize=12)
        
        # Création des éléments pédagogiques
        s_liquid = np.array([1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.55])
        h_liquid = np.array([200, 220, 240, 260, 280, 300, 310])
        s_vapor = np.array([1.55, 1.65, 1.75, 1.85, 1.95, 2.05, 2.1])
        h_vapor = np.array([310, 330, 350, 370, 390, 410, 420])
        
        # Courbes de saturation
        ax2.plot(s_liquid, h_liquid, color='#CC0000', linewidth=3, label='Courbe de bulle')
        ax2.plot(s_vapor, h_vapor, color='#0066CC', linewidth=3, label='Courbe de rosée')
        
        # Point critique
        ax2.plot(1.55, 310, 'o', color='#FF6600', markersize=8)
        ax2.text(1.55, 325, 'Point\ncritique', ha='center', fontsize=10, fontweight='bold')
        
        # Zones colorées
        liquid_vertices = np.array([[0.8, 150], [1.0, 150], [1.55, 310], [0.8, 310]])
        vapor_vertices = np.array([[2.1, 420], [2.3, 420], [2.3, 450], [2.1, 450]])
        
        ax2.fill(liquid_vertices[:, 0], liquid_vertices[:, 1], 
                color='#FFE6E6', alpha=0.7, label='Zone liquide')
        ax2.fill(vapor_vertices[:, 0], vapor_vertices[:, 1], 
                color='#E6F3FF', alpha=0.7, label='Zone vapeur')
        
        # Zone mélange
        mixture_vertices = np.concatenate([
            np.column_stack([s_liquid, h_liquid]),
            np.column_stack([s_vapor[::-1], h_vapor[::-1]])
        ])
        ax2.fill(mixture_vertices[:, 0], mixture_vertices[:, 1], 
                color='#F0E6FF', alpha=0.7, label='Zone mélange')
        
        # Labels des zones
        ax2.text(1.0, 250, 'LIQUIDE', fontsize=11, fontweight='bold', 
                color='#CC0000', ha='center')
        ax2.text(1.75, 350, 'LIQUIDE\n+\nVAPEUR', fontsize=11, fontweight='bold', 
                color='purple', ha='center')
        ax2.text(2.15, 400, 'VAPEUR', fontsize=11, fontweight='bold', 
                color='#0066CC', ha='center')
        
        # Flèche chaleur latente
        ax2.annotate('', xy=(1.9, 270), xytext=(1.2, 270),
                    arrowprops=dict(arrowstyle='<->', lw=2, color='#666666'))
        ax2.text(1.55, 285, 'Chaleur latente', fontsize=10, ha='center', 
                color='#666666', fontweight='bold')
        
        ax2.set_xlim(0.8, 2.3)
        ax2.set_ylim(150, 450)
        ax2.grid(True, alpha=0.3)
        ax2.legend(fontsize=10)
        
    except Exception as e:
        print(f"Erreur diagramme pédagogique: {e}")
    
    # Sauvegarde
    plt.tight_layout()
    plt.savefig('comparaison_mollier_frayo.png', dpi=300, bbox_inches='tight', 
               facecolor='white', edgecolor='none')
    
    print("✅ Comparaison sauvegardée: comparaison_mollier_frayo.png")
    
    # Affichage
    plt.show()
    
    return 'comparaison_mollier_frayo.png'

def main():
    """Fonction principale"""
    print("🔄 Génération de la comparaison des diagrammes...")
    
    try:
        path = generate_comparison()
        
        print("\n📊 Comparaison générée avec succès!")
        print("🎯 Différences principales:")
        print("   • Version complète: Données réservoir + cycle complet")
        print("   • Version pédagogique: Style académique simplifié")
        print("   • Même fluide Frayo, présentation adaptée à l'usage")
        print(f"📁 Fichier: {path}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()
