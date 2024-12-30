# test_financial_data.py

import sys
import os
import logging
from pathlib import Path
import json

# 1) Add `src` to Python path
sys.path.append(str(Path(__file__).resolve().parent / "src"))

# 2) Imports from your src
from src.utils.config import Config
from src.financial_data.fmp_client import FMPClient
from src.financial_data.yahoo_client import YahooFinanceClient
from src.financial_data.data_processor import FinancialDataProcessor

# Import the final transform function
from src.financial_data.transformer import transform_final_output

def main():
    # 3) Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s [%(name)s] %(message)s'
    )
    logger = logging.getLogger(__name__)

    # 4) Parse command-line arguments
    if len(sys.argv) < 3:
        logger.error("Usage: python test_financial_data.py SYMBOL START_YEAR")
        sys.exit(1)
    symbol = sys.argv[1].upper()
    start_year = int(sys.argv[2])

    # 5) Load config (.env, etc.)
    config = Config()
    fmp_api_key = config["fmp_api_key"]
    fmp_base_url = config["api"]["fmp_base_url"]

    # 6) Instantiate FMP + Yahoo + Processor
    fmp_client = FMPClient(api_key=fmp_api_key, base_url=fmp_base_url)
    yahoo_client = YahooFinanceClient()
    processor = FinancialDataProcessor(fmp_client, yahoo_client, output_dir="output")

    # 7) Decide an end_year. 
    end_year = start_year + 1

    logger.info(f"Processing financial data for {symbol} from {start_year} to {end_year}...")

    # ---------------------------------------------------------------------
    # 8) Fetch necessary data
    # ---------------------------------------------------------------------

    # 8a) Fetch revenue segmentation 
    logger.debug("Fetching revenue segmentation for breakdown")
    rev_seg = fmp_client.get_revenue_segmentation(symbol)
    if not rev_seg:
        logger.warning(f"No revenue segmentation data found for {symbol}.")

    # 8b) Fetch the company profile
    logger.debug("Fetching company profile (name, exchange, etc.)")
    profile_data = fmp_client.get_company_profile(symbol)
    if not profile_data:
        logger.error(f"No company profile data found for {symbol}.")
        sys.exit(1)

    # 8c) Build YOY data using DataProcessor's internal method
    raw_output = processor.process_company_data(symbol, start_year, end_year)

    # 8d) Ensure revenue segmentation is integrated
    yoy_data = raw_output.get("data", {})
    if rev_seg:
        for y in yoy_data:
            year_int = int(y)
            if year_int in rev_seg:
                if "profit_description" in yoy_data[y] and "revenues" in yoy_data[y]["profit_description"]:
                    yoy_data[y]["profit_description"]["revenues"]["breakdown"] = rev_seg[year_int]
                else:
                    logger.warning(f"Missing 'profit_description' or 'revenues' in YOY data for year {y}.")
            else:
                logger.warning(f"No revenue segmentation data for year {y}.")
    else:
        logger.warning("Revenue segmentation data is empty. Skipping revenue breakdown integration.")

    # 8e) Overwrite raw_output["data"] with our updated yoy_data
    raw_output["data"] = yoy_data

    # ---------------------------------------------------------------------
    # 9) Populate header fields from the company profile
    # ---------------------------------------------------------------------

    # Check if profile_data is a list and has at least one item
    if isinstance(profile_data, list) and len(profile_data) > 0:
        profile = profile_data[0]  # Assuming the first item is the desired profile
        raw_output["symbol"] = getattr(profile, "symbol", symbol)
        raw_output["company_name"] = getattr(profile, "companyName", "N/A")
        raw_output["exchange"] = getattr(profile, "exchange", "N/A")
        raw_output["description"] = getattr(profile, "description", "N/A")
        raw_output["marketCapitalization"] = getattr(profile, "mktCap", "N/A")
        raw_output["sector"] = getattr(profile, "sector", "N/A")
        raw_output["subsector"] = getattr(profile, "industry", "N/A")
    else:
        logger.error("Company profile data is empty or not in expected format.")
        sys.exit(1)

    # ---------------------------------------------------------------------
    # 10) Transform the raw output into multi-level JSON
    # ---------------------------------------------------------------------
    final_struct = transform_final_output(raw_output, stock_price=None)

    # ---------------------------------------------------------------------
    # 11) Save final JSON to a test file
    # ---------------------------------------------------------------------
    os.makedirs("output", exist_ok=True)  # Ensure output directory exists
    out_filepath = os.path.join("output", f"{symbol}_test_consolidated.json")
    try:
        with open(out_filepath, "w", encoding="utf-8") as f:
            json.dump(final_struct, f, indent=4)
        logger.info(f"Financial data processing complete for {symbol}. Transformed data saved to {out_filepath}")
    except Exception as e:
        logger.error(f"Failed to save JSON output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
