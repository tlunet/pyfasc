# 📦 Installation Guide

## Quick Start (Development Mode)

After the refactoring, you need to install the package to use it properly.

### 1. Install in Development Mode (Recommended)

From the `01_advDiffSolver` directory:

```bash
pip install -e .
```

**What this does:**
- Installs the package in "editable" mode
- Changes to code are immediately reflected (no reinstall needed)
- Creates clean imports: `from adapters import LanguageAdapter`
- Removes need for `sys.path` manipulation

### 2. Verify Installation

```bash
# Test the import
python -c "from adapters import LanguageRegistry; print('✅ Installation successful!')"

# Test the command-line tool
codebench --help
```

### 3. Run the Benchmark Tool

```bash
# From anywhere after installation:
codebench --py program.py --cpp program.cpp --config config.txt

# Or use the module directly:
python -m tests.diagnosetool --py program.py --cpp program.cpp --config config.txt
```

### 4. Run the Streamlit App

```bash
streamlit run app.py
```

## Alternative: Regular Installation

If you don't need to edit the code:

```bash
pip install .
```

## Uninstall

```bash
pip uninstall codebench-analyzer
```

## Installation with Development Tools

For development work (testing, linting, formatting):

```bash
pip install -e .[dev]
```

This installs additional tools:
- pytest (testing)
- black (code formatting)
- flake8 (linting)
- mypy (type checking)

## Troubleshooting

### Import Error: "No module named 'adapters'"

**Solution:** Install the package first:
```bash
pip install -e .
```

### ModuleNotFoundError: setuptools

**Solution:** Install setuptools:
```bash
pip install setuptools wheel
```

### Permission Denied

**Solution:** Use a virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install
pip install -e .
```

## What Changed?

### Before (Local Package):
```python
# Had to manipulate sys.path
import sys
sys.path.insert(0, os.path.dirname(__file__))
from adapters import LanguageAdapter  # ⚠️ Fragile
```

### After (Installed Package):
```python
# Clean import, works everywhere
from adapters import LanguageAdapter  # ✅ Professional
```

## For Your Bachelorarbeit

Add this to your documentation:

```
## Installation

1. Clone the repository
2. Navigate to the project directory
3. Install in development mode:
   ```
   pip install -e .
   ```
4. Run the application:
   ```
   streamlit run app.py
   ```
```

## Virtual Environment (Recommended)

Create an isolated environment for the project:

```bash
# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -e .

# When done, deactivate
deactivate
```

## Package Structure

After installation, the package structure is:

```
site-packages/
└── codebench_analyzer-2.0.0-py3.X.egg-link  # Points to your source
    └── (your source code in 01_advDiffSolver/)
```

## Benefits of This Setup

✅ **Clean Imports** - No more `sys.path` hacks
✅ **Professional** - Standard Python package structure
✅ **Reusable** - Can be used in other projects
✅ **Testable** - Easy to write tests
✅ **Documentable** - Standard documentation tools work
✅ **Distributable** - Can be shared via PyPI

## Next Steps

1. ✅ Install the package: `pip install -e .`
2. ✅ Test imports: `python -c "from adapters import LanguageRegistry"`
3. ✅ Run tests: `python tests/diagnosetool.py --help`
4. ✅ Run app: `streamlit run app.py`

---

**Note**: The `-e` flag (editable mode) means you can edit the code and see changes immediately without reinstalling. Perfect for development!
