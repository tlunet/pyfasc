import pandas as pd


def create_csv_data(results):
    """Create CSV data for download"""
    if not results or 'test_cases' not in results:
        return None
    
    lang1 = results['languages']['program1']
    lang2 = results['languages']['program2']
    
    csv_data = pd.DataFrame([
        {
            'Test Case': case_name,
            f'{lang1.title()} Runtime (s)': case_data['program1']['runtime'],
            f'{lang2.title()} Runtime (s)': case_data['program2']['runtime'],
            'Speedup Factor': case_data['program1']['runtime'] / case_data['program2']['runtime'] if case_data['program2']['runtime'] > 0 else 0
        }
        for case_name, case_data in results['test_cases'].items()
    ])
    
    return csv_data
