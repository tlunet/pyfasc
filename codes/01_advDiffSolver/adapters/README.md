# Language Adapters Architecture

## 📋 Overview

The adapter architecture provides a flexible, extensible way to add support for new programming languages without modifying the core application code. This follows the **Strategy Pattern** and **Open/Closed Principle** (open for extension, closed for modification).

## 🏗️ Architecture

```
adapters/
├── __init__.py                      # Package initialization
├── base_adapter.py                  # Abstract base class (interface)
├── python_adapter.py                # Python implementation
├── cpp_adapter.py                   # C++ implementation
├── julia_adapter.py                 # Julia implementation
├── registry.py                      # Language registry and discovery
├── custom_adapters_example.py       # Examples for Rust, Go, JavaScript
└── README.md                        # This file
```

## 🚀 How to Add a New Language

Adding support for a new programming language is **incredibly simple** with this architecture:

### Step 1: Create an Adapter Class

Create a new file `your_language_adapter.py` in the `adapters/` directory:

```python
from typing import List, Tuple
from .base_adapter import LanguageAdapter

class YourLanguageAdapter(LanguageAdapter):
    def __init__(self):
        super().__init__()
        self.name = "yourlang"              # Language identifier
        self.extensions = [".ext"]          # File extensions
        self.requires_compilation = False   # True if needs compilation
        self.display_name = "Your Language" # Display name
        self.emoji = "🎯"                   # Emoji for UI
    
    def prepare(self, source_file: str) -> Tuple[bool, str, str]:
        """Prepare the program (compile if needed)"""
        # Return (success, prepared_file, error_message)
        return True, source_file, ""
    
    def get_execution_command(self, prepared_file: str) -> List[str]:
        """Get the command to run the program"""
        return ["your_interpreter", prepared_file]
    
    def cleanup(self, prepared_file: str) -> None:
        """Clean up temporary files"""
        pass  # Optional: remove compiled files
```

### Step 2: Register the Adapter

Add your adapter to `registry.py`:

```python
from .your_language_adapter import YourLanguageAdapter

def _register_builtin_adapters(self) -> None:
    builtin_adapters = [
        PythonAdapter(),
        CppAdapter(),
        JuliaAdapter(),
        YourLanguageAdapter(),  # Add your adapter here!
    ]
```

### Step 3: Use It!

That's it! No changes needed to `app.py` or `diagnosetool.py`. Your language is now supported:

```bash
python tests/diagnosetool.py --yourlang program.ext --py other.py --config input.txt
```

## 📚 Real Examples

See `custom_adapters_example.py` for complete, working examples of:
- **Rust** (compiled language with rustc)
- **JavaScript/Node.js** (interpreted language)
- **Go** (compiled language with go build)

## 🎯 Benefits of This Architecture

### 1. **Easy Extension**
- Add new language = 1 new file
- No modification of existing code
- Plug-and-play design

### 2. **Consistent Interface**
All languages work the same way:
```python
adapter = registry.get_adapter_by_file("program.rs")
success, prepared, error = adapter.prepare("program.rs")
metrics = adapter.execute(prepared, config_content)
adapter.cleanup(prepared)
```

### 3. **Type Safety**
Abstract base class ensures all adapters implement required methods.

### 4. **Testability**
Each adapter can be tested independently:
```python
def test_python_adapter():
    adapter = PythonAdapter()
    success, prepared, error = adapter.prepare("test.py")
    assert success == True
```

### 5. **Separation of Concerns**
- `base_adapter.py` → Interface definition
- `*_adapter.py` → Language-specific implementation
- `registry.py` → Discovery and management
- `app.py` / `diagnosetool.py` → Business logic (unchanged!)

## 🔧 Adapter Methods

### Required Methods

#### `prepare(source_file: str) -> Tuple[bool, str, str]`
Prepare the program for execution (compile if needed).
- **Returns:** `(success: bool, prepared_file: str, error_message: str)`
- **Example:** Compile C++ code, or just return the source file for interpreted languages

