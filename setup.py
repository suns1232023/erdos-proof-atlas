"""
setup.py for erdos-proof-atlas

REPAIR NOTE:
  Provides proper package installation with optional dependencies.
  Install with: pip install -e ".[symbolic,dev]"
"""

from setuptools import setup, find_packages

setup(
    name="erdos-proof-atlas",
    version="0.2.0",
    description="Formal verification infrastructure for Erdős-type extremal geometry problems",
    author="Scott Sun",
    author_email="contact@pq-research.org",
    url="https://github.com/suns1232023/erdos-proof-atlas",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.24",
        "scipy>=1.10",
        "matplotlib>=3.7",
    ],
    extras_require={
        "symbolic": [
            "sympy>=1.12",
            "mpmath>=1.3",
        ],
        "dev": [
            "pytest>=7.4",
            "pytest-cov>=4.1",
            "pyyaml>=6.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
