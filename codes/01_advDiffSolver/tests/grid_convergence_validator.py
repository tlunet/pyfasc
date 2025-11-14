"""
Grid Convergence Test für numerische Validierung
Testet die Konvergenzordnung des Algorithmus über verschiedene Gittergrößen
"""
import os
import tempfile
import subprocess
import shutil
import numpy as np
import platform
import sys

def run_program_with_grid(code, language, filename, grid_size):
    """Führt das Programm mit einer bestimmten Gittergröße aus"""
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Modifiziere Code um Ausgabe zu schreiben (für Python)
            if language == 'python':
                # Füge Code zum Schreiben der Lösung hinzu
                modified_code = code.replace(
                    "# Simulation\np = Problem",
                    "# Simulation\nimport numpy as np\np = Problem"
                )
                # Füge am Ende Code zum Speichern hinzu
                if "np.savetxt" not in modified_code and "write(" not in modified_code:
                    modified_code = modified_code.rstrip() + "\n\n# Speichere Lösung für Validierung\nnp.savetxt('uEnd.txt', p.u[2:-2, 2:-2])\n"
            else:
                modified_code = code
            
            # Schreibe Code in temporäre Datei
            code_file = os.path.join(temp_dir, filename)
            with open(code_file, 'w') as f:
                f.write(modified_code)
            
            # Erstelle input.txt mit spezifischer Gittergröße
            # Format: nX nY initType flowType viscosity tEnd nSteps
            input_file = os.path.join(temp_dir, "input.txt")
            with open(input_file, 'w') as f:
                # Verwende einfache Konfiguration für Konvergenztest
                # Gauss-Puls mit nur Diffusion (keine Advektion)
                f.write(f"{grid_size} {grid_size} gauss diagonal 0.001 0.1 100\n")
            
            # Wechsle in temp_dir
            old_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                if language == 'python':
                    python_path = sys.executable
                    result = subprocess.run([python_path, filename], 
                                          capture_output=True, text=True, timeout=60)
                elif language == 'cpp':
                    exe_name = "program.exe" if platform.system() == "Windows" else "program"
                    exe_run = exe_name if platform.system() == "Windows" else "./program"
                    
                    # Find compiler
                    if shutil.which("g++"):
                        compiler = "g++"
                    elif shutil.which("clang++"):
                        compiler = "clang++"
                    elif platform.system() == "Windows" and shutil.which("cl"):
                        compiler = "cl"
                    else:
                        return None, "Kein C++ Compiler gefunden"
                    
                    # Kompiliere
                    if compiler in ["g++", "clang++"]:
                        compile_result = subprocess.run([compiler, '-O2', '-o', exe_name, filename], 
                                                      capture_output=True, text=True, timeout=30)
                    else:  # MSVC
                        compile_result = subprocess.run([compiler, '/O2', '/Fe:' + exe_name, filename], 
                                                      capture_output=True, text=True, timeout=30)
                    
                    if compile_result.returncode != 0:
                        return None, f"Kompilierfehler: {compile_result.stderr}"
                    
                    # Führe aus
                    result = subprocess.run([exe_run], 
                                          capture_output=True, text=True, timeout=60)
                
                elif language == 'julia':
                    result = subprocess.run(['julia', filename], 
                                          capture_output=True, text=True, timeout=60)
                else:
                    return None, f"Nicht unterstützte Sprache: {language}"
                
                if result.returncode != 0:
                    return None, f"Runtime-Fehler: {result.stderr}"
                
                # Lese uEnd.txt
                if not os.path.exists("uEnd.txt"):
                    return None, "uEnd.txt nicht gefunden"
                
                solution = np.loadtxt("uEnd.txt")
                
                if solution.shape != (grid_size, grid_size):
                    return None, f"Falsche Ausgabegröße: {solution.shape} statt ({grid_size}, {grid_size})"
                
                # Prüfe auf NaN/Inf
                if np.any(np.isnan(solution)) or np.any(np.isinf(solution)):
                    return None, "NaN oder Inf in Lösung gefunden"
                
                return solution, None
                
            finally:
                os.chdir(old_cwd)
                
        except subprocess.TimeoutExpired:
            return None, "Timeout"
        except Exception as e:
            return None, f"Fehler: {str(e)}"


