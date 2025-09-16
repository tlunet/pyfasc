"""
Setup configuration for the CodeBench Performance Analyzer

This makes the 'adapters' package installable, allowing clean imports
throughout the project without sys.path manipulation.

Installation:
    pip install -e .    # Development mode (editable)
    pip install .       # Regular installation

Usage after installation:
    from adapters import LanguageAdapter, LanguageRegistry
    from adapters.registry import get_registry
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "CodeBench - General Purpose Performance Analyzer"

# Read requirements from requirements.txt
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="codebench-analyzer",
    version="2.0.0",
    author="Your Name",  # Update with your name
    author_email="your.email@example.com",  # Update with your email
    description="A flexible benchmarking tool for comparing programming language performance",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/tlunet/pyfasc",  # Update if different
    
    # Package discovery
    packages=find_packages(exclude=['tests*', 'docs*', 'examples*']),
    
    # Python version requirement
    python_requires='>=3.7',
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Optional dependencies
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'mypy>=0.950',
        ],
        'docs': [
            'sphinx>=4.0.0',
            'sphinx-rtd-theme>=1.0.0',
        ],
    },
    
    # Entry points for command-line tools
    entry_points={
        'console_scripts': [
            'codebench=tests.diagnosetool:main',
        ],
    },
    
    # Package data to include
    package_data={
        'adapters': ['*.yaml', '*.yml'],
        'config': ['*.yaml', '*.yml', '*.txt'],
    },
    
    # Classifiers for PyPI
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Testing',
        'Topic :: System :: Benchmark',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    
    # Keywords for discoverability
    keywords='benchmark performance python cpp julia rust go testing',
    
    # Include package data
    include_package_data=True,
    
    # Zip safety
    zip_safe=False,
)
