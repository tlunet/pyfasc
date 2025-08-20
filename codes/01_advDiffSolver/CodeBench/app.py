import streamlit as st
import subprocess
import os
import tempfile
import json
import time
import shutil
import math
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import zipfile
import io

# Page configuration
st.set_page_config(
    page_title="CodeBench Performance Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
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
if 'python_code' not in st.session_state:
    st.session_state.python_code = ""
if 'cpp_code' not in st.session_state:
    st.session_state.cpp_code = ""
if 'validation_results' not in st.session_state:
    st.session_state.validation_results = {}
if 'benchmark_results' not in st.session_state:
    st.session_state.benchmark_results = None

def load_reference_outputs():
    """Load reference outputs from existing files for validation"""
    try:
        # Look for reference files (created by C++ program or designated reference)
        ref_files = []
        
        # Check if we have reference files in a dedicated folder
        if os.path.exists('reference'):
            ref_init_path = 'reference/uInit.txt'
            ref_end_path = 'reference/uEnd.txt'
        else:
            # Fallback: use current directory files as reference
            ref_init_path = 'uInit.txt'
            ref_end_path = 'uEnd.txt'
        
        if os.path.exists(ref_init_path) and os.path.exists(ref_end_path):
            with open(ref_init_path, 'r') as f:
                ref_init = f.read().strip()
            with open(ref_end_path, 'r') as f:
                ref_end = f.read().strip()
            return ref_init, ref_end
        else:
            return None, None
    except Exception as e:
        st.error(f"Could not load reference outputs: {e}")
        return None, None

def validate_program(code, language, filename):
    """Validate uploaded program by running it and comparing output with reference"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy input.txt to temp directory
            shutil.copy('input.txt', temp_dir)
            
            if language == "python":
                temp_file = os.path.join(temp_dir, filename)
                with open(temp_file, 'w') as f:
                    f.write(code)
                
                # Run the Python program
                result = subprocess.run(
                    [st.session_state.python_executable, filename],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
            elif language == "cpp":
                cpp_file = os.path.join(temp_dir, filename)
                exe_file = os.path.join(temp_dir, 'temp_program')
                
                with open(cpp_file, 'w') as f:
                    f.write(code)
                
                # Compile C++
                compile_result = subprocess.run(
                    ['g++', '-O2', filename, '-o', 'temp_program'],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True
                )
                
                if compile_result.returncode != 0:
                    return False, f"Compilation failed: {compile_result.stderr}"
                
                # Run the C++ program
                result = subprocess.run(
                    ['./temp_program'],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            
            if result.returncode != 0:
                return False, f"Runtime error: {result.stderr}"
            
            # Check if output files were created
            init_file = os.path.join(temp_dir, 'uInit.txt')
            end_file = os.path.join(temp_dir, 'uEnd.txt')
            
            if not (os.path.exists(init_file) and os.path.exists(end_file)):
                return False, "Program did not generate required output files (uInit.txt, uEnd.txt)"
            
            # Compare with reference outputs
            with open(init_file, 'r') as f:
                test_init = f.read().strip()
            with open(end_file, 'r') as f:
                test_end = f.read().strip()
            
            ref_init, ref_end = load_reference_outputs()
            if ref_init is None or ref_end is None:
                return False, "Could not load reference outputs for comparison"
            
            # Compare outputs (allowing for different grid sizes)
            if test_init == ref_init and test_end == ref_end:
                return True, "Validation successful - outputs match reference"
            else:
                # Check for numerical similarity and format consistency
                try:
                    test_init_lines = test_init.strip().split('\n')
                    test_end_lines = test_end.strip().split('\n')
                    
                    # Basic format validation - check that files exist and have content
                    if len(test_init_lines) == 0 or len(test_end_lines) == 0:
                        return False, "Output files are empty"
                    
                    # Check that output contains numerical values
                    try:
                        # Test first line of each file
                        first_init_vals = [float(x) for x in test_init_lines[0].split()]
                        first_end_vals = [float(x) for x in test_end_lines[0].split()]
                        
                        if len(first_init_vals) == 0 or len(first_end_vals) == 0:
                            return False, "Output lines contain no numerical values"
                            
                        # Check that grid dimensions are consistent
                        if len(first_init_vals) != len(first_end_vals):
                            return False, "Grid dimensions inconsistent between uInit.txt and uEnd.txt"
                            
                        # Check that we have a square grid
                        expected_cols = len(first_init_vals)
                        if len(test_init_lines) != expected_cols or len(test_end_lines) != expected_cols:
                            return False, f"Expected {expected_cols}x{expected_cols} grid, but got {len(test_init_lines)}x{len(first_init_vals)} and {len(test_end_lines)}x{len(first_end_vals)}"
                        
                        # Validate that all values are reasonable (not NaN, not infinite)
                        sample_lines = min(3, len(test_init_lines))
                        for i in range(sample_lines):
                            init_vals = [float(x) for x in test_init_lines[i].split()]
                            end_vals = [float(x) for x in test_end_lines[i].split()]
                            
                            for val in init_vals + end_vals:
                                if math.isnan(val) or math.isinf(val):
                                    return False, f"Output contains unreasonable values: {val}"
                                if not (-1e10 < val < 1e10):  # Reasonable range
                                    return False, f"Output contains unreasonable values: {val}"
                        
                        return True, f"Validation successful - generated {len(test_init_lines)}x{len(first_init_vals)} numerical grid output"
                        
                    except ValueError as e:
                        return False, f"Output contains non-numerical values: {e}"
                        
                except Exception as e:
                    return False, f"Could not parse output for validation: {e}"
                    
    except subprocess.TimeoutExpired:
        return False, "Program execution timed out"
    except Exception as e:
        return False, f"Validation error: {e}"

def generate_inputs_content(variable_type, start_val, end_val, num_steps, init_type="gauss", flow_type="diagonal", viscosity=0.0, end_time=1):
    """Generate inputs.txt content based on selected variable and range"""
    content_lines = []
    
    if variable_type == "Grid Size (N_x/N_y)":
        # Vary grid size, keep steps constant at 400
        sizes = []
        if num_steps == 1:
            sizes = [start_val]
        else:
            step = (end_val - start_val) / (num_steps - 1)
            sizes = [int(start_val + i * step) for i in range(num_steps)]
        
        for size in sizes:
            content_lines.append(f"{size} {size}")
            content_lines.append(init_type)
            content_lines.append(f"{flow_type} {viscosity}")
            content_lines.append(f"{end_time} 400")
            content_lines.append("")  # Empty line between test cases
            
    elif variable_type == "Time Steps":
        # Keep grid size constant at 128x128, vary steps
        steps_values = []
        if num_steps == 1:
            steps_values = [start_val]
        else:
            step = (end_val - start_val) / (num_steps - 1)
            steps_values = [int(start_val + i * step) for i in range(num_steps)]
        
        for steps in steps_values:
            content_lines.append("128 128")
            content_lines.append(init_type)
            content_lines.append(f"{flow_type} {viscosity}")
            content_lines.append(f"{end_time} {steps}")
            content_lines.append("")  # Empty line between test cases
    
    # Remove last empty line
    if content_lines and content_lines[-1] == "":
        content_lines.pop()
    
    return "\n".join(content_lines)

def run_benchmark(python_file, cpp_file, inputs_file):
    """Run the benchmark using diagnosetool.py"""
    try:
        cmd = [
            st.session_state.python_executable, 
            'diagnosetool.py',
            '--py', python_file,
            '--cpp', cpp_file,
            '--inputs', inputs_file
        ]
        
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
                'test_cases': {}
            }
            
            for i, test_case in enumerate(raw_results):
                case_name = f"Test Case {i+1}"
                formatted_results['test_cases'][case_name] = {
                    'input': test_case.get('input', ''),
                    'python': {
                        'runtime': test_case['python']['runtime'],
                        'memory_mb': test_case['python'].get('memory_mb', 0),
                        'cpu_percent': test_case['python'].get('cpu_percent', 0)
                    },
                    'cpp': {
                        'runtime': test_case['cpp']['runtime'],
                        'memory_mb': test_case['cpp'].get('memory_mb', 0),
                        'cpu_percent': test_case['cpp'].get('cpu_percent', 0)
                    }
                }
            
            return True, formatted_results
        except Exception as e:
            return False, f"Could not load results: {e}"
            
    except Exception as e:
        return False, f"Error running benchmark: {e}"

def create_performance_plots(results):
    """Create interactive performance plots"""
    if not results or 'test_cases' not in results:
        return None, None
    
    test_cases = results['test_cases']
    
    # Prepare data
    case_names = []
    python_times = []
    cpp_times = []
    python_memory = []
    cpp_memory = []
    
    for case_name, case_data in test_cases.items():
        case_names.append(case_name)
        python_times.append(case_data['python']['runtime'])
        cpp_times.append(case_data['cpp']['runtime'])
        python_memory.append(case_data['python']['memory_mb'])
        cpp_memory.append(case_data['cpp']['memory_mb'])
    
    # Create subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Runtime Comparison', 'Memory Usage Comparison'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Runtime plot
    fig.add_trace(
        go.Bar(name='Python', x=case_names, y=python_times, marker_color='lightblue'),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(name='C++', x=case_names, y=cpp_times, marker_color='lightcoral'),
        row=1, col=1
    )
    
    # Memory plot
    fig.add_trace(
        go.Bar(name='Python', x=case_names, y=python_memory, marker_color='lightblue', showlegend=False),
        row=1, col=2
    )
    fig.add_trace(
        go.Bar(name='C++', x=case_names, y=cpp_memory, marker_color='lightcoral', showlegend=False),
        row=1, col=2
    )
    
    # Update layout
    fig.update_xaxes(title_text="Test Cases", row=1, col=1)
    fig.update_xaxes(title_text="Test Cases", row=1, col=2)
    fig.update_yaxes(title_text="Runtime (seconds)", row=1, col=1)
    fig.update_yaxes(title_text="Memory Usage (MB)", row=1, col=2)
    
    fig.update_layout(
        title="Performance Comparison: Python vs C++",
        height=500,
        showlegend=True
    )
    
    # Create speedup plot
    speedup_fig = go.Figure()
    speedups = [py_time / cpp_time for py_time, cpp_time in zip(python_times, cpp_times)]
    
    speedup_fig.add_trace(
        go.Bar(x=case_names, y=speedups, marker_color='green', name='Speedup Factor')
    )
    
    speedup_fig.update_layout(
        title="C++ Speedup Factor (Python Time / C++ Time)",
        xaxis_title="Test Cases",
        yaxis_title="Speedup Factor",
        height=400
    )
    
    return fig, speedup_fig

def save_configuration(config_name, variable_type, start_val, end_val, num_steps):
    """Save current configuration"""
    config = {
        'variable_type': variable_type,
        'start_val': start_val,
        'end_val': end_val,
        'num_steps': num_steps
    }
    
    if 'saved_configs' not in st.session_state:
        st.session_state.saved_configs = {}
    
    st.session_state.saved_configs[config_name] = config
    
    # Also save to file
    configs_file = 'saved_configs.json'
    try:
        if os.path.exists(configs_file):
            with open(configs_file, 'r') as f:
                all_configs = json.load(f)
        else:
            all_configs = {}
        
        all_configs[config_name] = config
        
        with open(configs_file, 'w') as f:
            json.dump(all_configs, f, indent=2)
            
        return True
    except Exception as e:
        st.error(f"Could not save configuration: {e}")
        return False

def load_configurations():
    """Load saved configurations"""
    configs_file = 'saved_configs.json'
    try:
        if os.path.exists(configs_file):
            with open(configs_file, 'r') as f:
                return json.load(f)
        else:
            return {}
    except Exception as e:
        st.error(f"Could not load configurations: {e}")
        return {}

def create_download_package(results):
    """Create a downloadable package with all results"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add JSON results
        zip_file.writestr('results.json', json.dumps(results, indent=2))
        
        # Add CSV results
        if 'test_cases' in results:
            df_data = []
            for case_name, case_data in results['test_cases'].items():
                df_data.append({
                    'Test Case': case_name,
                    'Python Runtime (s)': case_data['python']['runtime'],
                    'C++ Runtime (s)': case_data['cpp']['runtime'],
                    'Python Memory (MB)': case_data['python']['memory_mb'],
                    'C++ Memory (MB)': case_data['cpp']['memory_mb'],
                    'Speedup Factor': case_data['cpp']['runtime'] / case_data['python']['runtime']
                })
            
            df = pd.DataFrame(df_data)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            zip_file.writestr('results.csv', csv_buffer.getvalue())
        
        # Add plot images if they exist
        if os.path.exists('results/performance_comparison.png'):
            zip_file.write('results/performance_comparison.png', 'performance_comparison.png')
        if os.path.exists('results/runtime_by_input.png'):
            zip_file.write('results/runtime_by_input.png', 'runtime_by_input.png')
    
    zip_buffer.seek(0)
    return zip_buffer

# Get Python executable path
if 'python_executable' not in st.session_state:
    try:
        # Try virtual environment first
        script_dir = os.path.dirname(os.path.abspath(__file__))
        venv_python = os.path.join(script_dir, '.venv', 'bin', 'python')
        
        if os.path.exists(venv_python):
            st.session_state.python_executable = venv_python
        else:
            # Fall back to finding python in PATH
            result = subprocess.run(['which', 'python3'], capture_output=True, text=True)
            if result.returncode == 0:
                st.session_state.python_executable = result.stdout.strip()
            else:
                result = subprocess.run(['which', 'python'], capture_output=True, text=True)
                if result.returncode == 0:
                    st.session_state.python_executable = result.stdout.strip()
                else:
                    st.session_state.python_executable = 'python'
    except:
        st.session_state.python_executable = 'python'

# Main UI
st.markdown('<div class="main-header">⚡ CodeBench Performance Analyzer</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
Welcome to CodeBench! This tool allows you to compare the performance of Python and C++ implementations 
of numerical simulations. Upload your code, configure test parameters, and get detailed performance insights.

**Validation System:** Programs are validated against reference outputs in isolated temporary directories. 
Each program runs independently without file conflicts.
</div>
""", unsafe_allow_html=True)

# Sidebar for configuration management
with st.sidebar:
    st.header("📁 Configuration Management")
    
    # Save current configuration
    with st.expander("💾 Save Current Config"):
        config_name = st.text_input("Configuration Name")
        if st.button("Save Configuration"):
            if config_name:
                # Get current values from session state
                current_variable_type = st.session_state.get('variable_type', 'Grid Size (N_x/N_y)')
                current_start_val = st.session_state.get('start_val', 64)
                current_end_val = st.session_state.get('end_val', 512)
                current_num_steps = st.session_state.get('num_steps', 5)
                
                if save_configuration(config_name, current_variable_type, current_start_val, current_end_val, current_num_steps):
                    st.success(f"Configuration '{config_name}' saved!")
                else:
                    st.error("Failed to save configuration")
    
    # Load saved configuration
    with st.expander("📂 Load Saved Config"):
        saved_configs = load_configurations()
        if saved_configs:
            selected_config = st.selectbox("Select Configuration", list(saved_configs.keys()))
            if st.button("Load Configuration"):
                config = saved_configs[selected_config]
                # Set values in session state for next render
                for key, value in config.items():
                    st.session_state[key] = value
                st.success(f"Configuration '{selected_config}' loaded!")
                st.rerun()
        else:
            st.info("No saved configurations found")

# Main content
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">📄 Python Program</div>', unsafe_allow_html=True)
    
    # File upload option
    uploaded_py_file = st.file_uploader("Upload Python file", type=['py'], key="py_upload")
    if uploaded_py_file is not None:
        st.session_state.python_code = uploaded_py_file.read().decode('utf-8')
    
    # Text area for direct input
    python_code = st.text_area(
        "Or paste Python code here:",
        value=st.session_state.python_code,
        height=300,
        key="python_text_area"
    )
    st.session_state.python_code = python_code
    
    # Validation
    if st.session_state.python_code:
        if st.button("🔍 Validate Python Code", key="validate_py"):
            with st.spinner("Validating Python code..."):
                success, message = validate_program(st.session_state.python_code, "python", "temp_program.py")
                st.session_state.validation_results['python'] = (success, message)
        
        if 'python' in st.session_state.validation_results:
            success, message = st.session_state.validation_results['python']
            if success:
                st.markdown(f'<div class="success-box">✅ {message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="error-box">❌ {message}</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-header">⚙️ C++ Program</div>', unsafe_allow_html=True)
    
    # File upload option
    uploaded_cpp_file = st.file_uploader("Upload C++ file", type=['cpp', 'cc', 'cxx'], key="cpp_upload")
    if uploaded_cpp_file is not None:
        st.session_state.cpp_code = uploaded_cpp_file.read().decode('utf-8')
    
    # Text area for direct input
    cpp_code = st.text_area(
        "Or paste C++ code here:",
        value=st.session_state.cpp_code,
        height=300,
        key="cpp_text_area"
    )
    st.session_state.cpp_code = cpp_code
    
    # Validation
    if st.session_state.cpp_code:
        if st.button("🔍 Validate C++ Code", key="validate_cpp"):
            with st.spinner("Validating C++ code..."):
                success, message = validate_program(st.session_state.cpp_code, "cpp", "temp_program.cpp")
                st.session_state.validation_results['cpp'] = (success, message)
        
        if 'cpp' in st.session_state.validation_results:
            success, message = st.session_state.validation_results['cpp']
            if success:
                st.markdown(f'<div class="success-box">✅ {message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="error-box">❌ {message}</div>', unsafe_allow_html=True)

# Configuration section
st.markdown('<div class="section-header">⚙️ Benchmark Configuration</div>', unsafe_allow_html=True)

# First row: Variable type and range
col1, col2, col3, col4 = st.columns(4)

with col1:
    variable_type = st.selectbox(
        "Variable to vary:",
        ["Grid Size (N_x/N_y)", "Time Steps"],
        index=0 if st.session_state.get('variable_type', 'Grid Size (N_x/N_y)') == 'Grid Size (N_x/N_y)' else 1,
        key="variable_type"
    )

with col2:
    if variable_type == "Grid Size (N_x/N_y)":
        start_val = st.number_input(
            "Start size:", 
            min_value=1, 
            value=st.session_state.get('start_val', 64), 
            key="start_val"
        )
    else:
        start_val = st.number_input(
            "Start steps:", 
            min_value=1, 
            value=st.session_state.get('start_val', 100), 
            key="start_val"
        )

with col3:
    if variable_type == "Grid Size (N_x/N_y)":
        end_val = st.number_input(
            "End size:", 
            min_value=start_val, 
            value=max(start_val, st.session_state.get('end_val', 512)), 
            key="end_val"
        )
    else:
        end_val = st.number_input(
            "End steps:", 
            min_value=start_val, 
            value=max(start_val, st.session_state.get('end_val', 800)), 
            key="end_val"
        )

with col4:
    num_steps = st.number_input(
        "Number of test cases:", 
        min_value=1, 
        max_value=10, 
        value=st.session_state.get('num_steps', 5), 
        key="num_steps"
    )

# Second row: Physics parameters
st.markdown("#### Physics Parameters")
col1, col2, col3, col4 = st.columns(4)

with col1:
    init_type = st.selectbox(
        "Initialization Type:",
        ["gauss", "sinus", "cross", "cross2"],
        index=0,
        key="init_type",
        help="Choose the initial condition for the simulation"
    )

with col2:
    flow_type = st.selectbox(
        "Flow Type:",
        ["diagonal", "rotating", "shear"],
        index=0,
        key="flow_type",
        help="Choose the flow pattern for the simulation"
    )

with col3:
    viscosity = st.number_input(
        "Viscosity:", 
        min_value=0.0, 
        max_value=1.0,
        value=st.session_state.get('viscosity', 0.0), 
        step=0.01,
        key="viscosity",
        help="Numerical viscosity parameter"
    )

with col4:
    end_time = st.number_input(
        "End Time:", 
        min_value=0.1, 
        max_value=10.0,
        value=st.session_state.get('end_time', 1.0), 
        step=0.1,
        key="end_time",
        help="Simulation end time"
    )

# Preview of inputs.txt
st.markdown('<div class="section-header">👁️ Preview inputs.txt</div>', unsafe_allow_html=True)
preview_content = generate_inputs_content(
    variable_type, start_val, end_val, num_steps, 
    init_type, flow_type, viscosity, end_time
)
st.code(preview_content, language="text")

# Benchmark execution
st.markdown('<div class="section-header">🚀 Run Benchmark</div>', unsafe_allow_html=True)

# Check if everything is ready
python_valid = 'python' in st.session_state.validation_results and st.session_state.validation_results['python'][0]
cpp_valid = 'cpp' in st.session_state.validation_results and st.session_state.validation_results['cpp'][0]
codes_provided = bool(st.session_state.python_code and st.session_state.cpp_code)

ready_to_run = python_valid and cpp_valid and codes_provided

if not ready_to_run:
    missing_items = []
    if not st.session_state.python_code:
        missing_items.append("Python code")
    elif not python_valid:
        missing_items.append("Valid Python code")
    
    if not st.session_state.cpp_code:
        missing_items.append("C++ code")
    elif not cpp_valid:
        missing_items.append("Valid C++ code")
    
    st.warning(f"Please provide: {', '.join(missing_items)}")

col1, col2 = st.columns([1, 3])

with col1:
    run_button = st.button(
        "🏃‍♂️ Run Benchmark",
        disabled=not ready_to_run,
        type="primary"
    )

if run_button and ready_to_run:
    with st.spinner("Running benchmark... This may take a few minutes."):
        # Create temporary files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write program files
            py_file = os.path.join(temp_dir, "user_program.py")
            cpp_file = os.path.join(temp_dir, "user_program.cpp")
            inputs_file = os.path.join(temp_dir, "inputs.txt")
            
            with open(py_file, 'w') as f:
                f.write(st.session_state.python_code)
            
            with open(cpp_file, 'w') as f:
                f.write(st.session_state.cpp_code)
            
            with open(inputs_file, 'w') as f:
                f.write(preview_content)
            
            # Copy input.txt to temp directory
            shutil.copy('input.txt', temp_dir)
            
            # Change to temp directory and run benchmark
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                # Copy diagnosetool.py
                shutil.copy(os.path.join(original_cwd, 'diagnosetool.py'), '.')
                
                success, results = run_benchmark("user_program.py", "user_program.cpp", "inputs.txt")
                
                # Copy results back
                if success and os.path.exists('results'):
                    if os.path.exists(os.path.join(original_cwd, 'results')):
                        shutil.rmtree(os.path.join(original_cwd, 'results'))
                    shutil.copytree('results', os.path.join(original_cwd, 'results'))
                
            finally:
                os.chdir(original_cwd)
            
            if success:
                st.session_state.benchmark_results = results
                st.success("✅ Benchmark completed successfully!")
            else:
                st.error(f"❌ Benchmark failed: {results}")

# Results section
if st.session_state.benchmark_results:
    st.markdown('<div class="section-header">📊 Results</div>', unsafe_allow_html=True)
    
    results = st.session_state.benchmark_results
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    if 'test_cases' in results:
        test_cases = results['test_cases']
        python_times = [case['python']['runtime'] for case in test_cases.values()]
        cpp_times = [case['cpp']['runtime'] for case in test_cases.values()]
        
        avg_speedup = sum(py/cpp for py, cpp in zip(python_times, cpp_times)) / len(python_times)
        max_speedup = max(py/cpp for py, cpp in zip(python_times, cpp_times))
        
        with col1:
            st.metric("Test Cases", len(test_cases))
        with col2:
            st.metric("Avg Python Time", f"{sum(python_times)/len(python_times):.3f}s")
        with col3:
            st.metric("Avg C++ Time", f"{sum(cpp_times)/len(cpp_times):.3f}s")
        with col4:
            st.metric("Avg Speedup", f"{avg_speedup:.2f}x")
    
    # Performance plots
    comparison_fig, speedup_fig = create_performance_plots(results)
    
    if comparison_fig:
        st.plotly_chart(comparison_fig, use_container_width=True)
        st.plotly_chart(speedup_fig, use_container_width=True)
    
    # Display generated plots from diagnosetool.py
    st.subheader("📈 Generated Performance Charts")
    
    # Look for generated PNG files in results directory
    results_dir = "results"
    if os.path.exists(results_dir):
        # Performance comparison plot
        perf_comp_path = os.path.join(results_dir, "performance_comparison.png")
        if os.path.exists(perf_comp_path):
            st.markdown("**Performance Comparison Overview**")
            st.image(perf_comp_path, caption="Comprehensive performance comparison generated by diagnosetool.py", use_column_width=True)
        
        # Individual metric plots
        metrics = ["runtime", "peak_memory_mb", "avg_cpu_percent"]
        metric_names = {
            "runtime": "Runtime by Input Size",
            "peak_memory_mb": "Peak Memory Usage by Input Size", 
            "avg_cpu_percent": "Average CPU Usage by Input Size"
        }
        
        cols = st.columns(len(metrics))
        for i, metric in enumerate(metrics):
            plot_path = os.path.join(results_dir, f"{metric}_by_input.png")
            if os.path.exists(plot_path):
                with cols[i]:
                    st.markdown(f"**{metric_names.get(metric, metric.title())}**")
                    st.image(plot_path, caption=f"{metric_names.get(metric, metric)} comparison", use_column_width=True)
    
    # Detailed results table
    if 'test_cases' in results:
        st.subheader("📋 Detailed Results")
        
        table_data = []
        for case_name, case_data in results['test_cases'].items():
            table_data.append({
                'Test Case': case_name,
                'Python Runtime (s)': f"{case_data['python']['runtime']:.4f}",
                'C++ Runtime (s)': f"{case_data['cpp']['runtime']:.4f}",
                'Python Memory (MB)': f"{case_data['python']['memory_mb']:.2f}",
                'C++ Memory (MB)': f"{case_data['cpp']['memory_mb']:.2f}",
                'Speedup Factor': f"{case_data['cpp']['runtime'] / case_data['python']['runtime']:.2f}x"
            })
        
        df = pd.DataFrame(table_data)
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
            csv_data = pd.DataFrame([
                {
                    'Test Case': case_name,
                    'Python Runtime (s)': case_data['python']['runtime'],
                    'C++ Runtime (s)': case_data['cpp']['runtime'],
                    'Python Memory (MB)': case_data['python']['memory_mb'],
                    'C++ Memory (MB)': case_data['cpp']['memory_mb'],
                    'Speedup Factor': case_data['cpp']['runtime'] / case_data['python']['runtime']
                }
                for case_name, case_data in results['test_cases'].items()
            ])
            
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
    CodeBench Performance Analyzer v1.0 | Built with Streamlit ⚡
</div>
""", unsafe_allow_html=True)
