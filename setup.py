# setup.py
from setuptools import setup, find_packages

setup(
    name="razor389-analysis",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "yfinance",
        "pandas",
        "openpyxl",
        "python-dotenv",
        "requests",
        "openai",
        "beautifulsoup4",
        "pyyaml"
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "acm-analysis=razor389_analysis.main:main",
        ],
    },
)

