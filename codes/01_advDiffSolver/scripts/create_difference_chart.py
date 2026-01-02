import matplotlib.pyplot as plt
import numpy as np
import os
import json
import tempfile


def load_metrics_from_json(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)
    

def create_difference_chart(json_path=None):
    if json_path is None:
        json_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'all_metrics.json')
    
    if not os.path.exists(json_path):
        return None
    
    metrics = load_metrics_from_json(json_path)
    
    if not metrics:
        return None
    
    languages = [key for key in metrics[0].keys() if key != 'config']
    
    lang1, lang2 = languages[0], languages[1]
    
    nX = []
    time_differences = []
    relative_differences = []
    
    for entry in metrics:
        nx_value = int(entry['config'].split()[0])
        runtime_lang1 = entry[lang1]['runtime']
        runtime_lang2 = entry[lang2]['runtime']
        
        nX.append(nx_value)
        time_differences.append(abs(runtime_lang1 - runtime_lang2))

        # Relative Differenz in Prozent
        avg_runtime = (runtime_lang1 + runtime_lang2) / 2
        if avg_runtime > 0:
            relative_differences.append(
                ((runtime_lang1 - runtime_lang2) / avg_runtime) * 100
            )
        else:
            relative_differences.append(0)
    
    nX = np.array(nX)
    relative_differences = np.array(relative_differences)
    #time_differences = np.array(time_differences)
    
    plt.figure("runtime_difference", figsize=(10, 6))
    plt.plot(nX, relative_differences, "o-", linewidth=2, markersize=8, 
             label=f"Relative Differenz")
    plt.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    
    plt.legend()
    plt.xlabel("Nx")
    plt.xscale('log')
    plt.ylabel("Relative Difference (%)")
    plt.title(f"Relative Runtime Difference: {lang1.title()} vs {lang2.title()}")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    diff_chart_path = os.path.join(tempfile.gettempdir(), 'difference_chart_runtime.png')
    plt.savefig(diff_chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return diff_chart_path


if __name__ == "__main__":
    runtime_path = create_difference_chart()
