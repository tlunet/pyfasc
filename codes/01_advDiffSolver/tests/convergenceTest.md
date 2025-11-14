## 🎯 Grundprinzip

Der Test basiert auf einer fundamentalen Eigenschaft numerischer Methoden: **Wenn Sie das Gitter verfeinern, sollte die Lösung konvergieren und der Fehler sollte mit einer bestimmten Rate abnehmen.**

## 📐 Mathematische Theorie

### 1. **Diskretisierungsfehler**
Für eine numerische Methode gilt:

$$\text{Fehler} \approx C \cdot h^p$$

Wobei:
- $h$ = Gitterweite (z.B. $h = 1/N$ für ein $N \times N$ Gitter)
- $p$ = **Konvergenzordnung** (charakteristisch für die Methode)
- $C$ = Konstante (hängt vom Problem ab)

### 2. **Berechnung der Ordnung**
Wenn wir zwei Gitter mit verschiedenen Auflösungen haben:

$$\frac{e_1}{e_2} = \frac{C \cdot h_1^p}{C \cdot h_2^p} = \left(\frac{h_1}{h_2}\right)^p$$

Durch Logarithmieren:

$$p = \frac{\log(e_1/e_2)}{\log(h_1/h_2)}$$

**Das ist die Formel, die wir verwenden!**

## 🔬 Was der Test macht (Schritt für Schritt)

### **Schritt 1: Lösungen für verschiedene Gitter berechnen**
```
Grid 8x8   → Lösung u₈
Grid 16x16 → Lösung u₁₆
Grid 32x32 → Lösung u₃₂
Grid 64x64 → Lösung u₆₄
```

Jedes Programm wird mit der **gleichen** Konfiguration ausgeführt, nur die Gittergröße variiert.

### **Schritt 2: Referenzlösung wählen**
Die **feinste** Lösung (64×64) wird als "quasi-exakte" Referenz verwendet:
```
u_ref = u₆₄
```

**Warum?** Weil wir keine analytische Lösung haben, approximieren wir sie mit der feinsten verfügbaren Lösung.

### **Schritt 3: Fehler berechnen**
Für jedes gröbere Gitter:
1. **Interpoliere** die grobe Lösung auf das feine 64×64 Gitter
2. Berechne den **L2-Fehler** (Wurzel aus mittlerem quadratischem Fehler):

$$\text{L2-Fehler} = \sqrt{\frac{1}{N^2} \sum_{i,j} (u_{ij} - u_{\text{ref},ij})^2}$$

**Beispiel aus Ihrem Test:**
```
Grid  8×8:  L2-Fehler = 8.92e-02
Grid 16×16: L2-Fehler = 3.71e-02
Grid 32×32: L2-Fehler = 1.42e-02
```

### **Schritt 4: Konvergenzordnung berechnen**
Zwischen zwei aufeinanderfolgenden Gittern:

**8→16:**
- $h_8 = 1/8 = 0.125$
- $h_{16} = 1/16 = 0.0625$
- $e_8 = 0.0892$, $e_{16} = 0.0371$

$$p = \frac{\log(0.0892/0.0371)}{\log(0.125/0.0625)} = \frac{\log(2.40)}{\log(2)} = \frac{0.876}{0.693} = 1.26$$

**16→32:**
$$p = \frac{\log(0.0371/0.0142)}{\log(0.0625/0.03125)} = 1.39$$

**Durchschnitt:** $p_{\text{avg}} = 1.33$

## 🎓 Interpretation der Ergebnisse

### **Was bedeutet die Konvergenzordnung?**

| Ordnung | Bedeutung | Typisch für |
|---------|-----------|-------------|
| p = 1 | **Linear**: Gitter halbieren → Fehler halbieren | Upwind-Schema (1. Ordnung) |
| p = 2 | **Quadratisch**: Gitter halbieren → Fehler vierteln | Zentrale Differenzen (2. Ordnung) |
| p = 4 | **Quartisch**: Gitter halbieren → Fehler /16 | Runge-Kutta 4 (zeitlich) |

### **Ihre Ergebnisse:**

**Python: p = 1.33**
- Liegt zwischen 1. und 2. Ordnung
- **Warum nicht 2?** Vermutlich weil:
  - Zeitliche Diskretisierung (RK4, 4. Ordnung) ist feiner als räumliche (2. Ordnung)
  - Bei groben Gittern dominiert räumlicher Fehler
  - Numerische Diffusion bei groben Gittern

**C++: p = 1.80**
- Näher an 2. Ordnung
- Bessere numerische Implementierung
- Möglicherweise bessere Stabilität

## ✅ Validierungskriterien

Der Test **besteht**, wenn:

1. ✅ **Fehler fallen monoton**: $e_8 > e_{16} > e_{32}$
2. ✅ **Konvergenzordnung plausibel**: $1.0 < p < 4.0$
3. ✅ **Keine NaN/Inf Werte**
4. ✅ **Korrekte Ausgabegröße**

Der Test **fällt durch**, wenn:

❌ Fehler steigen oder stagnieren → Algorithmus konvergiert nicht
❌ Ordnung zu niedrig (< 1) → Instabilität oder Bug
❌ Ordnung unrealistisch hoch (> 4) → Numerischer Zufall

## 🔍 Warum ist das besser als Ihre alte Validierung?

| Alte Validierung | Grid Convergence Test |
|------------------|----------------------|
| ❌ Nur Format-Check | ✅ Prüft numerische Korrektheit |
| ❌ Keine Fehleranalyse | ✅ Quantifiziert Genauigkeit |
| ❌ Sprach-spezifisch | ✅ Sprachunabhängig |
| ❌ Erkennt subtile Bugs nicht | ✅ Erkennt Konvergenzprobleme |

## 💡 Praktisches Beispiel

Stellen Sie sich vor, jemand ändert den Code und macht einen Vorzeichenfehler im Diffusionsterm. Die alte Validierung würde **nicht** versagen (Format ist ja OK), aber der Grid Convergence Test würde zeigen:

```
Grid  8×8:  L2-Fehler = 0.15
Grid 16×16: L2-Fehler = 0.28  ← Fehler steigt statt zu fallen!
Grid 32×32: L2-Fehler = 0.52
```

→ **Test fällt durch: "Fehler fallen nicht monoton!"** ✅

Das ist die **Stärke** dieser Methode! 🎯