# diagnosetool.py
import argparse
import subprocess
import time
import os
import json
import matplotlib.pyplot as plt

def read_input_blocks(filename):
    """Liest mehrere Input-Blöcke aus einer Datei, getrennt durch Leerzeilen."""
    with open(filename, "r") as f:
        content = f.read()
    blocks = content.strip().split("\n\n")
    # Hängt jeweils einen Zeilenumbruch an, damit input.txt korrekt endet
    return [block + "\n" for block in blocks]

def measure_process_with_input_file(cmd, label):
    """Führt den Prozess aus, der input.txt liest, und misst nur die Laufzeit."""
    print(f"Running {label}...")
    
    start = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()  # Wartet bis Prozess fertig ist
    end = time.time()
    
    return {
        "runtime": end - start,
        "stdout": stdout.decode(),
        "stderr": stderr.decode()
    }

def compile_cpp(cpp_file):
    binary = "temp_cpp_exec"
    compile_cmd = ["g++", cpp_file, "-O2", "-o", binary]
    subprocess.check_call(compile_cmd)
    return f"./{binary}"

def plot_multiple_runs(results, metric):
    inputs = list(range(len(results)))
    py_vals = [entry["python"][metric] for entry in results]
    cpp_vals = [entry["cpp"][metric] for entry in results]

    plt.figure()
    plt.plot(inputs, py_vals, label="Python", marker="o")
    plt.plot(inputs, cpp_vals, label="C++", marker="x")
    plt.xlabel("Input Index")
    plt.ylabel(metric.replace("_", " ").title())
    plt.title(f"{metric.replace('_', ' ').title()} across Inputs")
    plt.legend()
    os.makedirs("results", exist_ok=True)
    plt.savefig(f"results/{metric}_by_input.png")
    print(f"Saved plot to results/{metric}_by_input.png")

def create_performance_comparison_plot(results):
    """Erstellt eine Performance-Vergleichstabelle als PNG-Datei."""
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Daten extrahieren
    sizes = [result["input"].split('\n')[0] for result in results]
    py_times = [result["python"]["runtime"] for result in results]
    cpp_times = [result["cpp"]["runtime"] for result in results]
    speedups = [cpp / py if py > 0 else float('inf') for py, cpp in zip(py_times, cpp_times)]
    
    # Erstelle Figure mit zwei Subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Links: Tabelle
    table_data = []
    headers = ['Size', 'Python (s)', 'C++ (s)', 'Speedup']
    
    for i, result in enumerate(results):
        size = sizes[i]
        py_time = py_times[i]
        cpp_time = cpp_times[i]
        speedup = speedups[i]
        table_data.append([size, f"{py_time:.4f}", f"{cpp_time:.4f}", f"{speedup:.2f}x"])
    
    # Tabelle erstellen
    ax1.axis('tight')
    ax1.axis('off')
    table = ax1.table(cellText=table_data, colLabels=headers, 
                     cellLoc='center', loc='center',
                     colWidths=[0.2, 0.25, 0.25, 0.25])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 2)
    
    # Header-Zeile hervorheben
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#40466e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Alternating row colors
    for i in range(1, len(table_data) + 1):
        for j in range(len(headers)):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#f0f0f0')
    
    ax1.set_title('Performance Comparison Table', fontsize=14, fontweight='bold', pad=20)
    
    # Rechts: Speedup Bar Chart
    x_pos = np.arange(len(sizes))
    bars = ax2.bar(x_pos, speedups, color=['#2E8B57' if s >= 1 else '#DC143C' for s in speedups])
    
    ax2.set_xlabel('Problem Size', fontweight='bold')
    ax2.set_ylabel('Speedup Factor (C++/Python)', fontweight='bold')
    ax2.set_title('C++ vs Python Performance Speedup\n(>1: C++ faster, <1: Python faster)', fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(sizes, rotation=45)
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=1, color='black', linestyle='--', alpha=0.7, label='Equal Performance')
    
    # Werte auf den Balken anzeigen
    for i, (bar, speedup) in enumerate(zip(bars, speedups)):
        height = bar.get_height()
        # Position Text je nach Balkenhöhe
        if height >= 0:
            va = 'bottom'
            y_pos = height + 0.02
        else:
            va = 'top' 
            y_pos = height - 0.02
        ax2.text(bar.get_x() + bar.get_width()/2., y_pos,
                f'{speedup:.2f}x', ha='center', va=va, fontweight='bold')
    
    plt.tight_layout()
    os.makedirs("results", exist_ok=True)
    plt.savefig("results/performance_comparison.png", dpi=300, bbox_inches='tight')
    print("Saved performance comparison to results/performance_comparison.png")
    plt.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--py", required=True, help="Python script path")
    parser.add_argument("--cpp", required=True, help="C++ source path")
    parser.add_argument("--inputs", required=True, help="Path to file with multiple input blocks")
    args = parser.parse_args()

    cpp_binary = compile_cpp(args.cpp)
    input_blocks = read_input_blocks(args.inputs)

    all_results = []

    for idx, input_block in enumerate(input_blocks):
        print(f"\n=== Input Block #{idx} ===")
        
        # Schreibe aktuellen Input-Block in input.txt
        with open("input.txt", "w") as f:
            f.write(input_block)

        # Messe Python-Lauf
        py_metrics = measure_process_with_input_file(["python3", args.py], "Python")
        # Messe C++-Lauf
        cpp_metrics = measure_process_with_input_file([cpp_binary], "C++")

        all_results.append({
            "input": input_block.strip(),
            "python": py_metrics,
            "cpp": cpp_metrics
        })

    os.makedirs("results", exist_ok=True)
    with open("results/all_metrics.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print("Saved all metrics to results/all_metrics.json")

    for metric in ["runtime"]:
        plot_multiple_runs(all_results, metric)
    
    # Performance-Vergleichstabelle als PNG erstellen
    create_performance_comparison_plot(all_results)


if __name__ == "__main__":
    main()
