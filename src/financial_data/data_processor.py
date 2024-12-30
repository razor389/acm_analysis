# src/financial_data/data_processor.py
from typing import Dict, List, Optional
from .models import YearMetrics
from ..utils.calculations import calculate_cagr

class FinancialDataProcessor:
    """Process financial data from various sources."""
    
    def __init__(self, fmp_client, yahoo_client):
        self.fmp_client = fmp_client
        self.yahoo_client = yahoo_client
    
    def process_company_data(self, symbol: str, start_year: int, end_year: int) -> Dict:
        """Process all company financial data."""
        # Fetch required data
        profile = self.fmp_client.get_company_profile(symbol)
        statements = self._fetch_financial_statements(symbol)
        revenue_seg = self.fmp_client.get_revenue_segmentation(symbol)
        
        # Process year-over-year data
        yoy_data = self._process_yoy_data(statements, revenue_seg, range(start_year, end_year + 1))
        
        # Calculate characteristics
        investment_chars = self._compute_investment_characteristics(yoy_data)
        balance_sheet_chars = self._compute_balance_sheet_characteristics(yoy_data)
        profit_chars = self._compute_profit_characteristics(yoy_data)
        
        return {
            "summary": {
                "symbol": profile.symbol,
                "company_name": profile.company_name,
                "exchange": profile.exchange,
                "description": profile.description,
                "sector": profile.sector,
                "subsector": profile.subsector
            },
            "data": yoy_data,
            "characteristics": {
                "investment": investment_chars,
                "balance_sheet": balance_sheet_chars,
                "profit_description": profit_chars
            }
        }

    def _fetch_financial_statements(self, symbol: str) -> Dict:
        """Fetch all required financial statements."""
        return {
            "income": self.fmp_client.get_financial_statements(symbol, "income-statement"),
            "balance": self.fmp_client.get_financial_statements(symbol, "balance-sheet-statement"),
            "cash_flow": self.fmp_client.get_financial_statements(symbol, "cash-flow-statement")
        }

    def _process_yoy_data(self, statements: Dict, revenue_seg: Dict, years: range) -> Dict:
        """Process year-over-year financial data."""
        results = {}
        prev_shares = None
        
        for year in years:
            metrics = self._calculate_year_metrics(
                year,
                statements,
                revenue_seg.get(year, {}),
                prev_shares
            )
            results[year] = metrics
            prev_shares = metrics.get("shares_outstanding")
            
        return results

    def _calculate_year_metrics(self, year: int, statements: Dict, 
                              revenue_seg: Dict, prev_shares: Optional[float]) -> Dict:
        """Calculate financial metrics for a specific year."""
        # Implementation remains similar to original code but more structured
        # This would contain the detailed metric calculations from the original code
        pass

    def _compute_investment_characteristics(self, yoy_data: Dict) -> Dict:
        """Compute investment characteristics."""
        # Implementation similar to original compute_investment_characteristics
        pass

    def _compute_balance_sheet_characteristics(self, yoy_data: Dict) -> Dict:
        """Compute balance sheet characteristics."""
        # Implementation similar to original compute_balance_sheet_characteristics
        pass

    def _compute_profit_characteristics(self, yoy_data: Dict) -> Dict:
        """Compute profit description characteristics."""
        # Implementation similar to original compute_profit_description_characteristics
        pass