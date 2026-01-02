# CodeBench - Performance Analyzer für Multi-Language Benchmarks

Ein flexibles, erweiterbares Benchmarking-Framework zur Performance-Analyse numerischer Programme in verschiedenen Programmiersprachen. Entwickelt im Rahmen einer Bachelorarbeit zur Evaluation von Advektions-Diffusions-Solvern.

## 🎯 Überblick

CodeBench ist ein modernes Benchmarking-Tool, das es ermöglicht, Implementierungen des gleichen Algorithmus in verschiedenen Programmiersprachen (Python, C++, Julia) systematisch zu vergleichen. Das Framework wurde speziell für wissenschaftliche Berechnungen entwickelt, mit Fokus auf 2D-Advektions-Diffusions-Probleme.

### Kernfunktionalitäten

- **Multi-Language-Support**: Native Unterstützung für Python, C++, Julia - erweiterbar auf weitere Sprachen
- **Intelligente Adapter-Architektur**: Plugin-System für einfaches Hinzufügen neuer Sprachen
- **Web-Interface & CLI**: Moderne Streamlit-Oberfläche oder Command-Line Tool
- **Automatische Kompilierung**: Handhabt automatisch die Kompilierung kompilierter Sprachen
- **Umfassende Metriken**: Laufzeit, Compilation-Zeit, Gesamtzeit mit automatischer Messung
- **Interaktive Visualisierung**: Log-log-Plots, Bar-Charts, Speedup-Analysen mit Plotly & Matplotlib
- **Persistente Ergebnisse**: JSON-basierte Datenbank vermeidet Wiederholungsmessungen
- **Flexible Konfiguration**: Unterstützt multiple Parameter-Sets pro Benchmark-Session

## 📁 Projektstruktur

```
CodeBench/
├── README.md                           # Diese Datei
└── codes/
    └── 01_advDiffSolver/              # Advektions-Diffusions-Solver Benchmark
        ├── app.py                      # Streamlit Web-Interface (HAUPTEINSTIEGSPUNKT)
        ├── setup.py                    # Package-Installation
        ├── pyproject.toml              # Moderne Python-Projekt-Konfiguration
        ├── requirements.txt            # Python-Abhängigkeiten
        ├── LICENSE                     # MIT Lizenz
        │
        ├── adapters/                   # Language Adapter System
        │   ├── __init__.py
        │   ├── base_adapter.py        # Abstrakte Basisklasse für alle Adapter
        │   ├── python_adapter.py      # Python-Implementierung
        │   ├── cpp_adapter.py         # C++-Implementierung (g++/clang++/MSVC)
        │   ├── julia_adapter.py       # Julia-Implementierung
        │   ├── registry.py            # Zentrales Adapter-Register
        │   ├── adapter_helpers.py     # Hilfsfunktionen
        │   ├── custom_adapters_example.py  # Beispiele: Rust, Go, JavaScript
        │   └── README.md              # Adapter-Architektur-Dokumentation
        │
        ├── src/                       # Beispiel-Implementierungen
        │   ├── program.py             # Python: NumPy-basiert mit RK4-Zeitintegration
        │   ├── program.cpp            # C++: Optimiert mit Custom-Array-Klasse
        │   └── program.jl             # Julia: Hochperformante Implementierung
        │
        ├── scripts/                   # Benchmark & Visualisierung
        │   ├── diagnosetool.py        # Core-Benchmark-Engine (CLI)
        │   ├── create_bar_chart.py    # Plotly Bar-Charts
        │   ├── create_loglog_chart.py # Matplotlib Log-log-Plots
        │   ├── create_difference_chart.py  # Differenz-Visualisierung
        │   ├── create_results_table.py    # Tabellarische Aufbereitung
        │   ├── create_csv_data.py     # CSV-Export
        │   └── create_download_package.py # ZIP-Archiv-Erstellung
        │
        ├── utils/                     # Utility-Module
        │   ├── benchmark_utils.py     # Benchmark-Durchführung
        │   ├── console_utils.py       # Windows-Console UTF-8 Handling
        │   ├── file_utils.py          # Datei-Operationen & Language-Detection
        │   ├── results_utils.py       # Ergebnis-Formatierung
        │   ├── session_utils.py       # Streamlit Session State
        │   └── ui_utils.py            # UI-Komponenten & Styling
        │
        ├── config/                    # Konfigurations-Beispiele
        │   └── config.txt             # Beispiel-Konfiguration
        │
        ├── tests/                     # Validierung & Tests
        │   ├── convTestNumpy.py       # Konvergenz-Tests
        │   ├── run_validation.py      # Validierungs-Suite
        │   └── validation.md          # Validierungs-Dokumentation
        │
        ├── examples/                  # Beispiel-Daten
        │   └── advection_diffusion/
        │       ├── uInit.txt          # Initialisierungsdaten
        │       └── uEnd.txt           # Referenz-Endergebnisse
        │
        ├── results/                   # Generierte Benchmark-Ergebnisse
        │   └── all_metrics.json       # Persistente Ergebnis-Datenbank
        │
        ├── assets/                    # Statische Ressourcen
        │   └── styles.css             # Custom CSS für Streamlit
        │
        └── img/                       # Dokumentations-Bilder
```

