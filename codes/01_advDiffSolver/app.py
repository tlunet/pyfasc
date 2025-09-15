import streamlit as st
import subprocess
import os
import tempfile
import json
import shutil
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import zipfile
import io

# Page configuration
st.set_page_config(
    page_title="CodeBench Performance Analyzer",
    page_icon="⚡",
    layout="wide"
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
if 'benchmark_results' not in st.session_state:
    st.session_state.benchmark_results = None

def get_powers_of_two(min_val, max_val):
    """Get all powers of 2 between min_val and max_val (inclusive)"""
    powers = []
    power = 0
    while True:
        val = 2 ** power
        if val > max_val:
            break
        if val >= min_val:
            powers.append(val)
        power += 1
    return powers

def generate_inputs_content(variable_type, start_val, end_val, num_steps, init_type="gauss", flow_type="diagonal", viscosity=0.0, end_time=1):
    """Generate inputs.txt content based on selected variable and range"""
    content_lines = []
    
    if variable_type == "Grid Size (N_x/N_y)":
        # For grid size: use all powers of 2 between start_val and end_val
        sizes = get_powers_of_two(start_val, end_val)
        
        for size in sizes:
            content_lines.append(f"{size} {size}")
            content_lines.append(init_type)
            content_lines.append(f"{flow_type} {viscosity}")
            content_lines.append(f"{end_time} 400")
            content_lines.append("")  # Empty line between test cases
            
    elif variable_type == "Time Steps":
        # For time steps: keep the old system with num_steps
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

Each program runs independently in isolated temporary directories to avoid file conflicts.
</div>
""", unsafe_allow_html=True)

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

# Configuration section
st.markdown('<div class="section-header">⚙️ Benchmark Configuration</div>', unsafe_allow_html=True)

# Variable type selection
variable_type = st.selectbox(
    "Variable to vary:",
    ["Grid Size (N_x/N_y)", "Time Steps"],
    index=0 if st.session_state.get('variable_type', 'Grid Size (N_x/N_y)') == 'Grid Size (N_x/N_y)' else 1,
    key="variable_type"
)

# Create layout based on variable type
if variable_type == "Grid Size (N_x/N_y)":
    # For Grid Size: only start and end (powers of 2)
    col1, col2, col3 = st.columns(3)
    
    # Available powers of 2 (2^0 to 2^10)
    powers_of_2 = [2**i for i in range(11)]  # [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
    
    with col1:
        start_val = st.selectbox(
            "Start size (power of 2):", 
            options=powers_of_2,
            index=powers_of_2.index(st.session_state.get('start_val', 64)) if st.session_state.get('start_val', 64) in powers_of_2 else 6,
            key="start_val"
        )
    
    with col2:
        # Filter end values to only show powers >= start_val
        available_end_values = [p for p in powers_of_2 if p >= start_val]
        default_end = st.session_state.get('end_val', 512)
        if default_end not in available_end_values:
            default_end = available_end_values[-1]
        
        end_val = st.selectbox(
            "End size (power of 2):", 
            options=available_end_values,
            index=available_end_values.index(default_end) if default_end in available_end_values else -1,
            key="end_val"
        )
    
    with col3:
        # Show preview of selected powers
        selected_powers = get_powers_of_two(start_val, end_val)
        st.info(f"Test cases: {len(selected_powers)}\nSizes: {selected_powers}")
    
    # Set num_steps to None for Grid Size (not used)
    num_steps = None

else:
    # For Time Steps: keep the original 3-column layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_val = st.number_input(
            "Start steps:", 
            min_value=1, 
            value=st.session_state.get('start_val', 100), 
            key="start_val"
        )
    
    with col2:
        end_val = st.number_input(
            "End steps:", 
            min_value=start_val, 
            value=max(start_val, st.session_state.get('end_val', 800)), 
            key="end_val"
        )
    
    with col3:
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
    variable_type, start_val, end_val, num_steps if num_steps is not None else 0, 
    init_type, flow_type, viscosity, end_time
)
st.code(preview_content, language="text")

# Benchmark execution
st.markdown('<div class="section-header">🚀 Run Benchmark</div>', unsafe_allow_html=True)

# Check if everything is ready
codes_provided = bool(st.session_state.python_code and st.session_state.cpp_code)

ready_to_run = codes_provided

if not ready_to_run:
    missing_items = []
    if not st.session_state.python_code:
        missing_items.append("Python code")
    
    if not st.session_state.cpp_code:
        missing_items.append("C++ code")
    
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
