# Usage Guide - CodeBench# Usage Guide



## Running the Application## Running the Application



### Start the Web Interface### Using the Web Interface (Streamlit)



```bashThe application is designed to be used exclusively through the Streamlit web interface:

streamlit run app.py

``````bash

# From the project root directory

The application will open in your browser at `http://localhost:8501`.streamlit run app.py

```

## Using CodeBench

The web interface provides:

### Step 1: Upload Files- Code editor for Python and C++ implementations

- Configuration of benchmark parameters

Upload three files through the web interface:- Automated testing and validation

- Performance comparison and visualization

1. **Python Program** (.py file)- Results export

   - Must read configuration from `config.txt`

   - Performs the computation you want to benchmark## Running Tests



2. **C++ Program** (.cpp file)Tests can be run directly from the command line for development purposes:

   - Must read configuration from `config.txt`

   - Should perform the same computation as the Python version### Grid Convergence Validation (Python)



3. **Configuration File** (any format: .txt, .json, .yaml, etc.)```bash

   - Contains parameters for your programscd tests

   - Can include multiple test cases separated by blank lines# Default: validates program.py

python validate_grid_convergence.py

### Step 2: Preview Files

# Or specify a different Python file:

Use the "Preview Uploaded Files" expander to verify your files were uploaded correctly.python validate_grid_convergence.py my_solver.py

```

### Step 3: Run Benchmark

### Grid Convergence Validation (C++)

Click the "🏃‍♂️ Run Benchmark" button. The tool will:

- Compile the C++ program```bash

- Run both programs for each configuration blockcd tests

- Measure runtimes# Default: validates program.cpp

- Generate comparison visualizationspython validate_grid_convergence_cpp.py



### Step 4: View Results# Or specify a different C++ file:

python validate_grid_convergence_cpp.py my_solver.cpp

Results include:```

- Runtime comparison chart

- Detailed results table with speedup factors### Full Validation Suite

- Download options (JSON, CSV, ZIP)

```bash

## Writing Compatible Programscd tests

python validate.py <code_file> <language>

### Python Program Example

# Examples:

```pythonpython validate.py ../src/program.py python

#!/usr/bin/env python3python validate.py ../src/my_solver.cpp cpp

```

def main():

    # Read configuration### Performance Diagnosis

    with open('config.txt', 'r') as f:

        lines = f.readlines()```bash

    cd tests

    # Parse parameters# You can now use any .py and .cpp filenames:

    param1 = int(lines[0].strip())python diagnosetool.py --py ../src/program.py --cpp ../src/program.cpp --inputs ../config/inputs.txt

    param2 = float(lines[1].strip())python diagnosetool.py --py ../src/my_solver.py --cpp ../src/my_solver.cpp --inputs ../config/inputs.txt

    ```

    # Your algorithm here

    result = compute(param1, param2)**Note:** These tests are primarily for development. The Streamlit interface includes automated validation and benchmarking.

    

    # Optional: Write output## Configuration Files

    with open('output.txt', 'w') as f:

        f.write(str(result))Configuration files are located in `config/`:



if __name__ == '__main__':- `input.txt` - Single simulation configuration

    main()- `inputs.txt` - Multiple configurations (used by diagnosetool)

```- `test_inputs.txt` - Test configurations

- `test_multi_grid.txt` - Multi-grid test configurations

### C++ Program Example

Example `input.txt` format:

```cpp

#include <iostream>```

#include <fstream>512 512           # Grid size (nX nY)

#include <string>gauss             # Initialization type

diagonal 0.0      # Flow type and viscosity

int main() {1.0 100           # End time and number of time steps

    // Read configuration```

    std::ifstream config("config.txt");

    int param1;## Output Files

    double param2;

    config >> param1 >> param2;- `results/` - Persistent results (plots, animations, metrics)

    config.close();- `outputs/` - Temporary output files (uEnd.txt, uInit.txt)

    - `gif_frames/` - Temporary frames for animation generation

    // Your algorithm here

    double result = compute(param1, param2);## Tips

    

    // Optional: Write output1. **Quick Test Run**: Use small grid sizes (32x32) for fast testing

    std::ofstream output("output.txt");2. **Production Run**: Use larger grids (512x512 or 1024x1024) for accurate results

    output << result;3. **Benchmarking**: Use powers of 2 for grid sizes (32, 64, 128, 256, 512, 1024)

    output.close();4. **Memory**: Large grids may require significant RAM

    5. **Compilation**: Use `-O2` or `-O3` optimization flags for C++ for best performance

    return 0;
}
```

### Configuration File Example

```
# Single test case
100
0.5
1000

# Or multiple test cases separated by blank lines
100
0.5

200
0.7

400
0.9
```

## Command-Line Usage

For automated benchmarking or integration into scripts:

```bash
# Navigate to tests directory
cd tests

# Run benchmark
python diagnosetool.py --py ../src/my_program.py --cpp ../src/my_program.cpp --config ../config/my_config.txt

# Results will be saved in results/ directory
```

### Command-Line Arguments

- `--py`: Path to Python program
- `--cpp`: Path to C++ program
- `--config`: Path to configuration file

### Output Files

- `results/all_metrics.json` - Complete benchmark data
- `results/runtime_comparison.png` - Visualization chart

## Tips for Best Results

### 1. Ensure Comparable Implementations

Both Python and C++ programs should:
- Use the same algorithms
- Process the same input data
- Produce equivalent results

### 2. Multiple Test Cases

Include various parameter sets to see how performance scales:
```
# Small problem
10 10

# Medium problem
100 100

# Large problem
1000 1000
```

### 3. Warm-up Runs

The tool automatically performs warm-up runs to:
- Load Python modules
- Cache C++ executable
- Ensure fair comparison

### 4. Configuration Format

Use any format that makes sense for your programs:
- **Simple**: One value per line
- **JSON**: `{"param1": 100, "param2": 0.5}`
- **CSV**: `param1,param2\n100,0.5`
- **Custom**: Whatever your programs can parse

## Troubleshooting

### "No C++ compiler found"

Install a C++ compiler:
- **Windows**: Install MinGW or Visual Studio
- **Linux/Mac**: Install g++ (`sudo apt install g++` or `brew install gcc`)

### Programs Don't Read Config

Ensure your programs:
1. Look for `config.txt` in the current directory
2. Use the correct file parsing logic
3. Handle the config format you provided

### Runtime Errors

Check that:
- Both programs handle the same input format
- All required libraries are installed
- Programs exit with return code 0 on success

## Advanced Usage

### Custom Compilation Flags

Edit `diagnosetool.py` to modify C++ compilation:
```python
compile_cmd = ["g++", cpp_file, "-O3", "-march=native", "-o", binary]
```

### Different Python Interpreters

The tool uses `sys.executable` (the Python running Streamlit). To use a different interpreter, modify `app.py`.

### Timeout Configuration

Default timeout is 10 seconds per run. Modify in `diagnosetool.py`:
```python
proc.communicate(timeout=30)  # 30 seconds
```

---

For more information, see [README.md](README.md)