def compute_reference_solution(grid_size):
    """
    Berechnet eine hochaufgelöste Referenzlösung
    Diese dient als "exakte" Lösung für den Konvergenztest
    """
    # Für den Konvergenztest verwenden wir die feinste Gitterlösung als Referenz
    # In der Praxis: Dies sollte eine sehr feine Lösung sein (z.B. 256x256 oder 512x512)
    return None


def interpolate_solution(solution, target_size):
    """Interpoliert die Lösung auf eine Zielgröße für Vergleiche"""
    from scipy.interpolate import RectBivariateSpline
    
    n = solution.shape[0]
    x = np.linspace(0, 1, n)
    y = np.linspace(0, 1, n)
    
    # Erstelle Interpolator
    interp = RectBivariateSpline(x, y, solution, kx=3, ky=3)
    
    # Interpoliere auf Zielgröße
    x_new = np.linspace(0, 1, target_size)
    y_new = np.linspace(0, 1, target_size)
    
    return interp(x_new, y_new)


def compute_convergence_order(grid_sizes, errors):
    """
    Berechnet die Konvergenzordnung aus Gittergrößen und Fehlern
    
    Theorie: error ≈ C * h^p
    => log(error) ≈ log(C) + p * log(h)
    => p = (log(error2) - log(error1)) / (log(h2) - log(h1))
    """
    log_h = np.log(1.0 / np.array(grid_sizes))
    log_errors = np.log(errors)
    
    # Lineare Regression für Konvergenzordnung
    p = np.polyfit(log_h, log_errors, 1)
    order = p[0]
    
    return order