## 🚀 Installation & Schnellstart

### Voraussetzungen

- **Python 3.7+** (erforderlich)
- **C++ Compiler** (optional, für C++-Benchmarks):
  - Windows: MinGW-w64 oder Visual Studio mit C++
  - Linux/Mac: GCC oder Clang
- **Julia** (optional, für Julia-Benchmarks)

### Installation

```bash
# Repository klonen oder herunterladen
cd CodeBench/codes/01_advDiffSolver

# Abhängigkeiten installieren
pip install -r requirements.txt

# Optional: Als Package installieren (ermöglicht bessere Imports)
pip install -e .
```

### Web-Interface starten

```bash
# Streamlit-App starten
streamlit run app.py

# Öffnet automatisch http://localhost:8501
```

### Command-Line Tool verwenden

```bash
# In das Projekt-Verzeichnis wechseln
cd CodeBench/codes/01_advDiffSolver

# Benchmark ausführen
python scripts/diagnosetool.py \
    --py src/program.py \
    --cpp src/program.cpp \
    --config config/config.txt
```

## 📖 Verwendung

### 1. Web-Interface (Empfohlen)

Das Web-Interface bietet eine intuitive grafische Oberfläche:

1. **Dateien hochladen**:
   - Programm 1: Python/C++/Julia-Datei
   - Programm 2: Python/C++/Julia-Datei
   - Konfigurations-Datei

2. **Benchmark ausführen**:
   - Klick auf "Run Benchmark"
   - Fortschrittsanzeige in Echtzeit

3. **Ergebnisse analysieren**:
   - Interaktive Charts (Bar, Log-log, Speedup)
   - Detaillierte Tabellen mit allen Metriken
   - Export als JSON, CSV oder ZIP

4. **Datenbank verwalten**:
   - Button "🗑️ Delete Database" zum Zurücksetzen
   - Bereits gemessene Konfigurationen werden übersprungen

### 2. Command-Line Interface

Für automatisierte Workflows oder Skripting:

```bash
# Einfacher Benchmark
python scripts/diagnosetool.py --py prog1.py --cpp prog2.cpp --config input.txt

# Drei Programme vergleichen
python scripts/diagnosetool.py --py prog.py --cpp prog.cpp --jl prog.jl --config input.txt

# Mehrere Python-Varianten vergleichen
python scripts/diagnosetool.py --py numpy_impl.py --py pure_python.py --config input.txt
```

### 3. Konfigurations-Datei Format

Die Konfigurationsdatei definiert die Benchmark-Parameter. Beispiel für Advektions-Diffusions-Probleme:

```
# Format: nX nY initType flowType viscosity tEnd nSteps

# Test Case 1: Klein
64 64 gauss diagonal 0.001 0.1 100

# Test Case 2: Mittel
128 128 sinus rotating 0.005 0.1 200

# Test Case 3: Groß
256 256 cross2 circular 0.001 0.1 400
```

**Parameterübersicht**:
- `nX, nY`: Grid-Dimensionen
- `initType`: Initialisierung (`gauss`, `sinus`, `cross`, `cross2`)
- `flowType`: Strömungsmuster (`diagonal`, `rotating`, `circular`, `circular2`)
- `viscosity`: Viskositätskoeffizient
- `tEnd`: Simulationsendzeit
- `nSteps`: Anzahl Zeitschritte

**Multiple Konfigurationen**: Trenne Parameter-Sets durch Leerzeile. Kommentare beginnen mit `#`.

## 🏗️ Adapter-Architektur

Das Herzstück von CodeBench ist die erweiterbare Adapter-Architektur nach dem Strategy-Pattern:

### Vorteile

- ✅ **Einfache Erweiterung**: Neue Sprache = 1 neue Datei
- ✅ **Konsistente Schnittstelle**: Alle Sprachen funktionieren identisch
- ✅ **Plug-and-Play**: Keine Änderungen am Core-Code nötig
- ✅ **Automatische Erkennung**: File-Extension-basiert

### Neue Sprache hinzufügen

Siehe [adapters/README.md](codes/01_advDiffSolver/adapters/README.md) für detaillierte Anleitung. Kurz:

1. **Adapter-Klasse erstellen** (`adapters/your_language_adapter.py`):
```python
from .base_adapter import LanguageAdapter

class YourLanguageAdapter(LanguageAdapter):
    def __init__(self):
        super().__init__()
        self.name = "yourlang"
        self.extensions = [".ext"]
        self.display_name = "Your Language"
        self.emoji = "🎯"
    
    def prepare(self, source_file):
        # Kompilierung falls nötig
        return True, source_file, ""
    
    def get_execution_command(self, prepared_file):
        return ["your_interpreter", prepared_file]
    
    def cleanup(self, prepared_file):
        pass  # Aufräumen temporärer Dateien
```

