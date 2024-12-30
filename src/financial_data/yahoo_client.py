# src/financial_data/yahoo_client.py
import yfinance as yf
from typing import Tuple, Optional
from datetime import datetime

class YahooFinanceClient:
    """Client for Yahoo Finance data."""
    
    @staticmethod
    def get_yearly_high_low(symbol: str, year: int) -> Tuple[Optional[float], Optional[float]]:
        """Get yearly high and low prices."""
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        
        try:
            df = yf.download(symbol, start=start_date, end=end_date, progress=False)
            if df.empty:
                return None, None
                
            yearly_high = df['High'].max()
            yearly_low = df['Low'].min()
            
            return (
                yearly_high.item() if yearly_high is not None else None,
                yearly_low.item() if yearly_low is not None else None
            )
        except Exception as e:
            print(f"Error fetching Yahoo Finance data: {e}")
            return None, None