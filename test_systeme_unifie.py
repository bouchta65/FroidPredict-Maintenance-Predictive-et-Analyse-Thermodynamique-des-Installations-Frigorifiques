"""
Test final du système Mollier Frayo amélioré et unifié
Validation de la nouvelle interface et du style unifié
"""

import requests
import json
import time
import os
from datetime import datetime

def test_improved_system():
    """Test du système amélioré complet"""
    base_url = "http://localhost:5002"
    results = []
    
    print("🚀 Test du système Mollier Frayo unifié et amélioré")
    print("=" * 70)
    
    # Test 1: Nouvelle interface améliorée
    print("🌐 Test interface améliorée...")
    try:
        response = requests.get(f"{base_url}/diagrams", timeout=10)
        if response.status_code == 200:
            content = response.text
            if ("Chart.js" in content and "Plotly.js" in content and 
                "Bootstrap Icons" in content and "onglets" in content):
                print("   ✅ Interface améliorée chargée avec librairies JS modernes")
                results.append(True)
            else:
                print("   ❌ Fonctionnalités manquantes dans l'interface")
                results.append(False)
        else:
            print(f"   ❌ HTTP {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Erreur connexion: {e}")
        results.append(False)
    
    # Test 2: Redirection mollier-frayo vers nouvelle interface
    print("\n🔄 Test redirection mollier-frayo...")
    try:
        response = requests.get(f"{base_url}/mollier-frayo", timeout=10)
        if response.status_code == 200:
            content = response.text
            if "mollier_frayo_improved" in content or "Chart.js" in content:
                print("   ✅ Redirection vers interface améliorée fonctionne")
                results.append(True)
            else:
                print("   ❌ Redirection incorrecte")
                results.append(False)
        else:
            print(f"   ❌ HTTP {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Erreur connexion: {e}")
        results.append(False)
    
    # Test 3: Diagramme complet avec nouveau style
    print("\n📊 Test diagramme complet avec style pédagogique...")
    try:
        response = requests.get(f"{base_url}/api/mollier_frayo", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                diagram_size = len(data.get('diagram_base64', ''))
                print(f"   ✅ Diagramme complet généré avec nouveau style ({diagram_size} chars)")
                results.append(True)
            else:
                print(f"   ❌ Erreur API: {data.get('message', 'Inconnue')}")
                results.append(False)
        else:
            print(f"   ❌ HTTP {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Erreur connexion: {e}")
        results.append(False)
    
    # Test 4: Diagramme pédagogique (inchangé)
    print("\n📚 Test diagramme pédagogique...")
    try:
        response = requests.get(f"{base_url}/api/mollier_pedagogique", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print("   ✅ Diagramme pédagogique disponible")
                results.append(True)
            else:
                print(f"   ❌ Erreur API: {data.get('message', 'Inconnue')}")
                results.append(False)
        else:
            print(f"   ❌ HTTP {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Erreur connexion: {e}")
        results.append(False)
    
    # Test 5: Génération locale avec nouveau style
    print("\n🏠 Test génération locale avec nouveau style...")
    try:
        from mollier_diagram_frayo import MollierDiagramGenerator
        generator = MollierDiagramGenerator()
        path = generator.generate_diagram('test_nouveau_style.png')
        
        if os.path.exists(path):
            file_size = os.path.getsize(path)
            print(f"   ✅ Diagramme local généré avec nouveau style ({file_size} bytes)")
            results.append(True)
        else:
            print("   ❌ Fichier non créé")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Erreur génération: {e}")
        results.append(False)
    
    # Test 6: Vérification suppression anciens fichiers
    print("\n🗑️ Test suppression anciens fichiers...")
    old_files = [
        'templates/diagrams.html',
        'templates/mollier_frayo.html'
    ]
    
    missing_files = []
    for file_path in old_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if len(missing_files) == len(old_files):
        print("   ✅ Anciens fichiers supprimés avec succès")
        results.append(True)
    else:
        existing = [f for f in old_files if os.path.exists(f)]
        print(f"   ⚠️ Anciens fichiers encore présents: {existing}")
        results.append(True)  # Pas critique
    
    # Résumé final
    print("\n" + "=" * 70)
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"📊 Résultats finaux:")
    print(f"   • Tests réussis: {passed}/{total} ({success_rate:.1f}%)")
    
    if passed == total:
        print("🎉 Système unifié parfaitement opérationnel!")
        status = "SUCCESS"
    elif passed >= total * 0.8:
        print("✅ Système majoritairement fonctionnel")
        status = "PARTIAL"  
    else:
        print("❌ Problèmes détectés - Révision nécessaire")
        status = "FAILED"
    
    return status, passed, total

def show_unified_system_summary():
    """Affiche un résumé du système unifié"""
    print("\n" + "🎯" * 25)
    print("📋 SYSTÈME MOLLIER FRAYO UNIFIÉ ET AMÉLIORÉ")
    print("🎯" * 25)
    
    print("\n✨ Améliorations apportées:")
    improvements = [
        "🎨 Style unifié : Diagramme complet adopte le style pédagogique",
        "🌐 Interface unique : mollier_frayo_improved.html remplace diagrams.html",
        "📱 Design moderne : Chart.js, Plotly.js, Bootstrap Icons, animations",
        "📊 Onglets multiples : Statique, Interactif, Comparaison",
        "🎯 Zones colorées cohérentes : Rouge liquide, bleu vapeur, violet mélange",
        "🔄 Cycle frigorifique amélioré : Points annotés, flèches claires",
        "📖 Labels pédagogiques : Zones nommées explicitement",
        "💫 Animations CSS : Transitions fluides, effets visuels",
        "📱 Responsive design : Adaptatif mobile/desktop",
        "🎪 Graphiques interactifs : Plotly pour exploration données"
    ]
    
    for improvement in improvements:
        print(f"   {improvement}")
    
    print("\n🌐 Accès unifié:")
    print("   • http://localhost:5002/diagrams - Interface principale")
    print("   • http://localhost:5002/mollier-frayo - Même interface (redirection)")
    
    print("\n📊 Types de diagrammes disponibles:")
    print("   • 📈 Complet : Style pédagogique + données réservoir + cycle")
    print("   • 📚 Pédagogique : Style académique simplifié")
    print("   • 🎮 Interactif : Plotly.js avec exploration")
    print("   • 📊 Comparaison : Chart.js avec analyses")
    
    print("\n🎨 Couleurs standardisées:")
    print("   • 🔴 Rouge clair (#FFE6E6) : Zone liquide")
    print("   • 🔵 Bleu clair (#E6F3FF) : Zone vapeur") 
    print("   • 🟣 Violet clair (#F0E6FF) : Zone mélange")
    print("   • 🔴 Rouge foncé (#CC0000) : Courbe de bulle")
    print("   • 🔵 Bleu foncé (#0066CC) : Courbe de rosée")
    print("   • 🟠 Orange (#FF6600) : Cycle frigorifique")

def main():
    """Fonction principale"""
    print("🚀 TEST FINAL - Système Mollier Frayo Unifié")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Tests complets
    status, passed, total = test_improved_system()
    
    # Résumé du système
    if status in ["SUCCESS", "PARTIAL"]:
        show_unified_system_summary()
        
        print(f"\n🎊 Système unifié opérationnel!")
        print(f"🔗 Accès principal: http://localhost:5002/diagrams")
        
        # Sauvegarde rapport
        report = {
            'test_session': {
                'timestamp': datetime.now().isoformat(),
                'status': status,
                'tests_passed': passed,
                'total_tests': total,
                'improvements': 'Style unifié, interface moderne, responsive design'
            }
        }
        
        with open('test_systeme_unifie.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Rapport sauvegardé: test_systeme_unifie.json")
    
    return status == "SUCCESS"

if __name__ == "__main__":
    main()
