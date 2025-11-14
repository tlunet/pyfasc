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
- `codes/01_advDiffSolver/tests/grid_convergence_validator.py`
- `.github/workflows/grid-convergence-validation.yml`

## 📋 Was wird getestet?

Die Pipeline erkennt automatisch geänderte Dateien und testet:

- **Python-Dateien** (`.py`)
- **C++-Dateien** (`.cpp`)
- **Julia-Dateien** (`.jl`)

Für jede geänderte Datei wird ein Grid Convergence Test durchgeführt.

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

# Python
python tests/grid_convergence_validator.py src/program.py python

# C++
python tests/grid_convergence_validator.py src/program.cpp cpp

# Julia
python tests/grid_convergence_validator.py src/program.jl julia
```

## 📝 Beispiel-Ausgabe

### ✅ Erfolgreich
```
============================================================
Grid Convergence Test für PYTHON
============================================================

Berechne Lösungen für verschiedene Gittergrößen...
  Grid 8x8... ✓
  Grid 16x16... ✓
  Grid 32x32... ✓
  Grid 64x64... ✓

Berechne Fehler gegenüber Referenzlösung...
  Grid   8x  8: L2-Fehler = 8.92e-02
  Grid  16x 16: L2-Fehler = 3.71e-02
  Grid  32x 32: L2-Fehler = 1.42e-02

Konvergenzanalyse:
  Grid 8 → 16: Ordnung = 1.26
  Grid 16 → 32: Ordnung = 1.39

  Durchschnittliche Konvergenzordnung: 1.33 ± 0.06

============================================================
✅ Grid Convergence Test BESTANDEN!
   Konvergenzordnung: 1.33 (erwartet: 1.0-4.0)
============================================================
```

### ❌ Fehlgeschlagen
```
============================================================
Grid Convergence Test für PYTHON
============================================================

Berechne Lösungen für verschiedene Gittergrößen...
  Grid 8x8... ✓
  Grid 16x16... ✓
  Grid 32x32... ❌ Fehler

❌ Fehler bei Grid 32x32: NaN oder Inf in Lösung gefunden
```

## 🛠️ Fehlerbehebung

### Problem: Pipeline schlägt fehl

**Mögliche Ursachen:**

1. **Algorithmus konvergiert nicht**
   - Überprüfen Sie die numerische Stabilität
   - Prüfen Sie Zeitschrittgröße (CFL-Bedingung)
   - Debuggen Sie Randbedingungen

2. **Ausgabedateien fehlen**
   - C++ muss `uEnd.txt` schreiben
   - Python wird automatisch angepasst (Zeile wird hinzugefügt)
   - Julia muss `uEnd.txt` schreiben

3. **Konvergenzordnung zu niedrig**
   - Prüfen Sie die räumliche Diskretisierung
   - Verifizieren Sie die zeitliche Integration
   - Evtl. numerische Diffusion bei groben Gittern

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
- **Validator Code**: `tests/grid_convergence_validator.py`

## 🤝 Workflow für Contributors

1. **Entwickeln** Sie Ihren Algorithmus lokal
2. **Testen** Sie lokal mit `grid_convergence_validator.py`
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
