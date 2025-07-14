"""
Test final du système Mollier Frayo amélioré
Validation de toutes les fonctionnalités pédagogiques
"""

import requests
import json
import time
from datetime import datetime

def test_pedagogical_features():
    """Test des nouvelles fonctionnalités pédagogiques"""
    base_url = "http://localhost:5002"
    results = []
    
    print("🧪 Test du système Mollier Frayo amélioré")
    print("=" * 60)
    
    # Test 1: API diagramme pédagogique
    print("📚 Test API diagramme pédagogique...")
    try:
        response = requests.get(f"{base_url}/api/mollier_pedagogique", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print(f"   ✅ Diagramme pédagogique généré ({len(data.get('diagram_base64', ''))} chars)")
                print(f"   📊 Type: {data.get('metadata', {}).get('type', 'N/A')}")
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
    
    # Test 2: API explication pédagogique
    print("\n📖 Test API explication pédagogique...")
    try:
        response = requests.get(f"{base_url}/api/mollier_explanation", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'titre' in data and 'zones_explication' in data:
                zones_count = len(data.get('zones_explication', {}))
                apps_count = len(data.get('applications', []))
                print(f"   ✅ Explication chargée ({zones_count} zones, {apps_count} applications)")
                results.append(True)
            else:
                print("   ❌ Structure invalide")
                results.append(False)
        else:
            print(f"   ❌ HTTP {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Erreur connexion: {e}")
        results.append(False)
    
    # Test 3: Génération locale pédagogique
    print("\n🏠 Test génération locale pédagogique...")
    try:
        from mollier_pedagogique import MollierDiagramPedagogique
        generator = MollierDiagramPedagogique()
        path, fig = generator.generate_pedagogical_diagram('test_pedagogique.png')
        
        import os
        if os.path.exists(path):
            file_size = os.path.getsize(path)
            print(f"   ✅ Diagramme local généré ({file_size} bytes)")
            results.append(True)
        else:
            print("   ❌ Fichier non créé")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Erreur génération: {e}")
        results.append(False)
    
    # Test 4: Comparaison des versions
    print("\n🔄 Test comparaison versions...")
    try:
        from comparaison_mollier import generate_comparison
        comp_path = generate_comparison()
        
        import os
        if os.path.exists(comp_path):
            file_size = os.path.getsize(comp_path)
            print(f"   ✅ Comparaison générée ({file_size} bytes)")
            results.append(True)
        else:
            print("   ❌ Fichier comparaison non créé")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Erreur comparaison: {e}")
        results.append(False)
    
    # Test 5: Page web améliorée
    print("\n🌐 Test page web améliorée...")
    try:
        response = requests.get(f"{base_url}/mollier-frayo", timeout=10)
        if response.status_code == 200:
            content = response.text
            if "Version Pédagogique" in content and "Explication" in content:
                print("   ✅ Page web mise à jour avec nouvelles fonctionnalités")
                results.append(True)
            else:
                print("   ❌ Fonctionnalités manquantes dans la page")
                results.append(False)
        else:
            print(f"   ❌ HTTP {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Erreur connexion: {e}")
        results.append(False)
    
    # Résumé final
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"📊 Résultats finaux:")
    print(f"   • Tests réussis: {passed}/{total} ({success_rate:.1f}%)")
    
    if passed == total:
        print("🎉 Tous les tests sont passés! Système pédagogique opérationnel!")
        status = "SUCCESS"
    elif passed >= total * 0.8:
        print("✅ Système majoritairement fonctionnel")
        status = "PARTIAL"
    else:
        print("❌ Problèmes détectés - Révision nécessaire")
        status = "FAILED"
    
    # Sauvegarde du rapport
    report = {
        'test_session': {
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'tests_passed': passed,
            'total_tests': total,
            'success_rate': success_rate
        },
        'features_tested': [
            'Diagramme pédagogique simplifié',
            'API explication académique',
            'Génération locale optimisée',
            'Comparaison des versions',
            'Interface web améliorée'
        ]
    }
    
    with open('test_pedagogique_final.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Rapport sauvegardé: test_pedagogique_final.json")
    
    return status == "SUCCESS"

def show_system_summary():
    """Affiche un résumé du système complet"""
    print("\n" + "🎯" * 20)
    print("📋 RÉSUMÉ DU SYSTÈME MOLLIER FRAYO COMPLET")
    print("🎯" * 20)
    
    print("\n📁 Fichiers créés:")
    files = [
        "mollier_diagram_frayo.py - Générateur complet",
        "mollier_pedagogique.py - Version académique simplifiée", 
        "mollier_api.py - API version complète",
        "mollier_pedagogique_api.py - API version pédagogique",
        "comparaison_mollier.py - Comparaison des versions",
        "templates/mollier_frayo.html - Interface web responsive",
        "MOLLIER_FRAYO_GUIDE.md - Documentation complète"
    ]
    
    for i, file in enumerate(files, 1):
        print(f"   {i}. {file}")
    
    print("\n🌐 Endpoints API disponibles:")
    apis = [
        "GET /mollier-frayo - Page web principale",
        "GET /api/mollier_frayo - Diagramme complet",
        "GET /api/mollier_pedagogique - Version pédagogique",
        "GET /api/frayo_properties - Propriétés thermodynamiques",
        "GET /api/mollier_explanation - Explication académique"
    ]
    
    for api in apis:
        print(f"   • {api}")
    
    print("\n✨ Fonctionnalités principales:")
    features = [
        "Diagramme h-s professionnel haute résolution",
        "Version pédagogique style académique",
        "Zones colorées (bleu liquide, rouge vapeur, violet mélange)",
        "Courbes de saturation et point critique",
        "Cycle frigorifique avec compression/expansion",
        "Données réservoir simulées temps réel",
        "Interface web responsive avec téléchargement",
        "Explication pédagogique interactive",
        "Comparaison versions multiples",
        "Export PNG haute résolution (300 DPI)"
    ]
    
    for feature in features:
        print(f"   ✅ {feature}")
    
    print(f"\n🎉 Système prêt pour la production!")
    print(f"🔗 Accès: http://localhost:5002/mollier-frayo")

def main():
    """Fonction principale"""
    print("🧊 TEST FINAL - Système Mollier Frayo Pédagogique")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Tests complets
    success = test_pedagogical_features()
    
    # Résumé du système
    if success:
        show_system_summary()
    
    return success

if __name__ == "__main__":
    main()
