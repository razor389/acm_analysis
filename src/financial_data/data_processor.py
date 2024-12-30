# src/financial_data/data_processor.py

import os
import json
from typing import Dict, List, Optional
from .models import YearMetrics
from ..utils.calculations import calculate_cagr
from .yahoo_client import YahooFinanceClient

class FinancialDataProcessor:
    """Process financial data from FMP + Yahoo + any other sources."""
    
    def __init__(self, fmp_client, yahoo_client: YahooFinanceClient, output_dir="output"):
        self.fmp_client = fmp_client
        self.yahoo_client = yahoo_client
        self.output_dir = output_dir
    
    def process_company_data(self, symbol: str, start_year: int, end_year: int) -> Dict:
        """End-to-end data fetching & processing, replicating old 'acm_analysis.py' logic."""
        # 1) Fetch the profile
        profile = self.fmp_client.get_company_profile(symbol)

        # 2) Fetch statements
        statements = self._fetch_financial_statements(symbol)

        # 3) Fetch revenue segmentation
        revenue_seg = self.fmp_client.get_revenue_segmentation(symbol)

        # 4) Process YOY data
        years_range = range(start_year, end_year + 1)
        yoy_data = self._process_yoy_data(statements, revenue_seg, years_range)

        # 5) Compute characteristics
        investment_chars = self._compute_investment_characteristics(yoy_data)
        bs_chars = self._compute_balance_sheet_characteristics(yoy_data)
        profit_chars = self._compute_profit_characteristics(yoy_data)

        # 6) Possibly fetch short quote
        short_quote = self._get_short_quote(symbol)
        
        # 7) Build final dict
        final_output = {
            "symbol": profile.symbol or symbol,
            "company_name": profile.company_name,
            "exchange": profile.exchange,
            "description": profile.description,
            "marketCapitalization": profile.market_cap,
            "sector": profile.sector,
            "subsector": profile.subsector,
            "investment_characteristics": investment_chars,
            "balance_sheet_characteristics": bs_chars,
            "profit_description_characteristics": profit_chars,
            "data": yoy_data
        }
        
        # 8) Save to a JSON file if desired
        out_file = os.path.join(self.output_dir, f"{symbol}_yoy_consolidated.json")
        with open(out_file, "w") as f:
            json.dump(final_output, f, indent=4)
        print(f"Consolidated YOY data saved to '{out_file}'")

        return final_output

    def _fetch_financial_statements(self, symbol: str) -> Dict:
        """Fetch annual income, balance, and cash flow statements from FMP."""
        income = self.fmp_client.get_financial_statements(symbol, "income-statement", "annual")
        balance = self.fmp_client.get_financial_statements(symbol, "balance-sheet-statement", "annual")
        cash_flow = self.fmp_client.get_financial_statements(symbol, "cash-flow-statement", "annual")
        return {"income": income, "balance": balance, "cash_flow": cash_flow}

    def _process_yoy_data(self, statements: Dict, revenue_seg: Dict, years: range) -> Dict:
        """Loop over the specified years, pulling out relevant metrics each year."""
        yoy_result = {}
        prev_shares = None
        for y in years:
            yoy_result[y] = self._calculate_year_metrics(y, statements, revenue_seg.get(y, {}), prev_shares)
            prev_shares = yoy_result[y].get("shares_outstanding")
        return yoy_result

    def _calculate_year_metrics(
        self, year: int, statements: Dict, rev_breakdown: Dict, prev_shares: Optional[float]
    ) -> Dict:
        """Pull from the raw statements data for a given year, returning a dict of metrics."""
        # This logic was previously in your 'extract_yoy_data' portion of acm_analysis.py
        # 1) Find the statement item for that year
        #    statements["income"] is a list of dicts from FMP
        #    We find the dict whose 'date' starts with f"{year}-"
        #    Do similarly for balance, cash_flow, etc.

        inc = self._find_statement_for_year(statements["income"], year)
        bal = self._find_statement_for_year(statements["balance"], year)
        cf  = self._find_statement_for_year(statements["cash_flow"], year)

        # 2) Extract relevant fields
        # net_income, revenue, shares_outstanding, etc.
        if not inc:
            return {}
        net_income = inc.get("netIncome")
        revenue = inc.get("revenue")
        shares_out = inc.get("weightedAverageShsOut", 0)
        cost_of_revenue = inc.get("costOfRevenue", 0)

        # many more lines follow, replicating your original logic:
        # - ebit, capex, free cash flow, eps, etc.
        # - find from bal and cf as well

        # 3) Possibly get yearly high/low from Yahoo
        year_high, year_low = self.yahoo_client.get_yearly_high_low(inc.get("symbol", ""), year)
        average_price = None
        if year_high and year_low:
            average_price = (year_high + year_low)/2

        # 4) Return a dict
        metrics = {
            "net_profit": net_income,
            "revenues": revenue,
            "shares_outstanding": shares_out,
            "price_high": year_high,
            "price_low": year_low,
            "average_price": average_price,
            # plus many more
        }
        return metrics

    def _find_statement_for_year(self, statements: List[Dict], year: int) -> Optional[Dict]:
        """Helper to get the statement dict for the specified year."""
        for st in statements:
            date_str = st.get("date", "")
            if date_str.startswith(str(year)):
                return st
        return None

    def _compute_investment_characteristics(self, yoy_data: Dict) -> Dict:
        # replicate your existing logic for "investment_characteristics"
        pass

    def _compute_balance_sheet_characteristics(self, yoy_data: Dict) -> Dict:
        # replicate logic for cagr_total_assets, etc.
        pass

    def _compute_profit_characteristics(self, yoy_data: Dict) -> Dict:
        # replicate logic for cagr_revenues_percent, cagr_ebitda_percent, etc.
        pass

    def _get_short_quote(self, symbol: str) -> Optional[float]:
        """Fetch the short quote from FMP (like get_quote_short in old code)."""
        # or you can do self.fmp_client.get_quote_short(...)
        return None
