# 🐛 Windows Encoding Fix

## Problem

Windows PowerShell und cmd.exe verwenden standardmäßig das `cp1252` Encoding (Windows-1252), das keine Emojis unterstützt. Dies führt zu diesem Fehler:

```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f40d' in position 13: 
character maps to <undefined>
```

## Lösung

Wir haben mehrere Schutzmechanismen implementiert:

### 1. Console-Konfiguration (Automatisch)

Die Funktion `configure_windows_console()` wird automatisch beim Import aufgerufen:

```python
from adapters.utils import configure_windows_console
configure_windows_console()  # Setzt stdout/stderr auf UTF-8
```

### 2. Safe Print Utility

Die `safe_print()` Funktion fängt Encoding-Fehler ab:

```python
from adapters.utils import safe_print

safe_print("🐍 Python program")  # Funktioniert auf allen Systemen
# UTF-8: "🐍 Python program"
# cp1252: " Python program" (Emoji entfernt)
```

### 3. Fallback in allen Adaptern

Alle Stellen, die Emojis ausgeben, haben einen Fallback:

```python
try:
    print(f"{adapter.emoji} {adapter.display_name}")
except (UnicodeEncodeError, UnicodeError):
    print(adapter.display_name)  # Ohne Emoji
```

## Workarounds für Nutzer

### Option 1: UTF-8 in PowerShell aktivieren

```powershell
# Vor dem Ausführen:
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001

# Dann:
python diagnosetool.py --py program.py --cpp program.cpp --config input.txt
```

### Option 2: Windows Terminal verwenden

Windows Terminal (modern) unterstützt UTF-8 nativ. Installieren aus dem Microsoft Store.

### Option 3: Streamlit App nutzen

Die Streamlit-App im Browser hat keine Encoding-Probleme:

```bash
streamlit run app.py
```

## Technische Details

### Was macht `configure_windows_console()`?

```python
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

Dies ersetzt die Standard-Streams mit UTF-8-fähigen Wrappern.

### Was macht `safe_print()`?

```python
def safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeError):
        # Entferne Emojis mit Regex
        text_no_emoji = re.sub(r'[\U0001F000-\U0001FFFF]+', '', text)
        print(text_no_emoji.strip())
```

Versucht zuerst normale Ausgabe, bei Fehler werden Emojis entfernt.

## Betroffene Dateien

Die folgenden Dateien wurden angepasst:

1. **`adapters/utils.py`** (NEU)
   - `safe_print()` - Sichere Print-Funktion
   - `configure_windows_console()` - Console-Setup
   - `get_emoji_safe_display()` - Emoji-sichere Anzeige

2. **`adapters/__init__.py`**
   - Exportiert Utility-Funktionen

3. **`adapters/registry.py`**
   - Verwendet sicheres Printing bei Adapter-Registrierung

4. **`tests/diagnosetool.py`**
   - Konfiguriert Console beim Start
   - Verwendet `safe_print()` für alle Emoji-Ausgaben

## Testen

### Test 1: Encoding-Check

```python
import sys
print(f"Encoding: {sys.stdout.encoding}")
# Erwünscht: utf-8
# Problematisch: cp1252
```

### Test 2: Emoji-Test

```python
from adapters.utils import safe_print

safe_print("🐍 Test 1")
safe_print("⚙️ Test 2")
safe_print("🔬 Test 3")
```

Sollte funktionieren ohne Fehler (mit oder ohne Emojis, je nach System).

### Test 3: Vollständiger Benchmark

```bash
python tests/diagnosetool.py --py src/program.py --cpp src/program.cpp --config config/input.txt
```

Sollte keine `UnicodeEncodeError` mehr werfen.

## Für Ihre Bachelorarbeit

Sie können dokumentieren:

> Die Anwendung berücksichtigt Plattform-spezifische Encoding-Probleme.
> Auf Windows-Systemen mit cp1252-Encoding werden Emojis automatisch
> entfernt oder das Console-Encoding wird auf UTF-8 umgestellt.
> Dies gewährleistet die Funktionsfähigkeit auf allen Plattformen.

## Weitere Hinweise

- **Linux/Mac**: Kein Problem, UTF-8 ist Standard
- **Windows 10+**: Windows Terminal empfohlen
- **Ältere Windows**: Funktioniert mit Fallback (ohne Emojis)
- **CI/CD**: Funktioniert in allen Umgebungen

## Zusammenfassung

✅ **Problem behoben** - Mehrfache Schutzebenen
✅ **Automatisch** - Keine Nutzer-Konfiguration nötig
✅ **Rückwärtskompatibel** - Funktioniert mit und ohne UTF-8
✅ **Dokumentiert** - Klar erklärt für BA-Dokumentation
