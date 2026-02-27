from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme = Path("README.md").read_text(encoding="utf-8")

setup(
    name="observational-memory",
    version="2.0.0",
    author="OpenClaw Community",
    author_email="",
    description="Mastra-inspired memory system for AI agents",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/kiss-kedaya/openclaw-observational-memory",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        
        
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "sentence-transformers>=5.0.0",
        "torch>=1.11.0",
        "numpy>=1.20.0",
        "streamlit>=1.54.0",
        "plotly>=6.5.0",
        "streamlit-option-menu>=0.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "api": [
            "fastapi>=0.129.0",
            "uvicorn>=0.41.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "observational-memory=observational_memory.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "observational_memory": ["../web/locales/*.json"],
    },
)
