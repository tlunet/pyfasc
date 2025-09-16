import matplotlib.pyplot as plt
import numpy as np
import os
import tempfile


def create_loglog_chart(results):
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
    plt.loglog(nX, 1e-5*nX**2, "--", c="black")
    plt.ylim(1e-2, 1e4)
    plt.legend()
    plt.xlabel("Nx")
    plt.ylabel("runtime")
    plt.grid(True, which="both")
    plt.tight_layout()
    
    line_chart_path = os.path.join(tempfile.gettempdir(), 'line_chart_loglog.png')
    plt.savefig(line_chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return line_chart_path
