import sys
import os
import shutil
import subprocess
import platform
import tempfile
from pathlib import Path
import numpy as np


def cpp_convergence_test(base_dir, temp_dir):
    print("\n[1/3] Compiling C++ implementation...")
    cpp_file = base_dir / "src" / "program.cpp"
    binary_name = "program_cpp.exe" if platform.system() == "Windows" else "program_cpp"
    binary_path = base_dir / binary_name
    
    compiler = ["g++", str(cpp_file), "-O2", "-o", str(binary_path)]
    subprocess.run(compiler, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    nX0 = 32
    nGrids = 3
    tEnd = 0.1
    nu = 0.001
    
    print("[2/3] Running reference simulation...")
    nXRef = nX0 * 2**nGrids
    config = f"{nXRef} {nXRef} gauss diagonal {nu} {tEnd} {nXRef}\n"
    (base_dir / "input.txt").write_text(config)
    
    os.chdir(base_dir)
    exec_cmd = [str(binary_path)] if platform.system() == "Windows" else [f"./{binary_path.name}"]
    subprocess.run(exec_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    uRef = np.loadtxt(base_dir / "uEnd.txt")
    
    np.savetxt(temp_dir / f"uEnd_cpp_{nXRef}x{nXRef}.txt", uRef)
    
    print("[3/3] Computing convergence rates...")
    errors = {}
    for i in range(nGrids):
        nX = nX0 * 2**i
        config = f"{nX} {nX} gauss diagonal {nu} {tEnd} {nX}\n"
        (base_dir / "input.txt").write_text(config)
        subprocess.run(exec_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        uNum = np.loadtxt(base_dir / "uEnd.txt")
        
        np.savetxt(temp_dir / f"uEnd_cpp_{nX}x{nX}.txt", uNum)
        
        r = nXRef // nX
        diff = uRef[::r, ::r] - uNum
        errors[nX] = np.sqrt(np.mean(diff**2))
    
    conv = {}
    for i in range(nGrids-1):
        nX1 = nX0 * 2**i
        nX2 = 2 * nX1
        conv[nX2] = np.log2(errors[nX1] / errors[nX2])
    
    print("\nConvergence order:")
    for nX, order in conv.items():
        err1, err2 = errors[nX//2], errors[nX]
        print(f" -- grid {nX}: {order:.2f} ({err1:.2e} -> {err2:.2e})")
    
    passed = all(abs(order - 4) < 0.3 for order in conv.values())
    print(f"\nConvergence test: {'PASS' if passed else 'FAIL'}")
    
    binary_path.unlink()
    return nXRef, passed


def compare_with_reference(base_dir, temp_dir, nXRef, language="python"):
    print(f"\n[1/2] Running {language} implementation ({nXRef}x{nXRef})...")
    
    if language == "python":
        py_file = base_dir / "src" / "program.py"
        config = f"{nXRef} {nXRef} gauss diagonal 0.001 0.1 {nXRef}\n"
        (base_dir / "input.txt").write_text(config)
        os.chdir(base_dir)
        subprocess.run(["python", str(py_file)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        result = np.loadtxt(base_dir / "uEnd.txt")
    
    print("[2/2] Comparing with validated C++ reference...")
    reference = np.loadtxt(temp_dir / f"uEnd_cpp_{nXRef}x{nXRef}.txt")
    diff = np.abs(reference - result)
    print(f"  Max diff: {diff.max():.2e}, Mean diff: {diff.mean():.2e}")
    
    match = np.allclose(reference, result, rtol=1e-6, atol=1e-6) 
    # Keine machine precision (1e-10), da hier größere Abweichungen auftreten können durch z.B. 
    # verschiedene Methoden (sq() statt ** bei Python, oder aber Compiler-Optimierungen) 

    print(f"  Match: {'PASS' if match else 'FAIL'}")
    
    return match


def main():
    base_dir = Path(__file__).parent.parent
    
    print("="*60)
    print("CONVERGENCE-BASED VALIDATION TEST")
    print("="*60)
    
    all_tests_passed = True
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        print("\n" + "="*60)
        print("STEP 1: C++ CONVERGENCE TEST")
        print("="*60)
        
        conv_passed = cpp_convergence_test(base_dir, temp_dir)
        all_tests_passed = all_tests_passed and conv_passed
        
        print("\n" + "="*60)
        print("STEP 2: COMPARE IMPLEMENTATIONS")
        print("="*60)
        
        py_passed = compare_with_reference(base_dir, temp_dir, 128, "python")
        all_tests_passed = all_tests_passed and py_passed
        
    except Exception as e:
        print(f"\n ERROR: {e}")
        all_tests_passed = False
    finally:
        shutil.rmtree(temp_dir)
    
    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)
    print(f"All tests: {'PASS' if all_tests_passed else 'FAIL'}")
    print("="*60)
    
    return all_tests_passed


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)