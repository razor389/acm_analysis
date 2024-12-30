# test_financial_data.py

import sys
import os
import logging
from pathlib import Path
import json

# 1) Add `src` to Python path
current_dir = Path(__file__).resolve().parent
src_dir = current_dir / "src"
sys.path.append(str(src_dir))

# 2) Imports from your src
from utils.config import Config
from financial_data.clients.fmp_client import FMPClient
from financial_data.clients.yahoo_client import YahooFinanceClient
from financial_data.data_processor import FinancialDataProcessor
from financial_data.models import CompanyProfile  # Ensure this import is present

def main():
    # 3) Configure logging
    logging.basicConfig(
        level=logging.INFO,  # Set to DEBUG for more detailed logs
        format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)

    # 4) Parse command-line arguments
    if len(sys.argv) != 3:
        logger.error("Usage: python test_financial_data.py <TICKER> <START_YEAR>")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    try:
        start_year = int(sys.argv[2])
    except ValueError:
        logger.error("START_YEAR must be an integer.")
        sys.exit(1)
    
    # 5) Load config (.env, etc.)
    try:
        config = Config()
        fmp_api_key = config["fmp_api_key"]
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)
    
    # 6) Instantiate Processor
    try:
        processor = FinancialDataProcessor(api_key=fmp_api_key, output_dir="output")
    except Exception as e:
        logger.error(f"Failed to instantiate clients or processor: {e}")
        sys.exit(1)
    
    # 7) Execute Data Processing
    try:
        logger.info(f"Processing financial data for {symbol} starting from {start_year}...")
        processor.process_company_data(symbol, start_year)
    except Exception as e:
        logger.error(f"Data processing failed: {e}")
        sys.exit(1)
    
    # 8) Confirm JSON Output
    output_file = os.path.join("output", f"{symbol}_yoy_consolidated.json")
    if os.path.exists(output_file):
        logger.info(f"JSON output successfully saved to '{output_file}'.")
    else:
        logger.error(f"JSON output file '{output_file}' was not created.")
        sys.exit(1)

if __name__ == "__main__":
    main()