2. **Im Registry registrieren** (`adapters/registry.py`):
```python
from .your_language_adapter import YourLanguageAdapter

# In _register_builtin_adapters() hinzufügen:
builtin_adapters = [
    PythonAdapter(),
    CppAdapter(),
    JuliaAdapter(),
    YourLanguageAdapter(),  # Hier einfügen!
]
```

3. **Fertig!** Keine weiteren Änderungen nötig.

Beispiele für Rust, Go, JavaScript sind in [custom_adapters_example.py](codes/01_advDiffSolver/adapters/custom_adapters_example.py) enthalten.

## 📊 Ergebnis-Format

Alle Ergebnisse werden in `results/all_metrics.json` gespeichert:

```json
[
  {
    "config": "64 64\ngauss\ndiagonal 0.001\n0.1 100",
    "python": {
      "runtime": 0.234,
      "total_time": 0.234,
      "compilation_time": 0,
      "returncode": 0
    },
    "cpp": {
      "runtime": 0.045,
      "total_time": 1.678,
      "compilation_time": 1.633,
      "returncode": 0
    }
  }
]
```

**Metriken**:
- `runtime`: Reine Ausführungszeit (ohne Kompilierung)
- `total_time`: Gesamtzeit (inkl. Kompilierung)
- `compilation_time`: Zeit für Kompilierung
- `returncode`: Exit-Code (0 = Erfolg)

## 🔬 Wissenschaftlicher Hintergrund

### Advektions-Diffusions-Gleichung

Das Framework wurde entwickelt für die 2D-Advektions-Diffusions-Gleichung:

$$\frac{\partial u}{\partial t} + \vec{v} \cdot \nabla u = \nu \nabla^2 u$$

Dabei ist:
- $u(x, y, t)$: skalares Feld (z.B. Konzentration, Temperatur)
- $\vec{v}(x, y)$: Geschwindigkeitsfeld
- $\nu$: Viskosität/Diffusionskoeffizient

### Numerische Methode

- **Räumliche Diskretisierung**: Finite Differenzen 5. Ordnung
- **Zeitintegration**: Runge-Kutta 4. Ordnung (RK4)
- **Randbedingungen**: Periodisch in beiden Richtungen
- **Konvergenzordnung**: $O(\Delta x^4, \Delta t^4)$

### Implementierungen

1. **Python** (`src/program.py`):
   - NumPy-Array-Operationen
   - Vektorisiert für bessere Performance
   - Explizite Halo-Region-Updates

2. **C++** (`src/program.cpp`):
   - Custom `Array2D`-Klasse für effiziente Speicherverwaltung
   - Template-basierte `Coeffs2D`-Klasse
   - Compiler-Optimierungen (`-O2`)

3. **Julia** (`src/program.jl`):
   - Just-In-Time-Compilation
   - Native Array-Performance
   - Elegante mathematische Notation

## 📈 Typische Ergebnisse

Beispiel für Grid-Size-Variation (256×256 bis 1024×1024):

| Grid Size | Python [s] | C++ [s] | Speedup | C++ Compile [s] |
|-----------|------------|---------|---------|-----------------|
| 256×256   | 0.234      | 0.045   | 5.2×    | 1.633           |
| 512×512   | 0.987      | 0.189   | 5.2×    | 1.645           |
| 1024×1024 | 3.876      | 0.745   | 5.2×    | 1.659           |

**Beobachtungen**:
- C++ zeigt konstanten Speedup-Faktor (~5×)
- Kompilierungszeit relativ konstant
- Für große Probleme amortisiert sich Kompilierungszeit
- Beide zeigen erwartete $O(n^2)$-Skalierung

## 🧪 Validierung & Tests

```bash
# Konvergenz-Tests ausführen
python tests/convTestNumpy.py

# Vollständige Validierungs-Suite
python tests/run_validation.py
```

Siehe [tests/validation.md](codes/01_advDiffSolver/tests/validation.md) für Details zur Validierung.

## 📦 Export-Optionen

Das Web-Interface bietet mehrere Export-Formate:

1. **JSON**: Rohe Metriken für weitere Analyse
2. **CSV**: Tabellendaten für Excel/LibreOffice
3. **ZIP**: Komplettes Paket mit:
   - JSON-Daten
   - CSV-Tabellen
   - PNG-Charts (Bar, Log-log, Speedup)
   - Konfigurations-Kopien

## 🛠️ Entwicklung

### Package installieren (Development Mode)

```bash
pip install -e .
```

Ermöglicht saubere Imports:
```python
from adapters import LanguageAdapter, LanguageRegistry
from utils.benchmark_utils import run_benchmark
```

### Testing

```bash
# Pytest (optional)
pip install pytest pytest-cov
pytest tests/
```

### Code-Style

Empfohlene Tools (in `setup.py` als optional definiert):
```bash
pip install -e .[dev]  # Installiert black, flake8, mypy
```