def grid_convergence_test(code, language, filename, test_grids=None):
    """
    Hauptfunktion für Grid Convergence Test
    
    Returns:
        success (bool): Ob der Test erfolgreich war
        message (str): Beschreibung des Ergebnisses
        details (dict): Detaillierte Ergebnisse mit Konvergenzordnung
    """
    if test_grids is None:
        test_grids = [8, 16, 32, 64]
    
    print(f"\n{'='*60}")
    print(f"Grid Convergence Test für {language.upper()}")
    print(f"{'='*60}\n")
    
    solutions = {}
    errors = {}
    
    # Schritt 1: Berechne Lösungen für alle Gittergrößen
    print("Berechne Lösungen für verschiedene Gittergrößen...")
    for grid_size in test_grids:
        print(f"  Grid {grid_size}x{grid_size}...", end=" ")
        solution, error_msg = run_program_with_grid(code, language, filename, grid_size)
        
        if solution is None:
            print(f"❌ Fehler")
            return False, f"Fehler bei Grid {grid_size}x{grid_size}: {error_msg}", None
        
        solutions[grid_size] = solution
        print(f"✓")
    
    # Schritt 2: Verwende feinste Lösung als Referenz
    finest_grid = max(test_grids)
    reference_solution = solutions[finest_grid]
    
    print(f"\nVerwende {finest_grid}x{finest_grid} Grid als Referenzlösung")
    
    # Schritt 3: Berechne Fehler für alle gröberen Gitter
    print("\nBerechne Fehler gegenüber Referenzlösung...")
    convergence_grids = [g for g in test_grids if g < finest_grid]
    
    if len(convergence_grids) < 2:
        return False, "Mindestens 3 verschiedene Gittergrößen benötigt für Konvergenztest", None
    
    for grid_size in convergence_grids:
        # Interpoliere beide Lösungen auf gemeinsames feines Gitter für Vergleich
        interpolated_solution = interpolate_solution(solutions[grid_size], finest_grid)
        
        # Berechne L2-Fehler
        diff = interpolated_solution - reference_solution
        l2_error = np.sqrt(np.mean(diff**2))
        errors[grid_size] = l2_error
        
        print(f"  Grid {grid_size:3d}x{grid_size:3d}: L2-Fehler = {l2_error:.6e}")
    
    # Schritt 4: Berechne Konvergenzordnung
    print("\nKonvergenzanalyse:")
    grid_list = sorted(errors.keys())
    error_list = [errors[g] for g in grid_list]
    
    # Berechne paarweise Konvergenzordnungen
    orders = []
    for i in range(len(grid_list) - 1):
        h1 = 1.0 / grid_list[i]
        h2 = 1.0 / grid_list[i + 1]
        e1 = error_list[i]
        e2 = error_list[i + 1]
        
        if e1 > 0 and e2 > 0:
            order = np.log(e1 / e2) / np.log(h1 / h2)
            orders.append(order)
            print(f"  Grid {grid_list[i]} → {grid_list[i+1]}: Ordnung = {order:.2f}")
    
    if len(orders) == 0:
        return False, "Konnte Konvergenzordnung nicht berechnen", None
    
    avg_order = np.mean(orders)
    std_order = np.std(orders)
    
    print(f"\n  Durchschnittliche Konvergenzordnung: {avg_order:.2f} ± {std_order:.2f}")
    
    # Schritt 5: Validiere Konvergenzordnung
    # Für Runge-Kutta 4 mit räumlichen zentralen Differenzen (2. Ordnung)
    # Erwarte räumliche Konvergenzordnung ~1-2 (räumliche Diskretisierung dominiert)
    # Bei groben Gittern kann Ordnung niedriger sein
    expected_min_order = 1.0  # Mindestens 1.0 für grobes Gitter
    expected_max_order = 4.0  # Maximal 4 (theoretische Grenze für RK4)
    
    details = {
        'grids': grid_list,
        'errors': error_list,
        'orders': orders,
        'avg_order': avg_order,
        'std_order': std_order,
        'reference_grid': finest_grid
    }
    
    # Prüfe ob Fehler monoton fallen
    errors_decreasing = all(error_list[i] > error_list[i+1] for i in range(len(error_list)-1))
    
    if not errors_decreasing:
        return False, f"⚠️  Fehler fallen nicht monoton! Algorithmus konvergiert nicht korrekt.", details
    
    if avg_order < expected_min_order:
        return False, f"⚠️  Konvergenzordnung zu niedrig: {avg_order:.2f} < {expected_min_order}", details
    
    if avg_order > expected_max_order:
        return False, f"⚠️  Konvergenzordnung unrealistisch hoch: {avg_order:.2f} > {expected_max_order}", details
    
    print(f"\n{'='*60}")
    print(f"✅ Grid Convergence Test BESTANDEN!")
    print(f"   Konvergenzordnung: {avg_order:.2f} (erwartet: {expected_min_order}-{expected_max_order})")
    print(f"{'='*60}\n")
    
    return True, f"Grid Convergence Test bestanden (Ordnung: {avg_order:.2f})", details


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python grid_convergence_validator.py <code_file> <language>")
        print("Example: python grid_convergence_validator.py ../src/program.py python")
        sys.exit(1)
    
    code_file, language = sys.argv[1], sys.argv[2]
    
    if not os.path.exists(code_file):
        print(f"❌ Datei nicht gefunden: {code_file}")
        sys.exit(1)
    
    # Prüfe ob scipy verfügbar ist (für Interpolation)
    try:
        import scipy.interpolate
    except ImportError:
        print("⚠️  scipy nicht gefunden. Installiere mit: pip install scipy")
        sys.exit(1)
    
    with open(code_file, 'r') as f:
        code = f.read()
    
    filename = os.path.basename(code_file)
    
    # Standardisiere Dateiendung
    if language == 'cpp' and not filename.endswith('.cpp'):
        filename = filename + '.cpp'
    elif language == 'julia' and not filename.endswith('.jl'):
        filename = filename + '.jl'
    elif language == 'python' and not filename.endswith('.py'):
        filename = filename + '.py'
    
    # Führe Grid Convergence Test durch
    # Verwende kleinere Grids für schnelleren Test (kann angepasst werden)
    test_grids = [8, 16, 32, 64]
    
    success, message, details = grid_convergence_test(code, language, filename, test_grids)
    
    if success:
        print(f"\n✅ {message}")
        if details:
            print(f"\nDetails:")
            print(f"  Getestete Grids: {details['grids']}")
            print(f"  L2-Fehler: {[f'{e:.2e}' for e in details['errors']]}")
            print(f"  Konvergenzordnungen: {[f'{o:.2f}' for o in details['orders']]}")
        sys.exit(0)
    else:
        print(f"\n❌ {message}")
        if details:
            print(f"\nDetails:")
            print(f"  Getestete Grids: {details['grids']}")
            print(f"  L2-Fehler: {[f'{e:.2e}' for e in details['errors']]}")
            if details['orders']:
                print(f"  Konvergenzordnungen: {[f'{o:.2f}' for o in details['orders']]}")
        sys.exit(1)
