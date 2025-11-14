import streamlit as st
import os
import tempfile
import json
import shutil

# Import utility functions
from utils.file_utils import detect_language
from utils.session_utils import init_session_state
from utils.benchmark_utils import run_benchmark
from utils.results_utils import calculate_summary_metrics
from utils.ui_utils import load_custom_css, get_language_emoji

# Import plot and table creation functions
from scripts.create_bar_chart import create_bar_chart
from scripts.create_loglog_chart import create_loglog_chart, create_loglog_chart_total
from scripts.create_results_table import create_results_table
from scripts.create_csv_data import create_csv_data
from scripts.create_download_package import create_download_package

# Page configuration
st.set_page_config(
    page_title="CodeBench Performance Analyzer",
    page_icon="⚡",
    layout="centered"
)

load_custom_css()

# Initialize session state
init_session_state()

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
        lang_emoji = get_language_emoji(st.session_state.program1_language)
        st.success(f"✅ {lang_emoji} {uploaded_prog1_file.name}")
    elif 'program1_code' in st.session_state and st.session_state.program1_code:
        lang_emoji = get_language_emoji(st.session_state.program1_language)
        st.info(f"{lang_emoji} {st.session_state.get('program1_filename', 'file')} loaded")

with col2:
    st.markdown("**Program 2 (.py/.cpp/.jl)**")
    uploaded_prog2_file = st.file_uploader("Upload second program", type=['py', 'cpp', 'cc', 'cxx', 'jl'], key="prog2_upload")
    if uploaded_prog2_file is not None:
        st.session_state.program2_code = uploaded_prog2_file.read().decode('utf-8')
        st.session_state.program2_filename = uploaded_prog2_file.name
        st.session_state.program2_language = detect_language(uploaded_prog2_file.name)
        lang_emoji = get_language_emoji(st.session_state.program2_language)
        st.success(f"✅ {lang_emoji} {uploaded_prog2_file.name}")
    elif 'program2_code' in st.session_state and st.session_state.program2_code:
        lang_emoji = get_language_emoji(st.session_state.program2_language)
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
                from utils.ui_utils import get_language_display_name
                lang_display = get_language_display_name(lang)
                st.code(st.session_state.program1_code[:1000] + ("..." if len(st.session_state.program1_code) > 1000 else ""), language=lang_display)
            else:
                st.info("No program 1 uploaded yet")
        
        with preview_tab2:
            if st.session_state.get('program2_code'):
                lang = st.session_state.get('program2_language', 'text')
                from utils.ui_utils import get_language_display_name
                lang_display = get_language_display_name(lang)
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
                
                # Copy utils and adapters directories (needed by diagnosetool.py)
                shutil.copytree(os.path.join(original_cwd, 'utils'), 'utils')
                shutil.copytree(os.path.join(original_cwd, 'adapters'), 'adapters')
                
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
        # Calculate metrics using utility function
        metrics = calculate_summary_metrics(results)
        
        if metrics:
            with col1:
                st.metric("Test Cases", metrics['num_test_cases'])
            with col2:
                st.metric(f"Avg {lang1.title()} Time", f"{metrics['prog1_avg_runtime']:.3f}s")
            with col3:
                st.metric(f"Avg {lang2.title()} Time", f"{metrics['prog2_avg_runtime']:.3f}s")
            with col4:
                st.metric("Avg Speedup", f"{metrics['avg_speedup']:.2f}x")
            
            # Additional metrics row for total time
            st.markdown("**Total Time (including compilation):**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(f"Avg {lang1.title()} Total", f"{metrics['prog1_avg_total']:.3f}s")
            with col2:
                st.metric(f"Avg {lang2.title()} Total", f"{metrics['prog2_avg_total']:.3f}s")
            with col3:
                st.metric("Avg Total Speedup", f"{metrics['avg_total_speedup']:.2f}x")
    
    # Performance plots
    line_chart_path = create_loglog_chart(results)
    line_chart_total_path = create_loglog_chart_total(results)
    bar_fig = create_bar_chart(results)
    
    if line_chart_path and os.path.exists(line_chart_path):
        st.markdown("### 📈 Execution Time Comparison (Log-Log)")
        st.image(line_chart_path, use_column_width=True, 
                caption="Execution time only (compilation excluded) - logarithmic scales on both axes")
    
    if line_chart_total_path and os.path.exists(line_chart_total_path):
        st.markdown("### 📈 Total Time Comparison (Log-Log)")
        st.image(line_chart_total_path, use_column_width=True, 
                caption="Total time including compilation - logarithmic scales on both axes")
    
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
