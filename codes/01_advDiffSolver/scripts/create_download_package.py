import zipfile
import io
import json
import pandas as pd
import os


def create_download_package(results):
    """Create a downloadable package with all results"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add JSON results
        zip_file.writestr('results.json', json.dumps(results, indent=2))
        
        # Add CSV results
        if 'test_cases' in results:
            lang1 = results['languages']['program1']
            lang2 = results['languages']['program2']
            
            df_data = []
            for case_name, case_data in results['test_cases'].items():
                speedup = case_data['program1']['runtime'] / case_data['program2']['runtime'] if case_data['program2']['runtime'] > 0 else 0
                df_data.append({
                    'Test Case': case_name,
                    f'{lang1.title()} Runtime (s)': case_data['program1']['runtime'],
                    f'{lang2.title()} Runtime (s)': case_data['program2']['runtime'],
                    'Speedup Factor': speedup
                })
            
            df = pd.DataFrame(df_data)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            zip_file.writestr('results.csv', csv_buffer.getvalue())
        
        # Add plot images if they exist
        if os.path.exists('results/runtime_comparison.png'):
            zip_file.write('results/runtime_comparison.png', 'runtime_comparison.png')
    
    zip_buffer.seek(0)
    return zip_buffer
