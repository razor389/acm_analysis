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

# requirements.txt
yfinance==0.2.36
pandas==2.1.4
openpyxl==3.1.2
python-dotenv==1.0.0
requests==2.31.0
openai==1.3.7
beautifulsoup4==4.12.2
pyyaml==6.0.1