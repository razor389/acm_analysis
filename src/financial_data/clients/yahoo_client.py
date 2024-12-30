# src/financial_data/yahoo_client.py

import yfinance as yf
from typing import Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class YahooFinanceClient:
    """Client for Yahoo Finance data."""

    @staticmethod
    def get_yearly_high(symbol: str, year: int) -> Optional[float]:
        """Get yearly high price."""
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"

        try:
            df = yf.download(symbol, start=start_date, end=end_date, progress=False)
            if df.empty:
                return None

            yearly_high = df['High'].max()
            return yearly_high.item() if yearly_high is not None else None
        except Exception as e:
            logging.error(f"Error fetching yearly high from Yahoo Finance: {e}")
            return None

    @staticmethod
    def get_yearly_low(symbol: str, year: int) -> Optional[float]:
        """Get yearly low price."""
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"

        try:
            df = yf.download(symbol, start=start_date, end=end_date, progress=False)
            if df.empty:
                return None

            yearly_low = df['Low'].min()
            return yearly_low.item() if yearly_low is not None else None
        except Exception as e:
            logging.error(f"Error fetching yearly low from Yahoo Finance: {e}")
            return None