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
from financial_data.models import Analyses, AnalysesYoYData, AnalysisOfDebtLevels, AssetsBreakdown, BalanceSheet, BalanceSheetCharacteristics, BalanceSheetData, ExpensesBreakdown, ExternalCostBreakdown, InvestmentCharacteristics, InvestmentCharacteristicsSection, LiabilitiesBreakdown, Metrics, FinancialData, ProfitDescription, ProfitDescriptionCharacteristics, ProfitDescriptionData, SalesAnalysis, ShareholdersEquityBreakdown, Studies, UseOfEarningsAnalysis
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

            # 4. Extract financial statements and data
            income_statements = raw_data["income_statements"]
            balance_sheets = raw_data["balance_sheets"]
            cash_flows = raw_data["cash_flows"]
            key_metrics = raw_data["key_metrics"]
            revenue_segmentation = raw_data["revenue_segmentation"]
            current_stock_price = raw_data["current_stock_price"]

            # 5. Derive end year and validate
            end_year = most_recent_fiscal_year
            if start_year > end_year:
                logger.error("START_YEAR cannot be greater than END_YEAR.")
                raise ValueError("START_YEAR cannot be greater than END_YEAR.")

            years_to_extract = list(range(start_year, end_year + 1))
            logger.info(f"Processing data for {symbol} from {start_year} to {end_year}")

            # 6. Process YOY financial data
            yoy_financial_data = self._process_yoy_financial_data(
                symbol, years_to_extract, income_statements, balance_sheets, 
                cash_flows, key_metrics, revenue_segmentation
            )

            # 7. Create company description
            company_description = self.data_transformer.transform_company_description(
                fiscal_year_end, 
                current_stock_price,
                self._get_market_cap(key_metrics),
                yoy_financial_data
            )

            # 8. Process analyses section
            analyses = self._process_analyses(yoy_financial_data)

            # 9. Process profit description
            profit_description = self._process_profit_description(
                income_statements,
                revenue_segmentation,
                years_to_extract
            )

            # 10. Process balance sheet
            balance_sheet = self._process_balance_sheet(
                balance_sheets,
                years_to_extract
            )

            # 11. Process studies
            studies = self._process_studies(
                balance_sheets,
                income_statements,
                yoy_financial_data,
                years_to_extract
            )

            # 12. Compile Metrics dataclass
            metrics = Metrics(
                company_profile=profile,
                company_description=company_description,
                analyses=analyses,
                profit_description=profit_description,
                balance_sheet=balance_sheet,
                studies=studies
            )

            # 13. Format data into JSON
            profit_description_char = self._calculate_profit_description_characteristics(
                income_statements,
                revenue_segmentation,
                years_to_extract
            )

            final_output = self.json_formatter.format_to_json(
                metrics, 
                revenue_segmentation, 
                profit_description_char
            )

            # 14. Save JSON output
            self.save_json_output(symbol, final_output)

            logger.info(f"Successfully processed data for {symbol}")
            return metrics

        except Exception as e:
            logger.error(f"Error processing data for {symbol}: {e}")
            raise

    def _find_statement_for_year(self, statements: List[Dict], year: int) -> Optional[Dict]:
        """
        Find the financial statement for a specific year from a list of statements.

        Args:
            statements: List of financial statements (income, balance sheet, cash flow, etc.)
            year: Year to find statement for

        Returns:
            Dict containing the statement data if found, None otherwise
        """
        for stmt in statements:
            # FMP API returns date in format "YYYY-MM-DD"
            stmt_date = stmt.get("date", "")
            if stmt_date.startswith(str(year)):
                return stmt
        
        logger.debug(f"No statement found for year {year}")
        return None

    def _process_yoy_financial_data(
        self,
        symbol: str,
        years: List[int],
        income_statements: List[Dict],
        balance_sheets: List[Dict],
        cash_flows: List[Dict],
        key_metrics: List[Dict],
        revenue_segmentation: Dict[int, Dict[str, float]]
    ) -> Dict[int, FinancialData]:
        """
        Process year-over-year financial data from various statements.
        
        Args:
            symbol: Company ticker symbol
            years: List of years to process
            income_statements: List of income statements
            balance_sheets: List of balance sheets
            cash_flows: List of cash flow statements
            key_metrics: List of key metrics
            revenue_segmentation: Revenue breakdown by segment
            
        Returns:
            Dict mapping years to FinancialData objects
        """
        yoy_data = {}
        
        for year in years:
            # Find statements for the year
            income = self._find_statement_for_year(income_statements, year)
            balance = self._find_statement_for_year(balance_sheets, year)
            cash_flow = self._find_statement_for_year(cash_flows, year)
            key_metric = self._find_statement_for_year(key_metrics, year)
            
            if not income:
                logger.warning(f"No income statement found for {year} ({symbol})")
                continue
                
            if not balance:
                logger.warning(f"No balance sheet found for {year} ({symbol})")
                continue
                
            if not cash_flow:
                logger.warning(f"No cash flow statement found for {year} ({symbol})")
                continue

            # Calculate operating metrics
            total_revenue = income.get("revenue", 0)
            shares_outstanding = income.get("weightedAverageShsOut", 0)
            operating_income = income.get("operatingIncome", 0)
            
            # Calculate sales per share
            sales_per_share = (total_revenue / shares_outstanding) if shares_outstanding else None
            
            # Calculate margins and rates
            operating_margin = (operating_income / total_revenue * 100) if total_revenue else None
            tax_expense = income.get("incomeTaxExpense", 0)
            income_before_tax = income.get("incomeBeforeTax", 0)
            tax_rate = (tax_expense / income_before_tax * 100) if income_before_tax else None
            
            # Calculate depreciation metrics
            depreciation = income.get("depreciationAndAmortization", 0)
            net_income = income.get("netIncome", 0)
            depreciation_pct = (depreciation / net_income * 100) if net_income else None
            
            # Calculate ROE and ROC
            avg_equity = (
                balance.get("totalStockholdersEquity", 0) + 
                self._get_prev_year_equity(balance_sheets, year)
            ) / 2
            
            roe = (net_income / avg_equity * 100) if avg_equity else None
            
            total_capital = avg_equity + balance.get("totalDebt", 0)
            roc = (operating_income / total_capital * 100) if total_capital else None
            
            # Calculate book value and buyback metrics
            book_value = balance.get("totalStockholdersEquity", 0)
            book_value_per_share = book_value / shares_outstanding if shares_outstanding else None
            
            buyback = abs(cash_flow.get("commonStockRepurchased", 0))
            
            # Calculate dividend metrics
            dividends_paid = abs(cash_flow.get("dividendsPaid", 0))
            dividends_per_share = income.get("dividendPerShare", 0)
            dividend_yield = key_metric.get("dividendYield", 0) if key_metric else None
            
            # Get stock price metrics
            price_high = self.yahoo_client.get_yearly_high(symbol, year)
            price_low = self.yahoo_client.get_yearly_low(symbol, year)
            pe_ratio = key_metric.get("peRatio", None) if key_metric else None

            # Create FinancialData object for the year
            financial_data = FinancialData(
                net_profit=net_income,
                diluted_eps=income.get("epsDiluted"),
                operating_eps=income.get("operatingIncome") / shares_outstanding if shares_outstanding else None,
                pe_ratio=pe_ratio,
                price_low=price_low,
                price_high=price_high,
                dividends_paid=dividends_paid,
                dividends_per_share=dividends_per_share,
                avg_dividend_yield=dividend_yield,
                shares_outstanding=shares_outstanding,
                buyback=buyback,
                share_equity=book_value,
                book_value_per_share=book_value_per_share,
                long_term_debt=balance.get("longTermDebt"),
                roe=roe,
                roc=roc,
                # Additional calculated fields for analyses
                revenues=total_revenue,
                sales_per_share=sales_per_share,
                operating_margin=operating_margin,
                tax_rate=tax_rate,
                depreciation=depreciation,
                depreciation_pct=depreciation_pct
            )
            
            yoy_data[year] = financial_data
            logger.debug(f"Processed YOY data for {year}")
            
        return yoy_data

    def _get_prev_year_equity(self, balance_sheets: List[Dict], current_year: int) -> float:
        """Helper to get previous year's equity for average calculation."""
        prev_year_bs = self._find_statement_for_year(balance_sheets, current_year - 1)
        if prev_year_bs:
            return prev_year_bs.get("totalStockholdersEquity", 0)
        return 0

    def _process_analyses(self, yoy_financial_data: Dict[int, FinancialData]) -> Analyses:
        """Process analyses section of the metrics."""
        # Compute investment characteristics
        earnings_analysis = self.metrics_calculator.compute_earnings_analysis(yoy_financial_data)
        use_of_earnings = self.metrics_calculator.compute_use_of_earnings_analysis(yoy_financial_data)
        sales_analysis = self.metrics_calculator.compute_sales_analysis(yoy_financial_data)
        sales_analysis_5y = self.metrics_calculator.compute_sales_analysis_last_5_years(yoy_financial_data)

        # Create investment characteristics section
        investment_chars = InvestmentCharacteristicsSection(
            earnings_analysis=InvestmentCharacteristics(**earnings_analysis),
            use_of_earnings_analysis=UseOfEarningsAnalysis(**use_of_earnings),
            sales_analysis=SalesAnalysis(**sales_analysis),
            sales_analysis_last_5_years=SalesAnalysis(**sales_analysis_5y)
        )

        # Create analyses year-over-year data
        analyses_yoy_data = {}
        for year, data in yoy_financial_data.items():
            analyses_yoy_data[str(year)] = AnalysesYoYData(
                revenues=data.revenues,
                sales_per_share=data.sales_per_share,
                operating_margin_pct=data.operating_margin,
                tax_rate=data.tax_rate,
                depreciation=data.depreciation,
                depreciation_pct=data.depreciation_pct
            )

        return Analyses(
            investment_characteristics=investment_chars,
            data=analyses_yoy_data
        )

    def _process_profit_description(self, 
                                income_statements: List[Dict],
                                revenue_segmentation: Dict[int, Dict[str, float]],
                                years: List[int]) -> ProfitDescription:
        """Process profit description section of the metrics."""
        profit_desc_data = {}
        
        for year in years:
            income_stmt = self._find_statement_for_year(income_statements, year)
            if not income_stmt:
                continue

            # Create revenue breakdown
            revenue_breakdown = revenue_segmentation.get(year, {})

            # Create expenses breakdown
            expenses_breakdown = ExpensesBreakdown(
                cost_of_revenue=income_stmt.get("costOfRevenue"),
                research_and_development=income_stmt.get("researchAndDevelopment"),
                selling_marketing_general_admin=income_stmt.get("sellingAndMarketingExpenses")
            )

            # Create external costs breakdown
            external_costs_breakdown = ExternalCostBreakdown(
                income_taxes=income_stmt.get("incomeTaxExpense"),
                interest_and_other_income=income_stmt.get("interestIncome")
            )

            # Create profit description data
            profit_desc_data[str(year)] = ProfitDescriptionData(
                total_revenues=income_stmt.get("revenue"),
                revenue_breakdown=revenue_breakdown,
                total_expenses=income_stmt.get("totalExpenses"),
                expenses_breakdown=expenses_breakdown,
                ebitda=income_stmt.get("ebitda"),
                amortization_depreciation=income_stmt.get("depreciationAndAmortization"),
                free_cash_flow=income_stmt.get("freeCashFlow"),
                capex=income_stmt.get("capitalExpenditure"),
                operating_earnings=income_stmt.get("operatingIncome"),
                operating_earnings_percent_revenue=str(round(income_stmt.get("operatingIncomeRatio", 0) * 100, 2)) + "%",
                total_external_costs=income_stmt.get("totalOtherIncomeExpensesNet"),
                external_cost_breakdown=external_costs_breakdown,
                earnings=income_stmt.get("netIncome"),
                earnings_percent_revenue=str(round(income_stmt.get("netIncomeRatio", 0) * 100, 2)) + "%",
                dividend_paid=str(income_stmt.get("dividendsPaid", 0)),
                dividend_paid_pct_fcf=None,  # Calculate if needed
                share_buybacks_from_stmt_cf=income_stmt.get("stockRepurchased", 0),
                net_biz_acquisition=income_stmt.get("acquisitionsNet", 0)
            )

        # Calculate characteristics
        characteristics = self._calculate_profit_description_characteristics(
            income_statements,
            revenue_segmentation,
            years
        )

        return ProfitDescription(
            profit_description_characteristics=ProfitDescriptionCharacteristics(**characteristics),
            data=profit_desc_data
        )

    def _process_balance_sheet(self, 
                            balance_sheets: List[Dict],
                            years: List[int]) -> BalanceSheet:
        """Process balance sheet section of the metrics."""
        balance_sheet_data = {}
        
        for year in years:
            bs = self._find_statement_for_year(balance_sheets, year)
            if not bs:
                continue

            # Create assets breakdown
            assets_breakdown = AssetsBreakdown(
                cash_and_cash_equivalents=bs.get("cashAndCashEquivalents"),
                short_term_investment=bs.get("shortTermInvestments"),
                accounts_receivable_net=bs.get("netReceivables"),
                other_current_assets=bs.get("otherCurrentAssets"),
                land_property_equipment_net=bs.get("propertyPlantEquipmentNet"),
                goodwill_and_intangible_assets=bs.get("goodwill"),
                other_non_current=bs.get("otherNonCurrentAssets"),
                long_term_equity_investment=bs.get("longTermInvestments")
            )

            # Create liabilities breakdown
            liabilities_breakdown = LiabilitiesBreakdown(
                accounts_payable=bs.get("accountPayables"),
                tax_payables=bs.get("taxPayables"),
                other_current_liabilities=bs.get("otherCurrentLiabilities"),
                deferred_revenue=bs.get("deferredRevenue"),
                short_term_debt=bs.get("shortTermDebt"),
                long_term_debt_minus_capital_lease_obligation=bs.get("longTermDebt"),
                other_non_current_liabilities=bs.get("otherNonCurrentLiabilities"),
                capital_lease_obligations=bs.get("capitalLeaseObligations")
            )

            # Create shareholders equity breakdown
            equity_breakdown = ShareholdersEquityBreakdown(
                common_stock=bs.get("commonStock"),
                additional_paid_in_capital=bs.get("additionalPaidInCapital"),
                retained_earnings=bs.get("retainedEarnings"),
                accum_other_comprehensive_income_loss=bs.get("accumulatedOtherComprehensiveIncomeLoss")
            )

            # Create balance sheet data
            balance_sheet_data[str(year)] = BalanceSheetData(
                total_assets=bs.get("totalAssets"),
                assets_breakdown=assets_breakdown,
                total_liabilities=bs.get("totalLiabilities"),
                liabilities_breakdown=liabilities_breakdown,
                total_shareholders_equity=bs.get("totalStockholdersEquity"),
                shareholders_equity_breakdown=equity_breakdown
            )

        # Calculate characteristics
        characteristics = self._calculate_balance_sheet_characteristics(balance_sheets, years)

        return BalanceSheet(
            balance_sheet_characteristics=BalanceSheetCharacteristics(**characteristics),
            data=balance_sheet_data
        )

    def _process_studies(self,
                        balance_sheets: List[Dict],
                        income_statements: List[Dict],
                        yoy_financial_data: Dict[int, FinancialData],
                        years: List[int]) -> Studies:
        """Process studies section of the metrics."""
        # Get most recent year's data
        latest_year = max(years)
        latest_bs = self._find_statement_for_year(balance_sheets, latest_year)
        latest_income = self._find_statement_for_year(income_statements, latest_year)

        if not (latest_bs and latest_income):
            return Studies()

        # Calculate total debt metrics
        total_debt = (latest_bs.get("shortTermDebt", 0) or 0) + (latest_bs.get("longTermDebt", 0) or 0)
        total_capital = total_debt + (latest_bs.get("totalStockholdersEquity", 0) or 0)
        total_debt_ratio = (total_debt / total_capital * 100) if total_capital else None

        # Calculate long term debt metrics
        lt_debt = latest_bs.get("longTermDebt", 0) or 0
        lt_capital = lt_debt + (latest_bs.get("totalStockholdersEquity", 0) or 0)
        lt_debt_ratio = (lt_debt / lt_capital * 100) if lt_capital else None

        # Calculate net income metrics
        net_income = latest_income.get("netIncome", 0) or 0
        years_payback_total_debt = total_debt / net_income if net_income else None
        years_payback_lt_debt = lt_debt / net_income if net_income else None

        # Calculate addback metrics
        addback = net_income + (latest_income.get("depreciationAndAmortization", 0) or 0)
        years_payback_addback = lt_debt / addback if addback else None

        return Studies(
            total_debt_capital=AnalysisOfDebtLevels(
                total_debt=total_debt,
                total_capital=total_capital,
                total_debt_ratio=total_debt_ratio
            ),
            long_term_debt=AnalysisOfDebtLevels(
                lt_debt=lt_debt,
                lt_capital=lt_capital,
                lt_debt_ratio=lt_debt_ratio
            ),
            net_income_payback=AnalysisOfDebtLevels(
                total_debt=total_debt,
                net_income=net_income,
                years_payback_total_debt=years_payback_total_debt,
                lt_debt=lt_debt,
                years_payback_lt_debt=years_payback_lt_debt
            ),
            addback_net_inc_payback=AnalysisOfDebtLevels(
                lt_debt=lt_debt,
                net_income=net_income,
                addback=addback,
                years_payback=years_payback_addback
            )
        )

    def _calculate_profit_description_characteristics(self,
                                                income_statements: List[Dict],
                                                revenue_segmentation: Dict[int, Dict[str, float]],
                                                years: List[int]) -> Dict:
        """Calculate profit description characteristics."""
        # Extract time series for various metrics
        metrics_series = {
            "revenues": [],
            "total_expenses": [],
            "ebitda": [],
            "free_cash_flow": [],
            "operating_earnings": [],
            "total_external_costs": [],
            "earnings": [],
            "cost_of_revenue": [],
            "research_and_development": [],
            "selling_marketing_general_admin": [],
            "income_taxes": [],
            "interest_and_other_income": []
        }

        # Populate time series data
        for year in years:
            stmt = self._find_statement_for_year(income_statements, year)
            if not stmt:
                continue

            metrics_series["revenues"].append((year, stmt.get("revenue")))
            metrics_series["total_expenses"].append((year, stmt.get("totalExpenses")))
            metrics_series["ebitda"].append((year, stmt.get("ebitda")))
            metrics_series["free_cash_flow"].append((year, stmt.get("freeCashFlow")))
            metrics_series["operating_earnings"].append((year, stmt.get("operatingIncome")))
            metrics_series["total_external_costs"].append((year, stmt.get("totalOtherIncomeExpensesNet")))
            metrics_series["earnings"].append((year, stmt.get("netIncome")))
            metrics_series["cost_of_revenue"].append((year, stmt.get("costOfRevenue")))
            metrics_series["research_and_development"].append((year, stmt.get("researchAndDevelopment")))
            metrics_series["selling_marketing_general_admin"].append((year, stmt.get("sellingAndMarketingExpenses")))
            metrics_series["income_taxes"].append((year, stmt.get("incomeTaxExpense")))
            metrics_series["interest_and_other_income"].append((year, stmt.get("interestIncome")))

        # Calculate CAGR for each metric
        characteristics = {}
        for metric_name, series in metrics_series.items():
            cagr = self.metrics_calculator.compute_cagr(series)
            if cagr is not None:
                characteristics[f"cagr_{metric_name}_percent"] = cagr

        # Calculate CAGR for revenue segmentation
        revenue_breakdown_cagr = self.metrics_calculator.compute_revenue_breakdown_cagr(revenue_segmentation)
        if revenue_breakdown_cagr:
            characteristics["cagr_revenues_breakdown_percent"] = revenue_breakdown_cagr
            
        # Create external costs breakdown CAGR
        characteristics["cagr_external_costs_breakdown_percent"] = {
            "cagr_external_costs_income_taxes_percent": characteristics.get("cagr_income_taxes_percent"),
            "cagr_external_costs_interest_and_other_income_percent": characteristics.get("cagr_interest_and_other_income_percent")
        }

        return characteristics

    def _calculate_balance_sheet_characteristics(self, balance_sheets: List[Dict], years: List[int]) -> Dict:
        """Calculate balance sheet characteristics."""
        # Extract time series for assets, liabilities, equity
        metrics_series = {
            "total_assets": [],
            "total_liabilities": [],
            "total_shareholders_equity": []
        }

        # Populate time series data
        for year in years:
            bs = self._find_statement_for_year(balance_sheets, year)
            if not bs:
                continue

            metrics_series["total_assets"].append((year, bs.get("totalAssets")))
            metrics_series["total_liabilities"].append((year, bs.get("totalLiabilities")))
            metrics_series["total_shareholders_equity"].append((year, bs.get("totalStockholdersEquity")))

        # Calculate CAGR for each metric
        characteristics = {}
        for metric_name, series in metrics_series.items():
            cagr = self.metrics_calculator.compute_cagr(series)
            if cagr is not None:
                characteristics[f"cagr_{metric_name}_percent"] = cagr

        return characteristics

    def _get_market_cap(self, key_metrics: List[Dict]) -> int:
        """
        Extract market capitalization from key metrics.
        
        Args:
            key_metrics: List of key metrics data from FMP API

        Returns:
            Market capitalization as integer
        """
        if not key_metrics:
            logger.warning("No key metrics available to extract market cap")
            return 0
            
        # Get most recent key metrics
        latest_metrics = key_metrics[0]  # FMP API returns metrics in reverse chronological order
        market_cap = latest_metrics.get("marketCap", 0)
        
        logger.debug(f"Market Cap extracted: {market_cap}")
        return int(market_cap)