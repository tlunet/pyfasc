import matplotlib.pyplot as plt
import numpy as np
import os
import tempfile


def create_loglog_chart(results):
    """Create log-log chart for execution time only (without compilation)."""
    if not results or 'test_cases' not in results:
        return None
    
    test_cases = results['test_cases']
    lang1 = results['languages']['program1']
    lang2 = results['languages']['program2']
    
    nX = np.array([int(case_data['config'].split()[0]) for case_data in test_cases.values()])
    timeLang1 = [case_data['program1']['runtime'] for case_data in test_cases.values()]
    timeLang2 = [case_data['program2']['runtime'] for case_data in test_cases.values()]
    
    plt.figure("runtime")
    plt.loglog(nX, timeLang1, "o-", label=lang1.title())
    plt.loglog(nX, timeLang2, "s-", label=lang2.title())
    plt.loglog(nX, 1e-5*nX**2, "--", c="black", label="O(n²)")
    
    # Automatische Y-Achsen-Skalierung basierend auf den Daten
    y_min = min(min(timeLang1), min(timeLang2))
    y_max = max(max(timeLang1), max(timeLang2))
    plt.ylim(y_min * 0.5, y_max * 2)
    
    plt.legend()
    plt.xlabel("Nx")
    plt.ylabel("Execution Time (s)")
    plt.title("Execution Time Comparison (Compilation Excluded)")
    plt.grid(True, which="both")
    plt.tight_layout()
    
    line_chart_path = os.path.join(tempfile.gettempdir(), 'line_chart_loglog_runtime.png')
    plt.savefig(line_chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return line_chart_path


def create_loglog_chart_total(results):
    """Create log-log chart for total time (including compilation)."""
    if not results or 'test_cases' not in results:
        return None
    
    test_cases = results['test_cases']
    lang1 = results['languages']['program1']
    lang2 = results['languages']['program2']
    
    nX = np.array([int(case_data['config'].split()[0]) for case_data in test_cases.values()])
    timeLang1 = [case_data['program1'].get('total_time', case_data['program1']['runtime']) 
                 for case_data in test_cases.values()]
    timeLang2 = [case_data['program2'].get('total_time', case_data['program2']['runtime']) 
                 for case_data in test_cases.values()]
    
    plt.figure("total_time")
    plt.loglog(nX, timeLang1, "o-", label=lang1.title())
    plt.loglog(nX, timeLang2, "s-", label=lang2.title())
    plt.loglog(nX, 1e-5*nX**2, "--", c="black", label="O(n²)")
    
    # Automatische Y-Achsen-Skalierung basierend auf den Daten
    y_min = min(min(timeLang1), min(timeLang2))
    y_max = max(max(timeLang1), max(timeLang2))
    plt.ylim(y_min * 0.5, y_max * 2)
    
    plt.legend()
    plt.xlabel("Nx")
    plt.ylabel("Total Time (s)")
    plt.title("Total Time Comparison (Including Compilation)")
    plt.grid(True, which="both")
    plt.tight_layout()
    
    line_chart_path = os.path.join(tempfile.gettempdir(), 'line_chart_loglog_total.png')
    plt.savefig(line_chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return line_chart_path
