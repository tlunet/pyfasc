# CI/CD Pipeline - Grid Convergence Validation

Diese Pipeline validiert automatisch alle neu hochgeladenen oder geänderten Algorithmus-Implementierungen mit einem Grid Convergence Test.

## 🎯 Zweck

Der Grid Convergence Test stellt sicher, dass numerische Algorithmen korrekt konvergieren, wenn die Gitterauflösung erhöht wird. Dies ist ein fundamentaler Qualitätstest für numerische Methoden.

## 🚀 Wann wird die Pipeline ausgelöst?

Die Pipeline wird **automatisch** ausgeführt bei:

1. **Push** auf `main` oder `develop` Branch
2. **Pull Requests** gegen `main` Branch

**Bedingung:** Änderungen in folgenden Dateien:
- `codes/01_advDiffSolver/src/**` (alle Dateien im src-Ordner)
- `codes/01_advDiffSolver/tests/run_validation.py`
- `codes/01_advDiffSolver/scripts/run_*_multi_*.py`
- `.github/workflows/grid-convergence-validation.yml`

## 📋 Was wird getestet?

Die Pipeline führt eine kombinierte Validierung durch:

- **Python und C++ Implementierungen** werden parallel getestet
- **Verschiedene Gittergrößen** (256x256, 128x128, 64x64)
- **Verschiedene Zeitschritte** (16, 32, 64 Schritte)
- **Vergleich zwischen Python und C++** Ergebnissen

Die Validierung stellt sicher, dass beide Implementierungen identische Ergebnisse liefern.

## ✅ Test-Kriterien

Ein Algorithmus besteht den Test, wenn:

1. ✅ **Fehler fallen monoton** mit feinerem Gitter
2. ✅ **Konvergenzordnung plausibel** (1.0 < p < 4.0)
3. ✅ **Keine NaN/Inf Werte** in der Lösung
4. ✅ **Korrekte Ausgabeformat**

## 📊 Pipeline-Schritte

```
1. Checkout Code
   ↓
2. Erkenne geänderte Dateien in src/
   ↓
3. Setup Umgebung (Python, C++, Julia)
   ↓
4. Installiere Dependencies (numpy, scipy)
   ↓
5. Führe Grid Convergence Test aus
   ↓
6. Zeige Ergebnisse & Summary
```

## 🔧 Lokales Testen (vor dem Push)

Bevor Sie Code pushen, können Sie lokal testen:

```bash
cd codes/01_advDiffSolver

# Kombinierte Validierung (Python & C++)
python tests/run_validation.py
```

## 📝 Beispiel-Ausgabe

### ✅ Erfolgreich
```
============================================================
COMBINED VALIDATION TEST
============================================================

============================================================
GRID SIZE VALIDATION
============================================================

[1/6] Running C++ implementation (grid sizes)...
[2/6] Running Python implementation (grid sizes)...
[3/6] Comparing grid size results...

256x256 grid:
  Initial - Max diff: 2.34e-15, Mean diff: 1.23e-16
  Final   - Max diff: 3.45e-14, Mean diff: 2.34e-15
  Match: ✓ PASS

128x128 grid:
  Initial - Max diff: 1.23e-15, Mean diff: 8.90e-17
  Final   - Max diff: 2.34e-14, Mean diff: 1.67e-15
  Match: ✓ PASS

Grid validation result: ✓ PASS

============================================================
TIME STEPS VALIDATION
============================================================

[4/6] Running C++ implementation (time steps)...
[5/6] Running Python implementation (time steps)...
[6/6] Comparing time step results...

All tests passed: True
```

### ❌ Fehlgeschlagen
```
============================================================
COMBINED VALIDATION TEST
============================================================

[1/6] Running C++ implementation (grid sizes)...
[2/6] Running Python implementation (grid sizes)...
[3/6] Comparing grid size results...

256x256 grid:
  Initial - Max diff: 1.23e-02, Mean diff: 4.56e-03
  Final   - Max diff: 5.67e-02, Mean diff: 2.34e-02
  Match: ✗ FAIL

Grid validation result: ✗ FAIL
```

## 🛠️ Fehlerbehebung

### Problem: Pipeline schlägt fehl

**Mögliche Ursachen:**

1. **Python und C++ Ergebnisse stimmen nicht überein**
   - Überprüfen Sie die Implementierung auf Unterschiede
   - Prüfen Sie Randbedingungen in beiden Sprachen
   - Vergleichen Sie die numerische Präzision

2. **Ausgabedateien fehlen**
   - C++ muss `uEnd.txt` und `uInit.txt` schreiben
   - Python muss `uEnd.txt` und `uInit.txt` schreiben
   - Dateien müssen im richtigen Format sein (Textdatei mit Matrix)

3. **Numerische Unterschiede zu groß**
   - Prüfen Sie Datentypen (float vs double)
   - Überprüfen Sie Compiler-Optimierungen
   - Verifizieren Sie mathematische Funktionen

### Problem: Dependencies fehlen

Fügen Sie in der YAML-Datei hinzu:
```yaml
- name: Install additional dependencies
  run: |
    pip install <package-name>
```

## 📚 Weiterführende Informationen

- **Grid Convergence Theory**: [Richardson Extrapolation](https://en.wikipedia.org/wiki/Richardson_extrapolation)
- **Numerische Methoden**: Siehe `/docs/numerical_methods.md`
- **Validator Code**: `tests/run_validation.py`
- **Helper Scripts**: `scripts/run_cpp_multi_grids.py`, `scripts/run_py_multi_grids.py`, etc.

## 🤝 Workflow für Contributors

1. **Entwickeln** Sie Ihren Algorithmus lokal
2. **Testen** Sie lokal mit `run_validation.py`
3. **Pushen** Sie auf einen Feature-Branch
4. **Erstellen** Sie einen Pull Request
5. Die **Pipeline läuft automatisch**
6. **Review** der Ergebnisse
7. Bei ✅ → **Merge** möglich

## 📧 Support

Bei Fragen oder Problemen:
- Öffnen Sie ein Issue im Repository
- Kontaktieren Sie das Entwickler-Team
- Konsultieren Sie die Dokumentation in `/docs`
