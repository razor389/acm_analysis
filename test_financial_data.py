# test_financial_data.py
import sys
import os
import logging
from pathlib import Path

# Add the `src` directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent / "src"))

# Import the needed classes from your src
from src.utils.config import Config
from src.financial_data.fmp_client import FMPClient
from src.financial_data.yahoo_client import YahooFinanceClient
from src.financial_data.data_processor import FinancialDataProcessor



def main():
    # 1) Optional: configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s [%(name)s] %(message)s'
    )
    logger = logging.getLogger(__name__)

    # 2) Parse command-line arguments
    if len(sys.argv) < 3:
        logger.error("Usage: python test_financial_data.py SYMBOL START_YEAR")
        sys.exit(1)
    symbol = sys.argv[1].upper()
    start_year = int(sys.argv[2])

    # 3) Load config (this will pick up your .env)
    config = Config()

    # 4) Instantiate FMP client + Yahoo client + data processor
    fmp_api_key = config["fmp_api_key"]
    fmp_base_url = config["api"]["fmp_base_url"]
    fmp_client = FMPClient(api_key=fmp_api_key, base_url=fmp_base_url)

    yahoo_client = YahooFinanceClient()
    processor = FinancialDataProcessor(fmp_client, yahoo_client, output_dir="output")

    # 5) Decide an end_year (for a small test, maybe just use start_year + 1)
    end_year = start_year + 1

    # 6) Process the financial data
    logger.info(f"Processing financial data for {symbol} from {start_year} to {end_year}")
    final_output = processor.process_company_data(symbol, start_year, end_year)

    # 7) We're done! We do NOT fetch forum posts or call OpenAI or generate Excel.
    logger.info(f"Financial data processing complete for {symbol}. See output in /output folder.")

if __name__ == "__main__":
    main()
