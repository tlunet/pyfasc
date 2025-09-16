import streamlit as st
import subprocess
import os
import sys
import tempfile
import json
import shutil
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import zipfile
import io
import glob
from PIL import Image
import re

# Import the language registry
from adapters.registry import get_registry

# Import plot and table creation functions
from scripts.create_bar_chart import create_bar_chart
from scripts.create_loglog_chart import create_loglog_chart
from scripts.create_results_table import create_results_table
from scripts.create_csv_data import create_csv_data
from scripts.create_download_package import create_download_package

# Page configuration
st.set_page_config(
    page_title="CodeBench Performance Analyzer",
    page_icon="⚡",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Limit main container width */
    .main .block-container {
        max-width: 1200px;
        margin: 0 auto;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Custom styling */
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'program1_code' not in st.session_state:
    st.session_state.program1_code = ""
if 'program1_filename' not in st.session_state:
    st.session_state.program1_filename = ""
if 'program1_language' not in st.session_state:
    st.session_state.program1_language = ""
    
if 'program2_code' not in st.session_state:
    st.session_state.program2_code = ""
if 'program2_filename' not in st.session_state:
    st.session_state.program2_filename = ""
if 'program2_language' not in st.session_state:
    st.session_state.program2_language = ""
    
if 'config_content' not in st.session_state:
    st.session_state.config_content = ""
if 'benchmark_results' not in st.session_state:
    st.session_state.benchmark_results = None

# Get the language registry
registry = get_registry()

def detect_language(filename):
    """Detect programming language from file extension using registry"""
    return registry.detect_language(filename) or 'unknown'

def run_benchmark(program1_file, program1_lang, program2_file, program2_lang, config_file):
    """Run the benchmark using diagnosetool.py with the new adapter architecture"""
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
        
        # Add config
        cmd.extend(['--config', config_file])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode != 0:
            return False, f"Benchmark failed: {result.stderr}"
        
        # Load results
        try:
            with open('results/all_metrics.json', 'r') as f:
                raw_results = json.load(f)
            
            # Convert to expected format
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
                        'returncode': test_case.get(program1_lang, {}).get('returncode', 0)
                    },
                    'program2': {
                        'runtime': test_case.get(program2_lang, {}).get('runtime', 0),
                        'returncode': test_case.get(program2_lang, {}).get('returncode', 0)
                    }
                }
            
            return True, formatted_results
        except Exception as e:
            return False, f"Could not load results: {e}"
            
    except Exception as e:
        return False, f"Error running benchmark: {e}"

