# src/financial_data/processors/data_fetcher.py

import logging
from typing import Dict, List, Optional

from financial_data.clients.fmp_client import FMPClient, FMPError
from financial_data.clients.yahoo_client import YahooFinanceClient

logger = logging.getLogger(__name__)

class DataFetcher:
    """Fetches financial data from FMP and Yahoo Finance APIs."""

    def __init__(self, fmp_client: FMPClient, yahoo_client: YahooFinanceClient):
        self.fmp_client = fmp_client
        self.yahoo_client = yahoo_client
        logger.debug("DataFetcher initialized.")

    def fetch_all_data(self, symbol: str) -> Dict:
        """Fetches all necessary data for the given symbol."""
        try:
            profile = self.fmp_client.get_company_profile(symbol)
            fiscal_year_end = self.fmp_client.get_fiscal_year_end(symbol)
            income_statements = self.fmp_client.get_income_statement(symbol, period="annual")
            balance_sheets = self.fmp_client.get_balance_sheet(symbol, period="annual")
            cash_flows = self.fmp_client.get_cash_flow_statement(symbol, period="annual")
            key_metrics = self.fmp_client.get_key_metrics(symbol)
            revenue_segmentation = self.fmp_client.get_revenue_segmentation(symbol)
            current_stock_price = self.fmp_client.get_quote_short(symbol) or 0.0

            data = {
                "profile": profile,
                "fiscal_year_end": fiscal_year_end,
                "income_statements": income_statements,
                "balance_sheets": balance_sheets,
                "cash_flows": cash_flows,
                "key_metrics": key_metrics,
                "revenue_segmentation": revenue_segmentation,
                "current_stock_price": current_stock_price
            }
            logger.info(f"All data fetched for symbol: {symbol}")
            return data

        except FMPError as e:
            logger.error(f"Failed to fetch data for {symbol}: {e}")
            raise
