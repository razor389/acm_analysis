# src/financial_data/data_processor.py

import os
import json
import logging
from typing import Dict, List, Optional

from financial_data.clients.fmp_client import FMPClient
from financial_data.clients.yahoo_client import YahooFinanceClient
from financial_data.processors.data_fetcher import DataFetcher
from financial_data.processors.data_transformer import DataTransformer
from financial_data.processors.metrics_calculator import MetricsCalculator
from financial_data.processors.json_formatter import JSONFormatter
from financial_data.models import Metrics, FinancialData
from utils.calculations import derive_fiscal_year

logger = logging.getLogger(__name__)

class FinancialDataProcessor:
    """Orchestrates fetching, processing, and formatting of financial data."""

    def __init__(self, api_key: str, output_dir: str = "output"):
        self.fmp_client = FMPClient(api_key=api_key)
        self.yahoo_client = YahooFinanceClient()
        self.data_fetcher = DataFetcher(self.fmp_client, self.yahoo_client)
        self.data_transformer = DataTransformer()
        self.metrics_calculator = MetricsCalculator()
        self.json_formatter = JSONFormatter()
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        logger.debug(f"FinancialDataProcessor initialized with output_dir={self.output_dir}")

    def process_company_data(self, symbol: str, start_year: int) -> Metrics:
        """Processes data for a given company symbol."""
        try:
            # 1. Fetch all data
            raw_data = self.data_fetcher.fetch_all_data(symbol)

            # 2. Transform company profile
            profile = self.data_transformer.transform_company_profile(raw_data["profile"])

            # 3. Determine fiscal year end and most recent fiscal year
            fiscal_year_end = raw_data["fiscal_year_end"]
            most_recent_fiscal_year = derive_fiscal_year(fiscal_year_end)

            # 4. Extract financial statements
            income_statements = raw_data["income_statements"]
            balance_sheets = raw_data["balance_sheets"]
            cash_flows = raw_data["cash_flows"]

            # 5. Extract key metrics
            key_metrics = raw_data["key_metrics"]

            # 6. Extract revenue segmentation
            revenue_segmentation = raw_data["revenue_segmentation"]

            # 7. Get current stock price
            current_stock_price = raw_data["current_stock_price"]

            # 8. Derive end year based on fiscal year end
            end_year = most_recent_fiscal_year

            # 9. Validate start and end years
            if start_year > end_year:
                logger.error("START_YEAR cannot be greater than END_YEAR.")
                raise ValueError("START_YEAR cannot be greater than END_YEAR.")

            years_to_extract = list(range(start_year, end_year + 1))
            logger.info(f"Processing data for {symbol} from {start_year} to {end_year}")

            # 10. Process YOY financial data
            yoy_financial_data = self._process_yoy_financial_data(
                symbol, years_to_extract, income_statements, balance_sheets, cash_flows, key_metrics, revenue_segmentation
            )

            # 11. Compute investment characteristics
            investment_characteristics = self.metrics_calculator.compute_earnings_analysis(yoy_financial_data)
            use_of_earnings_analysis = self.metrics_calculator.compute_use_of_earnings_analysis(yoy_financial_data)
            sales_analysis = self.metrics_calculator.compute_sales_analysis(yoy_financial_data)
            sales_analysis_last_5_years = self.metrics_calculator.compute_sales_analysis_last_5_years(yoy_financial_data)

            # 12. Compute CAGR for revenue breakdown
            cagr_revenues_breakdown = self.metrics_calculator.compute_revenue_breakdown_cagr(revenue_segmentation)

            # 13. Compile Metrics dataclass
            metrics = Metrics(
                company_profile=profile,
                company_description=self.data_transformer.transform_company_description(
                    fiscal_year_end, current_stock_price, self._get_market_cap(key_metrics), yoy_financial_data
                ),
                analyses=None,  # Populate as needed
                profit_description=None,  # Populate as needed
                balance_sheet=None,  # Populate as needed
                studies=None  # Populate as needed
            )

            # 14. Compute additional characteristics and populate other sections
            # Implement similar transformations and computations for analyses, profit_description, balance_sheet, studies

            # 15. Format data into JSON
            # Placeholder for profit_description_char dict
            profit_description_char = {}  # Populate with actual computed characteristics

            final_output = self.json_formatter.format_to_json(
                metrics, revenue_segmentation, profit_description_char
            )

            # 16. Save JSON to file
            self.save_json_output(symbol, final_output)

            logger.info(f"Successfully processed data for {symbol}")
            return metrics

        except Exception as e:
            logger.error(f"Error processing data for {symbol}: {e}")
            raise

    def _process_yoy_financial_data(self, symbol: str, years: List[int],
                                    income_statements: List[Dict],
                                    balance_sheets: List[Dict],
                                    cash_flows: List[Dict],
                                    key_metrics: List[Dict],
                                    revenue_segmentation: Dict[int, Dict[str, float]]) -> Dict[int, FinancialData]:
        """Processes Year-over-Year financial data."""
        yoy_data = {}
        for year in years:
            income = self._find_statement_for_year(income_statements, year)
            balance = self._find_statement_for_year(balance_sheets, year)
            cash_flow = self._find_statement_for_year(cash_flows, year)
            revenue_breakdown = revenue_segmentation.get(year, {})

            if not income:
                logger.warning(f"No income statement found for {year} ({symbol})")
                continue

            financial_data = FinancialData(
                net_profit=income.get("netIncome"),
                diluted_eps=income.get("epsdiluted"),
                operating_eps=income.get("operatingEps"),
                pe_ratio=self._extract_pe_ratio(key_metrics, year),
                price_low=self.yahoo_client.get_yearly_low(symbol, year),
                price_high=self.yahoo_client.get_yearly_high(symbol, year),
                dividends_paid=-cash_flow.get("dividendsPaid", 0.0),
                dividends_per_share=income.get("dividendsPerShare"),
                avg_dividend_yield=None,  # Calculate as needed
                shares_outstanding=income.get("weightedAverageShsOut", 0),
                buyback=None,  # Calculate as needed
                share_equity=balance.get("totalStockholdersEquity") if balance else None,
                book_value_per_share=None,  # Calculate as needed
                long_term_debt=balance.get("longTermDebt") if balance else None,
                roe=None,  # Calculate as needed
                roc=None,  # Calculate as needed
                # Populate additional fields
            )

            yoy_data[year] = financial_data
            logger.debug(f"Processed YOY data for {year}")

        return yoy_data

    def _find_statement_for_year(self, statements: List[Dict], year: int) -> Optional[Dict]:
        """Finds the financial statement for a specific year."""
        for stmt in statements:
            date_str = stmt.get("date", "")
            if date_str.startswith(str(year)):
                return stmt
        logger.debug(f"No statement found for year {year}")
        return None

    def _extract_pe_ratio(self, key_metrics: List[Dict], year: int) -> Optional[float]:
        """Extracts the P/E ratio for a specific year from key metrics."""
        for km in key_metrics:
            date_str = km.get("date", "")
            if date_str.startswith(str(year)):
                return km.get("peRatio")
        return None

    def _get_market_cap(self, key_metrics: List[Dict]) -> int:
        """Extracts market capitalization from key metrics."""
        if key_metrics:
            latest_metrics = key_metrics[0]
            market_cap = latest_metrics.get("marketCap", 0)
            logger.debug(f"Market Cap: {market_cap}")
            return int(market_cap)
        logger.warning("No key metrics available to extract market cap.")
        return 0

    def save_json_output(self, symbol: str, data: Dict):
        """Saves the formatted JSON data to a file."""
        out_file = os.path.join(self.output_dir, f"{symbol}_yoy_consolidated.json")
        with open(out_file, "w") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Consolidated YOY data saved to '{out_file}'")
