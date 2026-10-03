
"""setup.py for erdos-proof-atlas"""
from setuptools import setup, find_packages

setup(
    name="erdos-proof-atlas",
    version="0.1.0",
    description="Erdos Proof Atlas: Computational Discovery, Exact Certification, and Lean-Checked Mathematics",
    author="Scott Sun",
    author_email="contact@pq-research.org",
    url="https://github.com/suns1232023/erdos-proof-atlas",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "numpy>=1.24",
        "scipy>=1.10",
        "pyyaml>=6.0",
    ],
    extras_require={
        "symbolic": ["sympy>=1.12", "mpmath>=1.3"],
        "dev": ["pytest>=7.4", "pytest-timeout>=2.1", "ruff>=0.1"],
    },
)