#### `get_execution_command(prepared_file: str) -> List[str]`
Get the command to execute the program.
- **Returns:** List of command arguments
- **Example:** `["python", "program.py"]` or `["./compiled_binary"]`

#### `cleanup(prepared_file: str) -> None`
Clean up temporary files created during preparation.
- **Example:** Remove compiled binaries

### Optional Methods (with default implementation)

#### `execute(prepared_file, config_content, config_files)`
Execute the program with configuration.
- **Default implementation** handles standard execution
- Override if you need custom execution logic

#### `warmup(prepared_file) -> bool`
Perform a warm-up run to cache the executable.
- **Default implementation** provided
- Useful for reducing first-run overhead

#### `detect_from_file(filename) -> bool`
Check if adapter can handle a file.
- **Default implementation** checks file extensions
- Override for custom detection logic

## 🎨 Language Registry

The `LanguageRegistry` class manages all adapters:

```python
from adapters.registry import get_registry

registry = get_registry()

# Get adapter by language name
adapter = registry.get_adapter_by_name('python')

# Get adapter by filename
adapter = registry.get_adapter_by_file('program.cpp')

# Detect language from filename
lang = registry.detect_language('script.jl')  # Returns 'julia'

# Get all supported languages
languages = registry.get_supported_languages()  # ['python', 'cpp', 'julia']

# Get all supported extensions
extensions = registry.get_supported_extensions()  # ['.py', '.cpp', '.jl', ...]
```

## 🧪 Testing Your Adapter

Create a simple test:

```python
def test_your_adapter():
    from adapters.your_language_adapter import YourLanguageAdapter
    
    adapter = YourLanguageAdapter()
    
    # Test properties
    assert adapter.name == "yourlang"
    assert ".ext" in adapter.extensions
    
    # Test file detection
    assert adapter.detect_from_file("test.ext") == True
    
    # Test preparation
    success, prepared, error = adapter.prepare("test.ext")
    assert success == True
    
    # Test execution command
    cmd = adapter.get_execution_command(prepared)
    assert len(cmd) > 0
```

## 📖 Advanced: Dynamic Registration

For plugins and external adapters:

```python
from adapters.registry import register_custom_adapter
from adapters.base_adapter import LanguageAdapter

class MyCustomAdapter(LanguageAdapter):
    # ... implementation ...
    pass

# Register at runtime
register_custom_adapter(MyCustomAdapter())
```

## 🎓 Design Patterns Used

1. **Strategy Pattern**: Each adapter encapsulates a language-specific algorithm
2. **Factory Pattern**: Registry creates appropriate adapter instances
3. **Registry Pattern**: Central registry for adapter discovery
4. **Template Method**: Base class provides common algorithm structure

## 🔍 Troubleshooting

### "Adapter not found" error
Check that your adapter is registered in `registry.py`'s `_register_builtin_adapters()` method.

### Compilation fails
Ensure the required compiler/interpreter is installed and in the system PATH.

### Import errors
Make sure `adapters/` is in Python's module search path:
```python
import sys
sys.path.insert(0, os.path.dirname(__file__))
```

## 📝 Migration Guide

### Old Code (Before Refactoring)
```python
if lang == 'python':
    cmd = ['python', file]
elif lang == 'cpp':
    compile_cpp(file)
    cmd = ['./binary']
elif lang == 'julia':
    cmd = ['julia', file]
```

### New Code (After Refactoring)
```python
adapter = registry.get_adapter_by_name(lang)
success, prepared, error = adapter.prepare(file)
cmd = adapter.get_execution_command(prepared)
```

**Result**: To add Rust, just create `rust_adapter.py`. No changes to this code needed! ✨

## 🎉 Summary

The adapter architecture makes it **trivially easy** to extend the benchmark tool:

- ✅ **One file per language** (e.g., `rust_adapter.py`)
- ✅ **No changes to core application** (`app.py`, `diagnosetool.py`)
- ✅ **Clear, documented interface** (`LanguageAdapter` base class)
- ✅ **Complete examples provided** (see `custom_adapters_example.py`)
- ✅ **Type-safe and testable**

**Adding a new language takes less than 100 lines of code!**
