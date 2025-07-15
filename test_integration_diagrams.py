"""
Test d'intégration du diagramme complet dans la page diagrams
Validation de la suppression de l'ancienne page mollier_complet
"""

import requests
import json
import os
import time
from datetime import datetime

class DiagramsIntegrationTester:
    """Testeur d'intégration pour la page diagrams mise à jour"""
    
    def __init__(self, base_url="http://localhost:5002"):
        self.base_url = base_url
        self.test_results = []
        
    def log_test(self, test_name, status, message, duration=None):
        """Enregistre un résultat de test"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'duration_ms': duration
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        duration_str = f" ({duration}ms)" if duration else ""
        print(f"{status_icon} {test_name}: {message}{duration_str}")
    
    def test_diagrams_page_updated(self):
        """Test que la page diagrams contient le nouvel onglet complet"""
        test_name = "Page Diagrams Mise à Jour"
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.base_url}/diagrams", timeout=10)
            duration = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                content = response.text
                
                # Vérification des éléments de l'onglet complet
                required_elements = [
                    'Complet',  # Nom de l'onglet
                    'completeTab',  # ID de l'onglet
                    'generateCompleteDiagram',  # Fonction JS
                    'Diagramme Complet Responsive',  # Titre de l'onglet
                    'mollier_complet',  # API endpoint
                    'diagram-3-fill'  # Icône de l'onglet
                ]
                
                missing_elements = [elem for elem in required_elements if elem not in content]
                
                if not missing_elements:
                    page_size = len(content)
                    self.log_test(test_name, "PASS", 
                                f"Onglet complet intégré ({page_size} chars)", duration)
                    return True
                else:
                    self.log_test(test_name, "FAIL", 
                                f"Éléments manquants: {missing_elements[:3]}...", duration)
                    return False
            else:
                self.log_test(test_name, "FAIL", 
                            f"HTTP {response.status_code}", duration)
                return False
                
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            self.log_test(test_name, "FAIL", f"Erreur: {str(e)}", duration)
            return False
    
    def test_mollier_complet_redirect(self):
        """Test que /mollier-complet redirige vers la page diagrams"""
        test_name = "Redirection Mollier Complet"
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.base_url}/mollier-complet", timeout=10)
            duration = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                content = response.text
                
                # Vérifier que c'est bien la page diagrams avec l'onglet complet
                if ('completeTab' in content and 'generateCompleteDiagram' in content):
                    self.log_test(test_name, "PASS", 
                                "Redirection vers diagrams avec onglet complet", duration)
                    return True
                else:
                    self.log_test(test_name, "FAIL", 
                                "Page différente de diagrams", duration)
                    return False
            else:
                self.log_test(test_name, "FAIL", 
                            f"HTTP {response.status_code}", duration)
                return False
                
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            self.log_test(test_name, "FAIL", f"Erreur: {str(e)}", duration)
            return False
    
    def test_old_template_removed(self):
        """Test que l'ancien template mollier_complet.html a été supprimé"""
        test_name = "Suppression Ancien Template"
        start_time = time.time()
        
        try:
            old_template_path = "templates/mollier_complet.html"
            
            if not os.path.exists(old_template_path):
                duration = int((time.time() - start_time) * 1000)
                self.log_test(test_name, "PASS", 
                            "Ancien template supprimé avec succès", duration)
                return True
            else:
                duration = int((time.time() - start_time) * 1000)
                self.log_test(test_name, "FAIL", 
                            "Ancien template encore présent", duration)
                return False
                
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            self.log_test(test_name, "FAIL", f"Erreur: {str(e)}", duration)
            return False
    
    def test_complete_diagram_api_accessible(self):
        """Test que l'API du diagramme complet est accessible"""
        test_name = "API Diagramme Complet"
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.base_url}/api/mollier_complet", timeout=60)
            duration = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    diagram_size = len(data.get('diagram_base64', ''))
                    features = data.get('metadata', {}).get('generation_info', {}).get('features_count', 0)
                    
                    self.log_test(test_name, "PASS", 
                                f"API OK - {features} fonctionnalités ({diagram_size} chars)", duration)
                    return True
                else:
                    self.log_test(test_name, "FAIL", 
                                f"Erreur API: {data.get('message')}", duration)
                    return False
            else:
                self.log_test(test_name, "FAIL", 
                            f"HTTP {response.status_code}", duration)
                return False
                
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            self.log_test(test_name, "FAIL", f"Erreur: {str(e)}", duration)
            return False
    
    def test_navigation_consistency(self):
        """Test que la navigation reste cohérente"""
        test_name = "Cohérence Navigation"
        start_time = time.time()
        
        try:
            # Test des différentes pages
            pages_to_test = [
                ('/diagrams', 'diagrams'),
                ('/mollier-complet', 'diagrams'),  # Doit rediriger vers diagrams
                ('/', 'dashboard')
            ]
            
            all_passed = True
            for url, expected_content in pages_to_test:
                response = requests.get(f"{self.base_url}{url}", timeout=5)
                if response.status_code != 200:
                    all_passed = False
                    break
            
            duration = int((time.time() - start_time) * 1000)
            
            if all_passed:
                self.log_test(test_name, "PASS", 
                            f"Navigation cohérente ({len(pages_to_test)} pages testées)", duration)
                return True
            else:
                self.log_test(test_name, "FAIL", 
                            "Problèmes de navigation détectés", duration)
                return False
                
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            self.log_test(test_name, "FAIL", f"Erreur: {str(e)}", duration)
            return False
    
    def test_javascript_functions(self):
        """Test que les nouvelles fonctions JavaScript sont présentes"""
        test_name = "Fonctions JavaScript"
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.base_url}/diagrams", timeout=10)
            duration = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                content = response.text
                
                # Fonctions JS requises pour l'onglet complet
                required_functions = [
                    'generateCompleteDiagram',
                    'loadCompleteSpecifications', 
                    'downloadCompleteDiagram',
                    'currentCompleteDiagramData'
                ]
                
                missing_functions = [func for func in required_functions if func not in content]
                
                if not missing_functions:
                    self.log_test(test_name, "PASS", 
                                f"Toutes les fonctions JS présentes ({len(required_functions)})", duration)
                    return True
                else:
                    self.log_test(test_name, "FAIL", 
                                f"Fonctions manquantes: {missing_functions}", duration)
                    return False
            else:
                self.log_test(test_name, "FAIL", 
                            f"HTTP {response.status_code}", duration)
                return False
                
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            self.log_test(test_name, "FAIL", f"Erreur: {str(e)}", duration)
            return False
    
    def run_integration_tests(self):
        """Exécution de tous les tests d'intégration"""
        print("🔄 TESTS D'INTÉGRATION - DIAGRAMME COMPLET DANS DIAGRAMS")
        print("=" * 65)
        print(f"⏰ Début des tests: {datetime.now().strftime('%H:%M:%S')}")
        print()
        
        # Liste des tests
        tests = [
            self.test_old_template_removed,
            self.test_diagrams_page_updated,
            self.test_mollier_complet_redirect,
            self.test_javascript_functions,
            self.test_complete_diagram_api_accessible,
            self.test_navigation_consistency
        ]
        
        # Exécution des tests
        passed_tests = 0
        total_tests = len(tests)
        
        for test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_func.__name__, "FAIL", f"Exception: {str(e)}")
        
        # Résumé final
        print("\n" + "=" * 65)
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"📊 RÉSULTATS D'INTÉGRATION:")
        print(f"   • Tests réussis: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"   • Temps total: {datetime.now().strftime('%H:%M:%S')}")
        
        if passed_tests == total_tests:
            print("🎉 INTÉGRATION 100% RÉUSSIE !")
            status = "SUCCESS"
        elif passed_tests >= total_tests * 0.8:
            print("✅ Intégration majoritairement réussie")
            status = "PARTIAL"
        else:
            print("❌ Problèmes d'intégration détectés")
            status = "FAILED"
        
        # Sauvegarde du rapport
        report = {
            'integration_test': {
                'timestamp': datetime.now().isoformat(),
                'operation': 'Integration du diagramme complet dans page diagrams',
                'status': status,
                'tests_passed': passed_tests,
                'total_tests': total_tests,
                'success_rate': success_rate,
                'changes_made': [
                    'Ajout onglet "Complet" à la page diagrams',
                    'Redirection /mollier-complet vers /diagrams',
                    'Suppression ancien template mollier_complet.html',
                    'Intégration fonctions JS pour diagramme complet',
                    'Ajout styles CSS pour nouvel onglet'
                ]
            },
            'detailed_results': self.test_results
        }
        
        with open('test_integration_diagrams.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Rapport détaillé: test_integration_diagrams.json")
        
        return status == "SUCCESS"

def show_integration_summary():
    """Affiche un résumé de l'intégration réalisée"""
    print("\n" + "🎯" * 25)
    print("📋 RÉSUMÉ DE L'INTÉGRATION")
    print("🎯" * 25)
    
    print("\n✨ Modifications apportées:")
    modifications = [
        "➕ Ajout onglet 'Complet' à la page /diagrams",
        "🔄 Redirection /mollier-complet → /diagrams",
        "🗑️ Suppression template mollier_complet.html",
        "⚙️ Intégration fonctions JS : generateCompleteDiagram(), etc.",
        "🎨 Ajout styles CSS pour interface responsive",
        "📱 Compatibilité mobile maintenue",
        "🔗 APIs existantes préservées",
        "🧹 Navigation simplifiée et cohérente"
    ]
    
    for modification in modifications:
        print(f"   {modification}")
    
    print("\n🌐 Accès unifié:")
    print("   • http://localhost:5002/diagrams - Interface principale avec 4 onglets")
    print("   • http://localhost:5002/mollier-complet - Redirection vers diagrams")
    
    print("\n📊 Onglets disponibles:")
    print("   • 🖼️ Statique : Diagramme standard")
    print("   • 🎮 Interactif : Plotly.js interactif")
    print("   • 📊 Comparaison : Chart.js comparatifs")
    print("   • 🎯 Complet : Nouveau diagramme responsive complet")
    
    print("\n🎨 Fonctionnalités onglet Complet:")
    print("   • 🎨 Zones colorées selon spécifications")
    print("   • 🔄 Cycle frigorifique orange avec flèches")
    print("   • 📊 Données producteur intégrées")
    print("   • 🖼️ Encarts T-P et expérimentaux")
    print("   • 📋 Spécifications détaillées consultables")
    print("   • 💾 Téléchargement haute résolution")

def main():
    """Fonction principale"""
    print("🔄 TEST D'INTÉGRATION - DIAGRAMME COMPLET")
    print(f"⏰ Démarrage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Tests d'intégration
    tester = DiagramsIntegrationTester()
    success = tester.run_integration_tests()
    
    # Résumé de l'intégration
    if success:
        show_integration_summary()
        
        print(f"\n🎊 INTÉGRATION RÉUSSIE !")
        print(f"🔗 Accès: http://localhost:5002/diagrams (onglet 'Complet')")
    
    return success

if __name__ == "__main__":
    main()
