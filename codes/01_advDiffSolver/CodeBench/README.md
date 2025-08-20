# CodeBench Performance Analyzer

**CodeBench** ist ein leistungsfähiges Benchmarking-Tool, das die Laufzeit-Performance von Python- und C++-Programmen vergleicht. Es bietet sowohl eine **Command-Line-Interface** für automatisierte Tests als auch eine **moderne Web-Oberfläche** für interaktive Analyse.

## 🚀 Schnellstart

### Web-Interface (Empfohlen)
```bash
# Abhängigkeiten installieren
pip install streamlit plotly psutil matplotlib

# Web-Anwendung starten
python -m streamlit run app.py
```

### Command-Line Tool
```bash
python diagnosetool.py --py script.py --cpp source.cpp --inputs inputs.txt
```

## ✨ Features

### 🌐 Web-Interface
- **📁 Intuitiver Code-Upload**: Drag & Drop für Python/C++ Dateien
- **🔍 Intelligente Validierung**: Syntax-Check und Output-Vergleich mit Referenz-Implementierungen
- **⚙️ Flexible Konfiguration**: 
  - Grid Size Variation (64x64 bis 1024x1024)
  - Time Steps Variation (100-800+ Schritte)
  - Initialisierungstypen: `gauss`, `sinus`, `cross`, `cross2`
  - Flow-Typen: `diagonal`, `rotating`, `shear`
  - Physics-Parameter: Viscosity, End Time
- **📊 Interaktive Visualisierung**: Plotly-Charts mit Zoom, Pan, Hover
- **💾 Export & Konfiguration**: JSON, CSV, ZIP-Export; Konfig speichern/laden

### 🖥️ Command-Line Tool
- **Automatische Kompilierung**: C++ Code wird automatisch compiled
- **Multi-Input Benchmarking**: Läuft mit verschiedenen Input-Sets
- **Umfassende Metriken**: Laufzeit, Peak Memory (MB), CPU Usage (%)
- **Visualisierung**: Automatische Charts und Performance-Plots
- **JSON Export**: Rohdaten für weitere Analyse

## 🛠️ Verwendung

### Web-Interface Workflow

1. **🔧 Setup**:
   ```bash
   python -m streamlit run app.py
   # Öffnet automatisch http://localhost:8501
   ```

2. **📤 Code hochladen**:
   - Python (.py) und C++ (.cpp, .cc, .cxx) Dateien hochladen
   - Oder Code direkt in Text-Bereiche einfügen
   - Mit "🔍 Validate Code" Buttons validieren

3. **⚙️ Parameter konfigurieren**:
   - **Variable auswählen**: Grid Size oder Time Steps
   - **Physics Parameter**: Initialisierung, Flow-Typ, Viscosity
   - **Range festlegen**: Start/End-Werte und Anzahl Testfälle
   - **Preview prüfen**: Live-Ansicht der generierten `inputs.txt`

4. **🏃‍♂️ Benchmark ausführen**:
   - Button wird automatisch aktiviert wenn alles validiert ist
   - Real-time Progress-Anzeige
   - Automatische Ergebnis-Visualisierung

5. **📊 Ergebnisse analysieren**:
   - Interaktive Performance-Charts (Runtime, Memory, Speedup)
   - Detaillierte Tabellen mit allen Metriken
   - Export in JSON, CSV oder ZIP-Format

### Command-Line Verwendung

```bash
python diagnosetool.py --py program.py --cpp program.cpp --inputs inputs.txt
```

**Parameter:**
- `--py`: Path zum Python-Script
- `--cpp`: Path zur C++ Source-Datei  
- `--inputs`: Path zur Input-Datei mit Test-Fällen

**Input-Format (`inputs.txt`):**
```
64 64
gauss
diagonal 0.0
1 400

128 128
sinus  
rotating 0.1
1 400
```

## 📊 Validierung & Qualitätssicherung

