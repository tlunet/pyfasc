def format_benchmark_results(raw_results, program1_lang, program2_lang):
    formatted_results = {
        'test_cases': {},
        'languages': {
            'program1': program1_lang,
            'program2': program2_lang
        }
    }
    
    for i, test_case in enumerate(raw_results):
        case_name = f"Test Case {i+1}"
        
        # Extract config preview (first line or truncated)
        config_preview = test_case.get('config', '')[:50]
        
        formatted_results['test_cases'][case_name] = {
            'config': test_case.get('config', ''),
            'program1': {
                'runtime': test_case.get(program1_lang, {}).get('runtime', 0),
                'total_time': test_case.get(program1_lang, {}).get('total_time', 
                                test_case.get(program1_lang, {}).get('runtime', 0)),
                'compilation_time': test_case.get(program1_lang, {}).get('compilation_time', 0),
                'returncode': test_case.get(program1_lang, {}).get('returncode', 0)
            },
            'program2': {
                'runtime': test_case.get(program2_lang, {}).get('runtime', 0),
                'total_time': test_case.get(program2_lang, {}).get('total_time', 
                                test_case.get(program2_lang, {}).get('runtime', 0)),
                'compilation_time': test_case.get(program2_lang, {}).get('compilation_time', 0),
                'returncode': test_case.get(program2_lang, {}).get('returncode', 0)
            }
        }
    
    return formatted_results


def calculate_summary_metrics(results):
    if 'test_cases' not in results:
        return None
    
    test_cases = results['test_cases']
    
    if not test_cases:
        return None
    
    # Extract runtime values
    prog1_times = [case['program1']['runtime'] for case in test_cases.values()]
    prog2_times = [case['program2']['runtime'] for case in test_cases.values()]
    
    # Extract total time values
    prog1_total_times = [
        case['program1'].get('total_time', case['program1']['runtime']) 
        for case in test_cases.values()
    ]
    prog2_total_times = [
        case['program2'].get('total_time', case['program2']['runtime']) 
        for case in test_cases.values()
    ]
    
    # Calculate speedups
    speedups = [p1/p2 for p1, p2 in zip(prog1_times, prog2_times) if p2 > 0]
    total_speedups = [p1/p2 for p1, p2 in zip(prog1_total_times, prog2_total_times) if p2 > 0]
    
    return {
        'num_test_cases': len(test_cases),
        'prog1_avg_runtime': sum(prog1_times) / len(prog1_times) if prog1_times else 0,
        'prog2_avg_runtime': sum(prog2_times) / len(prog2_times) if prog2_times else 0,
        'prog1_avg_total': sum(prog1_total_times) / len(prog1_total_times) if prog1_total_times else 0,
        'prog2_avg_total': sum(prog2_total_times) / len(prog2_total_times) if prog2_total_times else 0,
        'avg_speedup': sum(speedups) / len(speedups) if speedups else 0,
        'avg_total_speedup': sum(total_speedups) / len(total_speedups) if total_speedups else 0,
        'max_speedup': max(speedups) if speedups else 0
    }
