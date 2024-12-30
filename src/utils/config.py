# src/utils/config.py
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

class Config:
    def __init__(self, config_path: str = None):
        load_dotenv(dotenv_path=Path(__file__).parents[2] / ".env")  
        self.config = self._load_config(config_path)
        self._validate_config()

    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration from file and environment variables."""
        # Default configuration
        config = {
            "fmp_api_key": os.getenv("FMP_API_KEY"),
            "websitetoolbox_api_key": os.getenv("WEBSITETOOLBOX_API_KEY"),
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "output_dir": "output",
            "api": {
                "fmp_base_url": "https://financialmodelingprep.com/api/v3",
                "websitetoolbox_base_url": "https://api.websitetoolbox.com/v1/api"
            }
        }

        # Override with file configuration if provided
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    config.update(file_config)

        return config

    def _validate_config(self):
        """Validate required configuration values."""
        required_keys = ["fmp_api_key", "websitetoolbox_api_key", "openai_api_key"]
        missing_keys = [key for key in required_keys if not self.config.get(key)]
        
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {', '.join(missing_keys)}")

    def __getitem__(self, key: str) -> Any:
        return self.config[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

# config/default_config.yml
default_config = """
# API Keys (override with environment variables)
fmp_api_key: ""
websitetoolbox_api_key: ""
openai_api_key: ""

# Output Configuration
output_dir: "output"

# API Configuration
api:
  fmp_base_url: "https://financialmodelingprep.com/api/v3"
  websitetoolbox_base_url: "https://api.websitetoolbox.com/v1/api"

# Excel Configuration
excel:
  fonts:
    title: 
      name: "Times New Roman"
      size: 14
      bold: true
      italic: true
    label:
      name: "Times New Roman"
      size: 10
      bold: true
      italic: true
    data:
      name: "Times New Roman"
      size: 10
"""

def create_default_config():
    """Create default configuration file if it doesn't exist."""
    config_dir = Path(__file__).parent.parent.parent.parent / 'config'
    config_file = config_dir / 'default_config.yml'
    
    if not config_dir.exists():
        config_dir.mkdir(parents=True)
        
    if not config_file.exists():
        with open(config_file, 'w') as f:
            f.write(default_config)