### Mehrstufige Code-Validierung
1. **Syntax-Check**: Kompilierung/Ausführung erfolgreich
2. **Output-Generierung**: Prüfung auf `uInit.txt` und `uEnd.txt`
3. **Referenz-Vergleich**: Numerischer Vergleich mit C++ Baseline
4. **Toleranz-Prüfung**: Akzeptiert Rundungsfehler < 1e-6 relativ

### Isolierte Benchmark-Ausführung
- Temporäre Verzeichnisse für jede Ausführung
- Automatische Ressourcen-Bereinigung
- Timeout-Schutz (30s pro Programm)
- Vollständige Metriken-Erfassung

## 🔧 Erweiterte Features

### Konfiguration Management
- **Speichern/Laden**: Häufig verwendete Setups persistent speichern
- **Session State**: UI-Zustände bleiben erhalten
- **Flexible Parameter**: Alle Simulationsparameter anpassbar

### Export & Analyse
- **JSON**: Vollständige Rohdaten für weitere Analyse
- **CSV**: Tabellarische Daten für Excel/Statistik-Tools
- **ZIP**: Komplettpaket mit Code, Configs, Plots und Ergebnissen
- **Interactive Charts**: Plotly-basierte Visualisierung mit Export-Optionen

## 🎯 Systemanforderungen

- **Python 3.8+**
- **C++ Compiler**: g++, clang++ oder MSVC
- **Dependencies**: `streamlit`, `plotly`, `psutil`, `matplotlib`
- **System**: 4GB+ RAM für größere Benchmarks
- **Browser**: Moderne Browser (Chrome, Firefox, Safari, Edge)

## 📋 Input-Format Spezifikation

Das neue standardisierte Format für `inputs.txt`:

```
nX nY              # Grid-Dimensionen
initType           # gauss, sinus, cross, cross2  
flowType viscosity # diagonal/rotating/shear + Wert
endTime nSteps     # Simulationszeit + Zeitschritte

# Leerzeile zwischen Test-Fällen
nX nY
initType
flowType viscosity  
endTime nSteps
```

**Beispiel:**
```
256 256
gauss
diagonal 0.0
1.0 400

512 512  
sinus
rotating 0.1
2.0 800
```

## 🚨 Troubleshooting

**Port bereits belegt:**
```bash
python -m streamlit run app.py --server.port 8502
```

**Validierung schlägt fehl:**
- Prüfen Sie g++ Installation: `g++ --version`
- Code muss `uInit.txt` und `uEnd.txt` generieren
- Output-Format mit Referenz vergleichen

**Performance-Probleme:**
- Problemgröße für Tests reduzieren
- Timeout erhöhen bei langsamen Systemen
- Memory-intensive Tests auf leistungsstarken Systemen

## 📁 Projekt-Struktur

```
CodeBench/
├── app.py                 # Streamlit Web-Interface
├── diagnosetool.py        # Command-Line Benchmarking Tool
├── program.py             # Python Referenz-Implementierung  
├── program.cpp            # C++ Referenz-Implementierung
├── reference/             # Baseline Output-Dateien
│   ├── uInit.txt
│   └── uEnd.txt
├── results/               # Benchmark-Ergebnisse
│   ├── all_metrics.json
│   └── *.png
└── inputs.txt            # Input-Konfiguration
```

## 🎮 Anwendungsfälle

- **🏫 Bildung**: Vergleich von Algorithmus-Implementierungen in verschiedenen Sprachen
- **🔬 Forschung**: Performance-Analyse numerischer Simulationen
- **💻 Development**: Optimierung kritischer Code-Pfade
- **📊 Benchmarking**: Systematische Performance-Evaluierung
- **🚀 Migration**: Quantifizierung von Sprach-Migration Benefits

---

**CodeBench** bietet eine moderne, benutzerfreundliche Lösung für systematisches Performance-Benchmarking mit professionellen Analyse-Tools. 🚀
