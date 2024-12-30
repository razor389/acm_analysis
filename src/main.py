# src/main.py
import sys
import os
import logging

from .utils.config import Config
from .financial_data.fmp_client import FMPClient
from .financial_data.yahoo_client import YahooFinanceClient
from .financial_data.data_processor import FinancialDataProcessor
from .summary.post_fetcher import fetch_all_posts_for_ticker
from .summary.summarizer import summarize_ticker_posts
from .excel.generator import generate_excel_for_ticker_year

def main():
    # 1) Configure logging globally
    logging.basicConfig(
        level=logging.DEBUG,  # or logging.INFO if you want fewer details
        format='%(asctime)s %(levelname)s [%(name)s] %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    if len(sys.argv) < 3:
        logger.error("Usage: acm-analysis SYMBOL START_YEAR")
        sys.exit(1)

    symbol = sys.argv[1].upper()
    start_year = int(sys.argv[2])

    # 2) Load config
    config = Config()

    # 3) Set up FMP client, Yahoo client, processor
    fmp_api_key = config["fmp_api_key"]
    fmp_base_url = config["api"]["fmp_base_url"]
    fmp_client = FMPClient(api_key=fmp_api_key, base_url=fmp_base_url)

    yahoo_client = YahooFinanceClient()
    processor = FinancialDataProcessor(fmp_client, yahoo_client, output_dir="output")

    # 4) Derive end_year
    fiscal_year_end = fmp_client.get_company_profile(symbol).fiscal_year_end
    if not fiscal_year_end:
        end_year = start_year
    else:
        end_year = max(start_year, 2023)  # example logic

    if start_year > end_year:
        logger.error("START_YEAR cannot be greater than END_YEAR.")
        sys.exit(1)

    # 5) Fetch forum posts
    wtb_api_key = config["websitetoolbox_api_key"]
    fetch_all_posts_for_ticker(symbol, output_dir="output", api_key=wtb_api_key)

    # 6) Summarize the forum posts
    forum_summary = summarize_ticker_posts(symbol, output_dir="output", api_key=config["openai_api_key"])

    # 7) Process the financial data
    final_output = processor.process_company_data(symbol, start_year, end_year)

    # 8) Insert the forum_summary into final_output (like "qualities")
    final_output["qualities"] = forum_summary

    # 9) Save updated final_output
    yoy_path = os.path.join("output", f"{symbol}_yoy_consolidated.json")
    with open(yoy_path, "w") as f:
        import json
        json.dump(final_output, f, indent=4)
    logger.info(f"Updated final output with forum summary in {yoy_path}")

    # 10) Generate Excel
    try:
        generate_excel_for_ticker_year(symbol, end_year)
    except Exception as e:
        logger.exception(f"Error generating Excel: {e}")
