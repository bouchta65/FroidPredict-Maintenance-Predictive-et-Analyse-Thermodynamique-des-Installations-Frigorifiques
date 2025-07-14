"""
Test du système de diagramme de Mollier pour Frayo
Validation complète des fonctionnalités
"""

import requests
import json
import base64
import os
import time
from datetime import datetime

class MollierFrayoTester:
    """Classe de test pour le système Mollier Frayo"""
    
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
        
        # Affichage console
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        duration_str = f" ({duration}ms)" if duration else ""
        print(f"{status_icon} {test_name}: {message}{duration_str}")
        
    def test_local_generation(self):
        """Test de génération locale du diagramme"""
        test_name = "Génération Locale"
        start_time = time.time()
        
        try:
            from mollier_diagram_frayo import MollierDiagramGenerator
            
            generator = MollierDiagramGenerator()
            diagram_path = generator.generate_diagram('test_mollier_frayo.png')
            
            # Vérification du fichier
            if os.path.exists(diagram_path):
                file_size = os.path.getsize(diagram_path)
                duration = int((time.time() - start_time) * 1000)
                self.log_test(test_name, "PASS", 
                            f"Diagramme généré ({file_size} bytes)", duration)
                return True
            else:
                self.log_test(test_name, "FAIL", "Fichier non créé")
                return False
                
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            self.log_test(test_name, "FAIL", f"Erreur: {str(e)}", duration)
            return False
            
    def test_api_mollier(self):
        """Test de l'API de génération Mollier"""
        test_name = "API Mollier"
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.base_url}/api/mollier_frayo", timeout=30)
            duration = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    diagram_size = len(data.get('diagram_base64', ''))
                    self.log_test(test_name, "PASS", 
                                f"API OK ({diagram_size} chars base64)", duration)
                    return True
                else:
                    self.log_test(test_name, "FAIL", 
                                f"Status: {data.get('status')}", duration)
                    return False
            else:
                self.log_test(test_name, "FAIL", 
                            f"HTTP {response.status_code}", duration)
                return False
                
        except requests.exceptions.RequestException as e:
            duration = int((time.time() - start_time) * 1000)
            self.log_test(test_name, "FAIL", f"Connexion: {str(e)}", duration)
            return False
            
    def test_api_properties(self):
        """Test de l'API des propriétés Frayo"""
        test_name = "API Propriétés"
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.base_url}/api/frayo_properties", timeout=10)
            duration = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                if 'fluid_properties' in data and 'saturation_properties' in data:
                    props_count = len(data['saturation_properties'])
                    self.log_test(test_name, "PASS", 
                                f"Propriétés OK ({props_count} points)", duration)
                    return True
                else:
                    self.log_test(test_name, "FAIL", "Structure invalide", duration)
                    return False
            else:
                self.log_test(test_name, "FAIL", 
                            f"HTTP {response.status_code}", duration)
                return False
                
        except requests.exceptions.RequestException as e:
            duration = int((time.time() - start_time) * 1000)
            self.log_test(test_name, "FAIL", f"Connexion: {str(e)}", duration)
            return False
            
    def test_web_page(self):
        """Test de la page web Mollier Frayo"""
        test_name = "Page Web"
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.base_url}/mollier-frayo", timeout=10)
            duration = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                content = response.text
                if "Diagramme de Mollier" in content and "Frayo" in content:
                    page_size = len(content)
                    self.log_test(test_name, "PASS", 
                                f"Page chargée ({page_size} chars)", duration)
                    return True
                else:
                    self.log_test(test_name, "FAIL", "Contenu invalide", duration)
                    return False
            else:
                self.log_test(test_name, "FAIL", 
                            f"HTTP {response.status_code}", duration)
                return False
                
        except requests.exceptions.RequestException as e:
            duration = int((time.time() - start_time) * 1000)
            self.log_test(test_name, "FAIL", f"Connexion: {str(e)}", duration)
            return False
            
    def test_thermodynamic_calculations(self):
        """Test des calculs thermodynamiques"""
        test_name = "Calculs Thermodynamiques"
        start_time = time.time()
        
        try:
            from mollier_diagram_frayo import FrayoProperties
            
            frayo = FrayoProperties()
            
            # Tests de cohérence
            T_test = 20  # °C
            P_sat = frayo.saturation_pressure(T_test)
            T_sat_calc = frayo.saturation_temperature(P_sat)
            
            # Tolérance de 1°C
            if abs(T_test - T_sat_calc) < 1.0:
                duration = int((time.time() - start_time) * 1000)
                self.log_test(test_name, "PASS", 
                            f"Cohérence OK (ΔT={abs(T_test - T_sat_calc):.2f}°C)", duration)
                return True
            else:
                duration = int((time.time() - start_time) * 1000)
                self.log_test(test_name, "FAIL", 
                            f"Incohérence (ΔT={abs(T_test - T_sat_calc):.2f}°C)", duration)
                return False
                
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            self.log_test(test_name, "FAIL", f"Erreur: {str(e)}", duration)
            return False
            
    def test_file_outputs(self):
        """Test des fichiers de sortie"""
        test_name = "Fichiers Sortie"
        start_time = time.time()
        
        try:
            # Vérification des fichiers créés
            files_to_check = [
                'mollier_diagram_frayo.py',
                'mollier_api.py', 
                'templates/mollier_frayo.html',
                'MOLLIER_FRAYO_GUIDE.md'
            ]
            
            missing_files = []
            total_size = 0
            
            for file_path in files_to_check:
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
                else:
                    missing_files.append(file_path)
                    
            if not missing_files:
                duration = int((time.time() - start_time) * 1000)
                self.log_test(test_name, "PASS", 
                            f"Tous fichiers présents ({total_size} bytes)", duration)
                return True
            else:
                duration = int((time.time() - start_time) * 1000)
                self.log_test(test_name, "FAIL", 
                            f"Fichiers manquants: {missing_files}", duration)
                return False
                
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            self.log_test(test_name, "FAIL", f"Erreur: {str(e)}", duration)
            return False
            
    def run_all_tests(self):
        """Exécution de tous les tests"""
        print("🧪 Début des tests du système Mollier Frayo")
        print("=" * 60)
        
        start_time = time.time()
        tests_passed = 0
        total_tests = 0
        
        # Liste des tests à exécuter
        test_methods = [
            self.test_file_outputs,
            self.test_thermodynamic_calculations,
            self.test_local_generation,
            self.test_web_page,
            self.test_api_properties,
            self.test_api_mollier
        ]
        
        for test_method in test_methods:
            total_tests += 1
            if test_method():
                tests_passed += 1
                
        # Résumé
        total_duration = int((time.time() - start_time) * 1000)
        success_rate = (tests_passed / total_tests) * 100
        
        print("=" * 60)
        print(f"📊 Résumé des tests:")
        print(f"   • Tests réussis: {tests_passed}/{total_tests} ({success_rate:.1f}%)")
        print(f"   • Durée totale: {total_duration}ms")
        
        if tests_passed == total_tests:
            print("🎉 Tous les tests sont passés avec succès!")
            status = "SUCCESS"
        else:
            print("⚠️ Certains tests ont échoué")
            status = "PARTIAL"
            
        # Sauvegarde du rapport
        self.save_test_report(status, tests_passed, total_tests, total_duration)
        
        return tests_passed == total_tests
        
    def save_test_report(self, status, passed, total, duration):
        """Sauvegarde du rapport de test"""
        report = {
            'test_session': {
                'timestamp': datetime.now().isoformat(),
                'status': status,
                'tests_passed': passed,
                'total_tests': total,
                'duration_ms': duration,
                'success_rate': (passed / total) * 100
            },
            'test_results': self.test_results
        }
        
        with open('mollier_frayo_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"📄 Rapport sauvegardé: mollier_frayo_test_report.json")

def main():
    """Fonction principale de test"""
    print("🧊 Test du Système Diagramme de Mollier Frayo")
    print(f"⏰ Démarrage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = MollierFrayoTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Système opérationnel - Prêt pour la production!")
    else:
        print("\n❌ Des problèmes ont été détectés - Vérifier les logs")
        
    return success

if __name__ == "__main__":
    main()
