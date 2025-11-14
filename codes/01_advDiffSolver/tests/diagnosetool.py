# diagnosetool.py
# -*- coding: utf-8 -*-
import argparse
import os
import sys
import json

from adapters.registry import get_registry
from utils.console_utils import safe_print, configure_windows_console

# Configure Windows console for UTF-8
configure_windows_console()

def read_config_blocks(filename):
    with open(filename, "r") as f:
        content = f.read()
    
    # Split by double newline to support multiple parameter sets
    blocks = content.strip().split("\n\n")
    
    # Filter each block to remove comment lines
    filtered_blocks = []
    for block in blocks:
        # Remove lines starting with # (comments)
        lines = [line for line in block.split('\n') if line.strip() and not line.strip().startswith('#')]
        if lines:
            filtered_blocks.append('\n'.join(lines))
    
    # If no blocks found after filtering, return empty list
    if not filtered_blocks:
        return []
    
    return filtered_blocks

def main():
    parser = argparse.ArgumentParser(
        description="General-purpose benchmark tool for Python, C++, and Julia programs"
    )
    parser.add_argument("--py", nargs='+', help="Python script path(s)")
    parser.add_argument("--cpp", nargs='+', help="C++ source path(s)")
    parser.add_argument("--jl", nargs='+', help="Julia script path(s)")
    parser.add_argument("--config", required=True, help="Path to configuration file with parameter sets")
    args = parser.parse_args()

    # Get the language registry
    registry = get_registry()
    
    # Collect all programs with their adapters
    programs = []
    
    # Python programs
    if args.py:
        adapter = registry.get_adapter_by_name('python')
        if adapter:
            for py_file in args.py:
                programs.append({
                    "type": "python",
                    "file": py_file,
                    "adapter": adapter
                })
        else:
            print("[ERROR] Python adapter not found")
            sys.exit(1)
    
    # C++ programs
    if args.cpp:
        adapter = registry.get_adapter_by_name('cpp')
        if adapter:
            for cpp_file in args.cpp:
                programs.append({
                    "type": "cpp",
                    "file": cpp_file,
                    "adapter": adapter
                })
        else:
            print("[ERROR] C++ adapter not found")
            sys.exit(1)
    
    # Julia programs
    if args.jl:
        adapter = registry.get_adapter_by_name('julia')
        if adapter:
            for jl_file in args.jl:
                programs.append({
                    "type": "julia",
                    "file": jl_file,
                    "adapter": adapter
                })
        else:
            print("[ERROR] Julia adapter not found")
            sys.exit(1)
    
    # Validate: need at least 2 programs
    if len(programs) < 2:
        print("[ERROR] Need at least 2 programs to benchmark (use --py, --cpp, and/or --jl)")
        sys.exit(1)
    
    print(f"\n[OK] Benchmarking {len(programs)} programs:")
    for i, prog in enumerate(programs):
        adapter = prog['adapter']
        safe_print(f"  Program {i+1}: {adapter.emoji} {adapter.display_name} - {prog['file']}")
    
    # Read configuration blocks
    config_blocks = read_config_blocks(args.config)
    print(f"\nFound {len(config_blocks)} configuration block(s)")

    # Prepare all programs (compile if needed)
    print("\n=== Preparing Programs ===")
    for prog in programs:
        adapter = prog['adapter']
        safe_print(f"\nPreparing {adapter.display_name} program: {prog['file']}")
        
        success, prepared_file, error = adapter.prepare(prog['file'])
        
        if not success:
            print(f"[ERROR] Failed to prepare {prog['file']}: {error}")
            sys.exit(1)
        
        prog['prepared_file'] = prepared_file
        safe_print(f"✓ Ready: {prepared_file}")
    
    # Warm-up runs
    print("\n=== Performing Warm-up Runs ===")
    for prog in programs:
        adapter = prog['adapter']
        adapter.warmup(prog['prepared_file'])

    # Benchmark all configurations
    print("\n=== Running Benchmarks ===")
    all_results = []

    for idx, config_block in enumerate(config_blocks):
        print(f"\n--- Configuration Block #{idx + 1} ---")
        print(f"Config preview: {config_block[:100]}..." if len(config_block) > 100 else f"Config: {config_block}")
        
        result_entry = {"config": config_block}
        
        # Measure execution for each program
        for prog in programs:
            adapter = prog['adapter']
            
            print(f"\nExecuting {adapter.display_name}...")
            metrics = adapter.execute(prog['prepared_file'], config_block)
            result_entry[prog['type']] = metrics
            
            # Check for errors
            if metrics["returncode"] != 0:
                print(f"[WARNING] {adapter.display_name} execution failed with return code {metrics['returncode']}")
                print(f"stderr: {metrics['stderr'][:200]}")
            
            print(f"{adapter.display_name} runtime: {metrics['runtime']:.4f}s")
            if 'compilation_time' in metrics and metrics['compilation_time'] > 0:
                print(f"{adapter.display_name} compilation time: {metrics['compilation_time']:.4f}s")
            print(f"{adapter.display_name} total time: {metrics.get('total_time', metrics['runtime']):.4f}s")
        
        # Calculate speedup (first vs second program)
        if len(programs) >= 2:
            prog1_time = result_entry[programs[0]['type']]['runtime']
            prog2_time = result_entry[programs[1]['type']]['runtime']
            speedup = prog1_time / prog2_time if prog2_time > 0 else 0
            print(f"\nSpeedup ({programs[0]['type']} vs {programs[1]['type']}): {speedup:.2f}x")

        all_results.append(result_entry)

    # Cleanup
    print("\n=== Cleaning Up ===")
    for prog in programs:
        adapter = prog['adapter']
        adapter.cleanup(prog.get('prepared_file', ''))

    # Save results
    os.makedirs("results", exist_ok=True)
    with open("results/all_metrics.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print("\n[OK] Saved all metrics to results/all_metrics.json")
    print("[OK] Benchmark complete!")


if __name__ == "__main__":
    main()
