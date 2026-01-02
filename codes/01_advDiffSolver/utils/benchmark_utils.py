import subprocess
import sys
import json
import os


def run_benchmark(program1_file, program1_lang, program2_file, program2_lang, config_file):
    try:
        # Build command based on languages
        cmd = [sys.executable, 'diagnosetool.py']
        
        # Map language names to command-line flags
        lang_flag_map = {
            'python': '--py',
            'cpp': '--cpp',
            'julia': '--jl'
        }
        
        # Add program 1
        flag1 = lang_flag_map.get(program1_lang)
        if flag1:
            cmd.extend([flag1, program1_file])
        else:
            return False, f"Unsupported language: {program1_lang}"
        
        # Add program 2
        flag2 = lang_flag_map.get(program2_lang)
        if flag2:
            cmd.extend([flag2, program2_file])
        else:
            return False, f"Unsupported language: {program2_lang}"
        
        # Add config
        cmd.extend(['--config', config_file])
        
        # Run the benchmark
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
            return False, f"Benchmark failed:\n{error_msg}\nCommand: {' '.join(cmd)}"
        
        # Load results
        try:
            with open('results/all_metrics.json', 'r') as f:
                raw_results = json.load(f)
            
            # Import the formatting function from results_utils
            from .results_utils import format_benchmark_results
            formatted_results = format_benchmark_results(raw_results, program1_lang, program2_lang)
            
            return True, formatted_results
            
        except Exception as e:
            return False, f"Could not load results: {e}"
            
    except Exception as e:
        return False, f"Error running benchmark: {e}"
