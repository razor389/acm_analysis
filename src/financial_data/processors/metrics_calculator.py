# src/financial_data/processors/metrics_calculator.py

import logging
from typing import Dict, List, Tuple, Optional

from financial_data.models import FinancialData
from utils.calculations import calculate_cagr

logger = logging.getLogger(__name__)

class MetricsCalculator:
    """Calculates financial metrics based on transformed data."""

    def __init__(self):
        logger.debug("MetricsCalculator initialized.")

    def compute_cagr(self, values_by_year: List[Tuple[int, float]]) -> Optional[float]:
        """Calculates CAGR for given values."""
        return calculate_cagr(values_by_year) * 100 if values_by_year else None

    def compute_earnings_analysis(self, yoy_data: Dict[int, FinancialData]) -> Dict:
        """Computes earnings analysis metrics."""
        earnings_analysis = {}

        # CAGR of Operating EPS
        ops_eps_pairs = [(year, data.operating_eps) for year, data in yoy_data.items() if data.operating_eps]
        earnings_analysis["growth_rate_percent_operating_eps"] = self.compute_cagr(sorted(ops_eps_pairs)) if len(ops_eps_pairs) >= 2 else None

        # Quality Percent
        diluted_eps_values = [data.diluted_eps for data in yoy_data.values() if data.diluted_eps]
        operating_eps_values = [data.operating_eps for data in yoy_data.values() if data.operating_eps]
        if diluted_eps_values and operating_eps_values:
            avg_diluted_eps = sum(diluted_eps_values) / len(diluted_eps_values)
            avg_operating_eps = sum(operating_eps_values) / len(operating_eps_values)
            earnings_analysis["quality_percent"] = round((avg_diluted_eps / avg_operating_eps) * 100, 2) if avg_operating_eps else None

        return earnings_analysis

    def compute_use_of_earnings_analysis(self, yoy_data: Dict[int, FinancialData]) -> Dict:
        """Computes use of earnings analysis metrics."""
        use_of_earnings = {}

        # Avg Dividend Payout %
        dividend_payouts = [
            (data.dividends_per_share / data.operating_eps) * 100
            for data in yoy_data.values()
            if data.dividends_per_share and data.operating_eps
        ]
        if dividend_payouts:
            use_of_earnings["avg_dividend_payout_percent"] = round(sum(dividend_payouts) / len(dividend_payouts), 2)

        # Avg Stock Buyback %
        buybacks = [data.buyback for data in yoy_data.values() if data.buyback]
        net_profits = [data.net_profit for data in yoy_data.values() if data.net_profit]
        if buybacks and net_profits:
            total_buyback = sum(buybacks)
            total_net_profit = sum(net_profits)
            use_of_earnings["avg_stock_buyback_percent"] = round((total_buyback / total_net_profit) * 100, 2) if total_net_profit else None

        return use_of_earnings

    def compute_sales_analysis(self, yoy_data: Dict[int, FinancialData]) -> Dict:
        """Computes sales analysis metrics."""
        sales_analysis = {}

        # CAGR of Revenues
        rev_pairs = [(year, data.revenues) for year, data in yoy_data.items() if data.revenues]
        sales_analysis["growth_rate_percent_revenues"] = self.compute_cagr(sorted(rev_pairs)) if len(rev_pairs) >= 2 else None

        # CAGR of Sales per Share
        sps_pairs = [(year, data.sales_per_share) for year, data in yoy_data.items() if data.sales_per_share]
        sales_analysis["growth_rate_percent_sales_per_share"] = self.compute_cagr(sorted(sps_pairs)) if len(sps_pairs) >= 2 else None

        return sales_analysis

    def compute_sales_analysis_last_5_years(self, yoy_data: Dict[int, FinancialData]) -> Dict:
        """Computes sales analysis metrics for the last 5 years."""
        sales_analysis_5y = {}

        sorted_years = sorted(yoy_data.keys())
        last_5_years = sorted_years[-5:]

        # CAGR of Revenues for last 5 years
        rev_pairs_5y = [(year, yoy_data[year].revenues) for year in last_5_years if yoy_data[year].revenues]
        sales_analysis_5y["growth_rate_percent_revenues"] = self.compute_cagr(sorted(rev_pairs_5y)) if len(rev_pairs_5y) >= 2 else None

        # CAGR of Sales per Share for last 5 years
        sps_pairs_5y = [(year, yoy_data[year].sales_per_share) for year in last_5_years if yoy_data[year].sales_per_share]
        sales_analysis_5y["growth_rate_percent_sales_per_share"] = self.compute_cagr(sorted(sps_pairs_5y)) if len(sps_pairs_5y) >= 2 else None

        return sales_analysis_5y

    def compute_revenue_breakdown_cagr(self, revenue_segmentation: Dict[int, Dict[str, float]]) -> Dict[str, Optional[float]]:
        """Computes CAGR for each revenue segment."""
        revenues_breakdown_cagr = {}
        # Identify all unique revenue segments
        segments = set()
        for segments_dict in revenue_segmentation.values():
            segments.update(segments_dict.keys())

        for segment in segments:
            segment_values = [(year, segments_dict.get(segment)) for year, segments_dict in revenue_segmentation.items() if segments_dict.get(segment)]
            segment_values = sorted(segment_values)
            if len(segment_values) >= 2:
                cagr = calculate_cagr(segment_values) * 100
                revenues_breakdown_cagr[f"cagr_revenues_{segment}_percent"] = round(cagr, 2)
            else:
                revenues_breakdown_cagr[f"cagr_revenues_{segment}_percent"] = None

        return revenues_breakdown_cagr

    # Implement additional methods for other metrics as needed
