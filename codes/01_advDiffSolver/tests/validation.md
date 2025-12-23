# Validierungsmethodik

## Übersicht
Das Skript `run_validation.py` validiert die numerischen Solver-Implementierungen mittels einer konvergenzbasierten Methode. Die Validierung erfolgt in zwei Schritten: Konvergenztest der C++-Referenzimplementierung, gefolgt von einem Vergleich mit anderen Sprachimplementierungen.

## Methodisches Vorgehen

### Schritt 1: C++ Gitter-Konvergenztest
**Zweck**: Validierung der räumlichen Diskretisierung

- **Gitter**: 32×32, 64×64, 128×128 werden gegen 256×256 Referenz verglichen
- **Parameter**: ν = 0.001, t_end = 0.1, Zeitschritte = Gittergröße
- **Methode**: Berechnung des RMS-Fehlers zwischen aufeinanderfolgenden Gittern
- **Erwartete Konvergenzordnung**: ~4 (4. Ordnung kompakte finite Differenzen)
- **Akzeptanzkriterium**: Ordnung im Bereich [3.7, 4.3]

**Berechnung der Konvergenzordnung**:
```
order = log₂(error_coarse / error_fine)
```

Bei korrekter Implementierung sollte die Ordnung nahe 4 liegen, was der theoretischen Genauigkeit des numerischen Schemas entspricht.

### Schritt 2: Implementierungsvergleich
**Zweck**: Verifikation alternativer Implementierungen gegen validierte Referenz

- **Gitter**: 256×256
- **Zeitschritte**: 256
- **Vergleich**: Python-Implementierung vs. validierte C++-Referenzlösung
- **Toleranz**: rtol = 1e-10, atol = 1e-10

## Diskussion: Machine Precision vs. Praktische Toleranz

### Machine Precision
Die theoretische Maschinengenauigkeit für `double` (64-bit floating point) beträgt:
```
ε_machine ≈ 2.22 × 10⁻¹⁶
```

### Beobachtete Differenzen
Der Vergleich zwischen C++ und Python zeigt:
```
Max. Differenz: ~5 × 10⁻⁷
Mean Differenz: ~1 × 10⁻⁸
```

### Ursachen für Abweichungen von Machine Precision

1. **Unterschiedliche Operationsreihenfolge**
   - C++ und Python führen Multiplikationen und Additionen in potenziell unterschiedlicher Reihenfolge aus
   - Floating-Point-Arithmetik ist nicht assoziativ: `(a+b)+c ≠ a+(b+c)`

2. **Compiler-Optimierungen**
   - C++ mit `-O2` Flag führt aggressive Optimierungen durch
   - Kann Operationsreihenfolge verändern oder Zwischenergebnisse cachen
   - Python/NumPy verwendet andere Optimierungsstrategien

3. **Akkumulation numerischer Fehler**
   - Pro Zeitschritt werden O(N²) Operationen durchgeführt (N = Gittergröße)
   - Bei 256×256 Gitter und 256 Zeitschritten: ~10⁹ Operationen
   - Rundungsfehler akkumulieren sich über diese vielen Operationen

4. **Bibliotheksunterschiede**
   - C++ verwendet Standard-Math-Bibliothek
   - Python/NumPy verwendet optimierte BLAS/LAPACK-Routinen
   - Unterschiedliche Implementierungen von exp(), sqrt(), etc.

### Wahl der Toleranz: 1e-10

Die gewählte Toleranz von **1e-10** ist ein Kompromiss:

**Zu streng (1e-16, Machine Precision)**:
- Würde bei nahezu identischen Implementierungen fehlschlagen
- Unterschiede in Operationsreihenfolge würden Test scheitern lassen
- Nicht aussagekräftig für praktische Anwendungen

**Zu locker (1e-6)**:
- Würde systematische Fehler in der Implementierung übersehen können
- Keine strenge Verifikation der numerischen Korrektheit

**Gewählte Toleranz (1e-10)**:
- Liegt deutlich über Machine Precision (10⁶ × ε_machine)
- Ist streng genug, um Implementierungsfehler zu erkennen
- Erlaubt unvermeidbare Unterschiede durch Operationsreihenfolge
- Entspricht ~6-7 korrekten Dezimalstellen

## Interpretation der Ergebnisse

### Erfolgreiche Validierung bedeutet:
1. C++ zeigt korrekte Konvergenzordnung → Numerisches Schema korrekt implementiert
2. Python stimmt mit C++ innerhalb 1e-10 überein → Python-Implementierung korrekt
3. Beide Implementierungen lösen dasselbe mathematische Problem mit gleicher Genauigkeit

### Bei Fehlschlag:
- **Grid/Time Convergence**: Fehler im numerischen Schema (Finite Differenzen, RK4)
- **Implementation Comparison**: Logikfehler in alternativer Implementierung

## Ausführung
```bash
python tests/run_validation.py
```

## Literaturhinweise
- Trefethen & Bau: "Numerical Linear Algebra" - Kapitel zu Floating-Point-Arithmetik
- Goldberg: "What Every Computer Scientist Should Know About Floating-Point Arithmetic"
- LeVeque: "Finite Difference Methods" - Konvergenzanalyse

