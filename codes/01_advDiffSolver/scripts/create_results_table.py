import pandas as pd

def create_results_table(results):
    """Create detailed results table as DataFrame"""
    if not results or 'test_cases' not in results:
        return None
    
    lang1 = results['languages']['program1']
    lang2 = results['languages']['program2']
    
    table_data = []
    for case_name, case_data in results['test_cases'].items():
        runtime_speedup = case_data['program1']['runtime'] / case_data['program2']['runtime'] if case_data['program2']['runtime'] > 0 else 0
        
        prog1_total = case_data['program1'].get('total_time', case_data['program1']['runtime'])
        prog2_total = case_data['program2'].get('total_time', case_data['program2']['runtime'])
        total_speedup = prog1_total / prog2_total if prog2_total > 0 else 0
        
        table_data.append({
            'Test Case': case_name,
            f'{lang1.title()} Runtime (s)': f"{case_data['program1']['runtime']:.4f}",
            f'{lang2.title()} Runtime (s)': f"{case_data['program2']['runtime']:.4f}",
            'Runtime Speedup': f"{runtime_speedup:.2f}x" if runtime_speedup > 0 else 'N/A',
            f'{lang1.title()} Total (s)': f"{prog1_total:.4f}",
            f'{lang2.title()} Total (s)': f"{prog2_total:.4f}",
            'Total Speedup': f"{total_speedup:.2f}x" if total_speedup > 0 else 'N/A'
        })
    
    df = pd.DataFrame(table_data)
    return df
