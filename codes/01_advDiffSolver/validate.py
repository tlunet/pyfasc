#!/usr/bin/env python3
"""
Eigenständige Validierung für CodeBench
Testet Code ohne UI-Abhängigkeiten
"""
import os
import tempfile
import subprocess
import shutil
import numpy as np

def validate_output_format(output_lines):
    """Validiert das Format der Ausgabedateien"""
    if len(output_lines) < 10:
        return False, "Zu wenige Ausgabezeilen"
    
    try:
        # Teste erste Zeile auf numerische Werte
        first_line = output_lines[0].strip().split()
        if len(first_line) < 2:
            return False, "Zu wenige Spalten in der ersten Zeile"
        
        # Teste auf numerische Werte
        for val in first_line[:5]:  # Teste nur ersten 5 Werte
            float_val = float(val)
            # Prüfe auf unrealistische Werte
            if abs(float_val) > 1e100 or (float_val != 0 and abs(float_val) < 1e-100):
                return False, f"Unrealistische Werte: {float_val}"
            if np.isnan(float_val) or np.isinf(float_val):
                return False, f"NaN oder Inf Werte gefunden: {float_val}"
                
        return True, "Format OK"
    except ValueError as e:
        return False, f"Nicht-numerische Werte gefunden: {e}"

def validate_program(code, language, filename):
    """Validiert ein Programm in isolierter Umgebung"""
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Schreibe Code in temporäre Datei
            code_file = os.path.join(temp_dir, filename)
            with open(code_file, 'w') as f:
                f.write(code)
            
            # Kopiere inputs.txt
            inputs_src = "/Users/yusif/Documents/Uni/CodeBench/inputs.txt"
            inputs_dst = os.path.join(temp_dir, "inputs.txt")
            input_dst = os.path.join(temp_dir, "input.txt")  # Für Python Script
            if os.path.exists(inputs_src):
                shutil.copy2(inputs_src, inputs_dst)
                shutil.copy2(inputs_src, input_dst)  # Kopiere auch als input.txt
            else:
                return False, "inputs.txt nicht gefunden"
            
            # Führe Code aus
            old_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                if language == 'python':
                    python_path = '/Users/yusif/Documents/Uni/CodeBench/.venv/bin/python'
                    result = subprocess.run([python_path, filename], 
                                          capture_output=True, text=True, timeout=30)
                elif language == 'cpp':
                    # Kompiliere C++
                    compile_result = subprocess.run(['g++', '-o', 'program', filename], 
                                                  capture_output=True, text=True, timeout=30)
                    if compile_result.returncode != 0:
                        return False, f"Kompilierfehler: {compile_result.stderr}"
                    
                    # Führe aus
                    result = subprocess.run(['./program'], 
                                          capture_output=True, text=True, timeout=30)
                elif language == 'julia':
                    result = subprocess.run(['julia', filename], 
                                          capture_output=True, text=True, timeout=30)
                else:
                    return False, f"Nicht unterstützte Sprache: {language}"
                
                if result.returncode != 0:
                    return False, f"Runtime-Fehler: {result.stderr}"
                
                # Prüfe Ausgabedateien
                output_files = ['uInit.txt', 'uEnd.txt']
                for output_file in output_files:
                    if not os.path.exists(output_file):
                        return False, f"Ausgabedatei fehlt: {output_file}"
                    
                    with open(output_file, 'r') as f:
                        lines = f.readlines()
                    
                    valid, msg = validate_output_format(lines)
                    if not valid:
                        return False, f"{output_file}: {msg}"
                
                return True, "Validierung erfolgreich"
                
            finally:
                os.chdir(old_cwd)
                
        except subprocess.TimeoutExpired:
            return False, "Timeout - Programm läuft zu lange"
        except Exception as e:
            return False, f"Unerwarteter Fehler: {str(e)}"

if __name__ == "__main__":
    # Teste mit vorhandenem Code
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python validate.py <code_file> <language>")
        sys.exit(1)
    
    code_file, language = sys.argv[1], sys.argv[2]
    
    if not os.path.exists(code_file):
        print(f"Datei nicht gefunden: {code_file}")
        sys.exit(1)
    
    with open(code_file, 'r') as f:
        code = f.read()
    
    filename = f"program.{language}"
    if language == 'cpp':
        filename = "program.cpp"
    elif language == 'julia':
        filename = "program.jl"
    elif language == 'python':
        filename = "program.py"
    
    success, message = validate_program(code, language, filename)
    
    if success:
        print(f"✅ {message}")
        sys.exit(0)
    else:
        print(f"❌ {message}")
        sys.exit(1)