# Main UI
st.markdown('<div class="main-header">⚡ CodeBench Performance Analyzer</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    <strong>📌 General Purpose Benchmark Tool</strong><br>
    Upload two programs (Python, C++, or Julia) along with a configuration file. 
    The tool will measure and compare their runtime performance.
</div>
""", unsafe_allow_html=True)

# File Upload Section
st.markdown('<div class="section-header">📁 Upload Files</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Program 1 (.py/.cpp/.jl)**")
    uploaded_prog1_file = st.file_uploader("Upload first program", type=['py', 'cpp', 'cc', 'cxx', 'jl'], key="prog1_upload")
    if uploaded_prog1_file is not None:
        st.session_state.program1_code = uploaded_prog1_file.read().decode('utf-8')
        st.session_state.program1_filename = uploaded_prog1_file.name
        st.session_state.program1_language = detect_language(uploaded_prog1_file.name)
        lang_emoji = {"python": "🐍", "cpp": "⚙️", "julia": "🔬"}.get(st.session_state.program1_language, "📄")
        st.success(f"✅ {lang_emoji} {uploaded_prog1_file.name}")
    elif 'program1_code' in st.session_state and st.session_state.program1_code:
        lang_emoji = {"python": "🐍", "cpp": "⚙️", "julia": "🔬"}.get(st.session_state.program1_language, "📄")
        st.info(f"{lang_emoji} {st.session_state.get('program1_filename', 'file')} loaded")

with col2:
    st.markdown("**Program 2 (.py/.cpp/.jl)**")
    uploaded_prog2_file = st.file_uploader("Upload second program", type=['py', 'cpp', 'cc', 'cxx', 'jl'], key="prog2_upload")
    if uploaded_prog2_file is not None:
        st.session_state.program2_code = uploaded_prog2_file.read().decode('utf-8')
        st.session_state.program2_filename = uploaded_prog2_file.name
        st.session_state.program2_language = detect_language(uploaded_prog2_file.name)
        lang_emoji = {"python": "🐍", "cpp": "⚙️", "julia": "🔬"}.get(st.session_state.program2_language, "📄")
        st.success(f"✅ {lang_emoji} {uploaded_prog2_file.name}")
    elif 'program2_code' in st.session_state and st.session_state.program2_code:
        lang_emoji = {"python": "🐍", "cpp": "⚙️", "julia": "🔬"}.get(st.session_state.program2_language, "📄")
        st.info(f"{lang_emoji} {st.session_state.get('program2_filename', 'file')} loaded")

with col3:
    st.markdown("**Configuration File**")
    uploaded_config_file = st.file_uploader("Upload config file", type=['txt', 'cfg', 'json', 'yaml', 'yml', 'ini'], key="config_upload")
    if uploaded_config_file is not None:
        st.session_state.config_content = uploaded_config_file.read().decode('utf-8')
        st.session_state.config_filename = uploaded_config_file.name
        st.success(f"✅ {uploaded_config_file.name}")
    elif 'config_content' in st.session_state and st.session_state.config_content:
        st.info(f"📄 {st.session_state.get('config_filename', 'config.txt')} loaded")

# Show file previews
if st.session_state.get('program1_code') or st.session_state.get('program2_code') or st.session_state.get('config_content'):
    with st.expander("👁️ Preview Uploaded Files", expanded=False):
        preview_tab1, preview_tab2, preview_tab3 = st.tabs(["Program 1", "Program 2", "Config"])
        
        with preview_tab1:
            if st.session_state.get('program1_code'):
                lang = st.session_state.get('program1_language', 'text')
                lang_display = {"python": "python", "cpp": "cpp", "julia": "julia"}.get(lang, "text")
                st.code(st.session_state.program1_code[:1000] + ("..." if len(st.session_state.program1_code) > 1000 else ""), language=lang_display)
            else:
                st.info("No program 1 uploaded yet")
        
        with preview_tab2:
            if st.session_state.get('program2_code'):
                lang = st.session_state.get('program2_language', 'text')
                lang_display = {"python": "python", "cpp": "cpp", "julia": "julia"}.get(lang, "text")
                st.code(st.session_state.program2_code[:1000] + ("..." if len(st.session_state.program2_code) > 1000 else ""), language=lang_display)
            else:
                st.info("No program 2 uploaded yet")
        
        with preview_tab3:
            if st.session_state.get('config_content'):
                st.code(st.session_state.config_content[:1000] + ("..." if len(st.session_state.config_content) > 1000 else ""), language="text")
                # Show number of config blocks
                config_blocks = st.session_state.config_content.strip().split("\n\n")
                num_blocks = len([b for b in config_blocks if b.strip()])
                st.info(f"📊 Detected {num_blocks} configuration block(s)")
            else:
                st.info("No config file uploaded yet")

# Benchmark execution
st.markdown('<div class="section-header">🚀 Run Benchmark</div>', unsafe_allow_html=True)

# Check if everything is ready
files_provided = bool(
    st.session_state.get('program1_code') and 
    st.session_state.get('program2_code') and 
    st.session_state.config_content
)

if not files_provided:
    missing_items = []
    if not st.session_state.get('program1_code'):
        missing_items.append("Program 1")
    if not st.session_state.get('program2_code'):
        missing_items.append("Program 2")
    if not st.session_state.get('config_content'):
        missing_items.append("Config file")
    
    st.warning(f"⚠️ Please upload: {', '.join(missing_items)}")

col1, col2 = st.columns([1, 3])

with col1:
    run_button = st.button(
        "🏃‍♂️ Run Benchmark",
        disabled=not files_provided,
        type="primary"
    )

if run_button and files_provided:
    with st.spinner("Running benchmark... This may take a few minutes."):
        # Create temporary files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write program files
            prog1_filename = st.session_state.get('program1_filename', 'program1.py')
            prog2_filename = st.session_state.get('program2_filename', 'program2.py')
            config_filename = st.session_state.get('config_filename', 'config.txt')
            
            prog1_file = os.path.join(temp_dir, prog1_filename)
            prog2_file = os.path.join(temp_dir, prog2_filename)
            config_file = os.path.join(temp_dir, config_filename)
            
            with open(prog1_file, 'w', encoding='utf-8') as f:
                f.write(st.session_state.program1_code)
            
            with open(prog2_file, 'w', encoding='utf-8') as f:
                f.write(st.session_state.program2_code)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(st.session_state.config_content)
            
            # Change to temp directory and run benchmark
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                # Copy diagnosetool.py
                shutil.copy(os.path.join(original_cwd, 'tests', 'diagnosetool.py'), '.')
                
                success, results = run_benchmark(
                    prog1_filename, 
                    st.session_state.program1_language,
                    prog2_filename, 
                    st.session_state.program2_language,
                    config_filename
                )
                
                # Copy results back
                if success and os.path.exists('results'):
                    if os.path.exists(os.path.join(original_cwd, 'results')):
                        shutil.rmtree(os.path.join(original_cwd, 'results'))
                    shutil.copytree('results', os.path.join(original_cwd, 'results'))
                
                # Copy gif_frames back if they exist
                if os.path.exists('gif_frames'):
                    gif_frames_dest = os.path.join(original_cwd, 'gif_frames')
                    if os.path.exists(gif_frames_dest):
                        shutil.rmtree(gif_frames_dest)
                    shutil.copytree('gif_frames', gif_frames_dest)
                
            finally:
                os.chdir(original_cwd)
            
            if success:
                st.session_state.benchmark_results = results
                st.success("✅ Benchmark completed successfully!")
                # Force rerun to update GIF display
                st.rerun()
            else:
                st.error(f"❌ Benchmark failed: {results}")

# Results section
if st.session_state.benchmark_results:
    st.markdown('<div class="section-header">📊 Results</div>', unsafe_allow_html=True)
    
    results = st.session_state.benchmark_results
    lang1 = results['languages']['program1']
    lang2 = results['languages']['program2']
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    if 'test_cases' in results:
        test_cases = results['test_cases']
        prog1_times = [case['program1']['runtime'] for case in test_cases.values()]
        prog2_times = [case['program2']['runtime'] for case in test_cases.values()]
        
        avg_speedup = sum(p1/p2 for p1, p2 in zip(prog1_times, prog2_times) if p2 > 0) / len(prog1_times)
        max_speedup = max((p1/p2 for p1, p2 in zip(prog1_times, prog2_times) if p2 > 0), default=0)
        
        with col1:
            st.metric("Test Cases", len(test_cases))
        with col2:
            st.metric(f"Avg {lang1.title()} Time", f"{sum(prog1_times)/len(prog1_times):.3f}s")
        with col3:
            st.metric(f"Avg {lang2.title()} Time", f"{sum(prog2_times)/len(prog2_times):.3f}s")
        with col4:
            st.metric("Avg Speedup", f"{avg_speedup:.2f}x")
    
    # Performance plots
    line_chart_path = create_loglog_chart(results)
    bar_fig = create_bar_chart(results)
    
    if line_chart_path and os.path.exists(line_chart_path):
        st.markdown("### 📈 Runtime Trend (Log-Log Line Chart)")
        st.image(line_chart_path, use_column_width=True, caption="Runtime comparison with logarithmic scales on both axes")
    
    if bar_fig:
        st.markdown("### 📊 Runtime Comparison (Bar Chart)")
        st.plotly_chart(bar_fig, use_container_width=True)
    
    # Look for generated PNG files in results directory
    results_dir = "results"
    if os.path.exists(results_dir):
        # Performance comparison plot
        perf_comp_path = os.path.join(results_dir, "performance_comparison.png")
        if os.path.exists(perf_comp_path):
            st.markdown("**Performance Comparison Overview**")
            st.image(perf_comp_path, caption="Comprehensive performance comparison generated by diagnosetool.py", use_container_width=True)
        
        # Runtime plot (always single plot)
        runtime_plot_path = os.path.join(results_dir, "runtime_by_input.png")
        if os.path.exists(runtime_plot_path):
            st.markdown("**Runtime by Input Size**")
            st.image(runtime_plot_path, caption="Runtime comparison across different input sizes", use_container_width=True)
    
    # Additional visualizations can be added here if needed
    st.markdown("---")
    
    # Detailed results table
    if 'test_cases' in results:
        st.subheader("📋 Detailed Results")
        
        df = create_results_table(results)
        if df is not None:
            st.dataframe(df, use_container_width=True)
    
    # Download section
    st.subheader("💾 Download Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="📄 Download JSON",
            data=json.dumps(results, indent=2),
            file_name="benchmark_results.json",
            mime="application/json"
        )
    
    with col2:
        if 'test_cases' in results:
            csv_data = create_csv_data(results)
            
            if csv_data is not None:
                st.download_button(
                    label="📊 Download CSV",
                    data=csv_data.to_csv(index=False),
                    file_name="benchmark_results.csv",
                    mime="text/csv"
                )
    
    with col3:
        zip_package = create_download_package(results)
        st.download_button(
            label="📦 Download All",
            data=zip_package.getvalue(),
            file_name="benchmark_results.zip",
            mime="application/zip"
        )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    CodeBench Performance Analyzer v2.0 | General Purpose Benchmark Tool
</div>
""", unsafe_allow_html=True)
