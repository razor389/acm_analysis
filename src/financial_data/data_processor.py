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

    def _find_statement_for_year(self, statements: List[Dict], year: int) -> Optional[Dict]:
        """Helper to get the statement dict for the specified year."""
        for st in statements:
            date_str = st.get("date", "")
            if date_str.startswith(str(year)):
                return st
        return None

    def _calculate_year_metrics(
        self, year: int, statements: Dict, rev_breakdown: Dict, prev_shares: Optional[float]
    ) -> Dict:
        """
        Pull from the raw statements data for a given year, returning a dict of metrics.
        This replicates the 'extract_yoy_data' portion of your old code:
        - Finds the statement for year in the income/balance/cash flow data
        - Extracts net income, revenues, ebit, shares outstanding, etc.
        - Uses Yahoo client to get yearly high/low
        - Returns a dictionary of metrics
        """
        inc = self._find_statement_for_year(statements["income"], year)
        bal = self._find_statement_for_year(statements["balance"], year)
        cf  = self._find_statement_for_year(statements["cash_flow"], year)

        # If no income statement for this year, return empty
        if not inc:
            return {}

        # --- Income statement fields ---
        net_income = inc.get("netIncome")
        revenues = inc.get("revenue")
        diluted_eps = inc.get("epsdiluted")
        ebit = inc.get("operatingIncome")
        shares_out = inc.get("weightedAverageShsOut", 0)
        cost_of_revenue = inc.get("costOfRevenue") or 0
        r_and_d = inc.get("researchAndDevelopmentExpenses") or 0
        sga = inc.get("sellingGeneralAndAdministrativeExpenses") or 0
        total_expenses = cost_of_revenue + r_and_d + sga

        # Operating earnings (revenues - total_expenses)
        operating_earnings = None
        if revenues is not None and total_expenses is not None:
            operating_earnings = revenues - total_expenses

        # Operating margin
        operating_margin = None
        if ebit and revenues:
            operating_margin = ebit / revenues

        # Operating EPS
        operating_eps = None
        if net_income and shares_out:
            operating_eps = net_income / shares_out

        # --- Balance sheet fields ---
        if bal:
            shareholder_equity = bal.get("totalStockholdersEquity")
            long_term_debt = bal.get("longTermDebt")
        else:
            shareholder_equity = None
            long_term_debt = None

        # --- Cash flow fields ---
        if cf:
            dividends_paid = cf.get("dividendsPaid", 0)
            depreciation_amort = cf.get("depreciationAndAmortization")
            capex = cf.get("capitalExpenditure")
            stmt_cf_share_repurchase = cf.get("commonStockRepurchased")
        else:
            dividends_paid = 0
            depreciation_amort = None
            capex = None
            stmt_cf_share_repurchase = None

        # Convert dividends_paid to positive number if negative
        if dividends_paid is not None:
            dividends_paid = -1 * dividends_paid  # your old code multiplied by -1

        # EBITDA approximation
        ebitda = None
        if revenues is not None and total_expenses is not None and depreciation_amort:
            ebitda = revenues - total_expenses + depreciation_amort

        # Free cash flow approximation
        fcf = None
        if ebitda is not None and capex is not None:
            fcf = ebitda + capex  # since capex is typically negative in statements

        # Use Yahoo to get yearly high/low
        year_high, year_low = self.yahoo_client.get_yearly_high_low(inc.get("symbol", ""), year)
        average_price = None
        if year_high and year_low:
            average_price = (year_high + year_low) / 2

        # If we had a previous shares count, compute buyback
        buyback = None
        if prev_shares is not None and shares_out and average_price:
            share_change = prev_shares - shares_out
            buyback = share_change * average_price

        # Build the metric dict
        metrics = {
            "year": year,
            "net_income": net_income,
            "revenues": revenues,
            "diluted_eps": diluted_eps,
            "ebit": ebit,
            "operating_margin": operating_margin,
            "operating_eps": operating_eps,
            "shares_outstanding": shares_out,
            "dividends_paid": dividends_paid,
            "depreciation_amort": depreciation_amort,
            "capex": capex,
            "ebitda": ebitda,
            "free_cash_flow": fcf,
            "buyback": buyback,
            "operating_earnings": operating_earnings,
            "long_term_debt": long_term_debt,
            "shareholder_equity": shareholder_equity,
            "cost_of_revenue": cost_of_revenue,
            "research_and_development": r_and_d,
            "selling_gen_admin": sga,
            "stmt_cf_share_repurchase": stmt_cf_share_repurchase,
            "yearly_high": year_high,
            "yearly_low": year_low,
            "average_price": average_price,
            "revenue_breakdown": rev_breakdown
        }
        return metrics

    def _compute_investment_characteristics(self, yoy_data: Dict) -> Dict:
        """
        Example that demonstrates computing growth rates (CAGR) for Operating EPS,
        plus other metrics like 'quality_percent', etc., from yoy_data.
        This code merges your old 'compute_investment_characteristics' logic.
        """
        # Sort year keys
        sorted_years = sorted(yoy_data.keys())

        # Helper function to gather (year, value) pairs for a given chain of keys
        # yoy_data[year] -> a metrics dict
        def get_values_for_chain(chain: List[str]):
            # e.g. chain = ["operating_eps"]
            vals = []
            for y in sorted_years:
                data_y = yoy_data[y]
                # data_y is the dict we returned from _calculate_year_metrics
                # so we get data_y.get("operating_eps")
                val = data_y.get(chain[0], None)  # if chain length is 1
                if val is not None:
                    vals.append((y, val))
            return vals

        # We'll store results in this dictionary
        results = {
            "earnings_analysis": {
                "growth_rate_percent_operating_eps": None,
                "quality_percent": None
            },
            "use_of_earnings_analysis": {
                "avg_dividend_payout_percent": None,
                "avg_stock_buyback_percent": None
            },
            "sales_analysis": {
                "growth_rate_percent_revenues": None,
                "growth_rate_percent_sales_per_share": None
            },
            "sales_analysis_last_5_years": {
                "growth_rate_percent_revenues": None,
                "growth_rate_percent_sales_per_share": None
            }
        }

        # 1) CAGR Operating EPS
        ops_eps_pairs = get_values_for_chain(["operating_eps"])
        if len(ops_eps_pairs) >= 2:
            cagr_ops = calculate_cagr(ops_eps_pairs)
            results["earnings_analysis"]["growth_rate_percent_operating_eps"] = cagr_ops

        # 2) Quality % = (avg of diluted_eps) / (avg of operating_eps)
        total_eps = 0
        total_oeps = 0
        count_eps = 0
        count_oeps = 0
        for y in sorted_years:
            m = yoy_data[y]
            d_eps = m.get("diluted_eps")
            o_eps = m.get("operating_eps")
            if d_eps is not None:
                total_eps += d_eps
                count_eps += 1
            if o_eps is not None:
                total_oeps += o_eps
                count_oeps += 1
        if count_eps and count_oeps and total_oeps != 0:
            results["earnings_analysis"]["quality_percent"] = round((total_eps / count_eps) / (total_oeps / count_oeps), 2)

        # 3) Avg Dividend Payout % = (dividends_per_share / operating_eps) across years
        # but from our new yoy_data, we only have 'dividends_paid' and 'shares_outstanding', so let's do:
        sum_div_share = 0
        sum_op_eps = 0
        count_div = 0
        for y in sorted_years:
            m = yoy_data[y]
            div_paid = m.get("dividends_paid")
            sh_out = m.get("shares_outstanding")
            op_eps = m.get("operating_eps")

            if div_paid and sh_out and op_eps and op_eps != 0:
                # dividends_per_share = div_paid / sh_out
                dps = div_paid / sh_out
                sum_div_share += dps
                sum_op_eps += op_eps
                count_div += 1
        if count_div > 0 and sum_op_eps != 0:
            avg_dps = sum_div_share / count_div
            avg_op_eps = sum_op_eps / count_div
            results["use_of_earnings_analysis"]["avg_dividend_payout_percent"] = round((avg_dps / avg_op_eps), 2)

        # 4) Avg Stock Buyback % = sum(buyback) / sum(net_income)
        sum_buybacks = 0
        sum_net_income = 0
        for y in sorted_years:
            buyback_val = yoy_data[y].get("buyback")
            net_inc = yoy_data[y].get("net_income")
            if buyback_val and net_inc and net_inc != 0:
                sum_buybacks += buyback_val
                sum_net_income += net_inc
        if sum_net_income != 0:
            results["use_of_earnings_analysis"]["avg_stock_buyback_percent"] = round(sum_buybacks / sum_net_income, 2)

        # 5) Sales Analysis: CAGR of revenues, sales_per_share (we need to compute sales_per_share ourselves if we want)
        # For your old code, you did yoy_data[year]["analyses"].get("sales_per_share")
        # but we are storing 'revenues' in yoy_data[year]["revenues"] and so on. Let's just do:
        rev_pairs = []
        sps_pairs = []
        for y in sorted_years:
            rev = yoy_data[y].get("revenues")
            shares = yoy_data[y].get("shares_outstanding")
            if rev is not None:
                rev_pairs.append((y, rev))
            if rev is not None and shares:
                sps = rev / shares
                sps_pairs.append((y, sps))

        if len(rev_pairs) >= 2:
            results["sales_analysis"]["growth_rate_percent_revenues"] = calculate_cagr(rev_pairs)
        if len(sps_pairs) >= 2:
            results["sales_analysis"]["growth_rate_percent_sales_per_share"] = calculate_cagr(sps_pairs)

        # 6) Sales analysis last 5 yrs
        last_5_yrs = sorted_years[-5:]
        rev_pairs_5y = []
        sps_pairs_5y = []
        for y in last_5_yrs:
            rev = yoy_data[y].get("revenues")
            shares = yoy_data[y].get("shares_outstanding")
            if rev is not None:
                rev_pairs_5y.append((y, rev))
            if rev is not None and shares:
                sps_5y = rev / shares
                sps_pairs_5y.append((y, sps_5y))
        if len(rev_pairs_5y) >= 2:
            results["sales_analysis_last_5_years"]["growth_rate_percent_revenues"] = calculate_cagr(rev_pairs_5y)
        if len(sps_pairs_5y) >= 2:
            results["sales_analysis_last_5_years"]["growth_rate_percent_sales_per_share"] = calculate_cagr(sps_pairs_5y)

        return results

    def _compute_balance_sheet_characteristics(self, yoy_data: Dict) -> Dict:
        """
        Compute CAGR for total assets, total liabilities, total equity, etc., using logic from your old code.
        We rely on yoy_data[y]["balance_sheet"] if you choose to store assets, liabilities, etc. there.
        """
        results = {
            "cagr_total_assets_percent": None,
            "cagr_total_liabilities_percent": None,
            "cagr_total_shareholders_equity_percent": None
        }

        sorted_years = sorted(yoy_data.keys())
        if len(sorted_years) < 2:
            return results

        # helper to build list of (year, value) pairs
        def get_bs_values(metric_key):
            pairs = []
            for y in sorted_years:
                # yoy_data[y].get("...somebalancefield...")
                # We didn't store an explicit "totalAssets" in yoy_data[y], but we do have
                # yoy_data[y]["balance_sheet"]["assets"]["total_assets"] if you prefer to store that.
                bsheet = yoy_data[y].get("balance_sheet", {})
                assets_dict = bsheet.get("assets", {})
                liab_dict = bsheet.get("liabilities", {})
                eq_dict = bsheet.get("shareholders_equity", {})

                val = None
                if metric_key == "assets":
                    val = assets_dict.get("total_assets")
                elif metric_key == "liabilities":
                    val = liab_dict.get("total_liabilities")
                elif metric_key == "equity":
                    val = eq_dict.get("total_shareholders_equity")

                if val is not None:
                    pairs.append((y, val))
            return pairs

        assets_pairs = get_bs_values("assets")
        liab_pairs = get_bs_values("liabilities")
        eq_pairs = get_bs_values("equity")

        if len(assets_pairs) >= 2:
            results["cagr_total_assets_percent"] = calculate_cagr(assets_pairs)
        if len(liab_pairs) >= 2:
            results["cagr_total_liabilities_percent"] = calculate_cagr(liab_pairs)
        if len(eq_pairs) >= 2:
            results["cagr_total_shareholders_equity_percent"] = calculate_cagr(eq_pairs)

        return results

    def _compute_profit_characteristics(self, yoy_data: Dict) -> Dict:
        """
        Compute CAGR for various profit metrics (revenues, ebitda, free cash flow, etc.).
        Incorporates logic similar to your old 'compute_profit_description_characteristics'.
        """
        sorted_years = sorted(yoy_data.keys())
        if len(sorted_years) < 2:
            return {
                "cagr_revenues_percent": None,
                "cagr_total_expenses_percent": None,
                "cagr_ebitda_percent": None,
                "cagr_free_cash_flow_percent": None,
                "cagr_operating_earnings_percent": None,
                "cagr_total_external_costs_percent": None,
                "cagr_earnings_percent": None,
                "cagr_cost_of_revenue_percent": None,
                "cagr_research_and_development_percent": None,
                "cagr_selling_marketing_general_admin_percent": None,
                "cagr_external_costs_breakdown_percent": {},
                "cagr_revenues_breakdown_percent": {}
            }

        # We'll store results in a dict
        results = {}
        # Pre-populate for convenience
        for key in [
            "cagr_revenues_percent", "cagr_total_expenses_percent", "cagr_ebitda_percent",
            "cagr_free_cash_flow_percent", "cagr_operating_earnings_percent", "cagr_total_external_costs_percent",
            "cagr_earnings_percent", "cagr_cost_of_revenue_percent", "cagr_research_and_development_percent",
            "cagr_selling_marketing_general_admin_percent"
        ]:
            results[key] = None
        results["cagr_external_costs_breakdown_percent"] = {}
        results["cagr_revenues_breakdown_percent"] = {}

        def build_pairs(metric_name: str):
            """
            Helper to gather (year, value) for yoy_data[y].get(metric_name).
            Example metrics: "revenues", "ebitda", "free_cash_flow", etc.
            """
            pairs = []
            for y in sorted_years:
                val = yoy_data[y].get(metric_name)
                if val is not None:
                    pairs.append((y, float(val)))
            return pairs

        # Let's define each top-level metric we want to measure
        top_metrics = {
            "cagr_revenues_percent": "revenues",
            "cagr_ebitda_percent": "ebitda",
            "cagr_free_cash_flow_percent": "free_cash_flow",
            "cagr_operating_earnings_percent": "operating_earnings",
            "cagr_earnings_percent": "net_income"
        }
        # We'll just do total_expenses by summing cost_of_revenue + research_and_development + selling_gen_admin
        # if you want an explicit yoy_data[y]["expenses"] you can do that:
        # or we can compute on the fly in build_expenses_pairs
        def build_expenses_pairs():
            pairs = []
            for y in sorted_years:
                cor = yoy_data[y].get("cost_of_revenue", 0)
                rnd = yoy_data[y].get("research_and_development", 0)
                sga = yoy_data[y].get("selling_gen_admin", 0)
                total_exp = cor + rnd + sga
                pairs.append((y, float(total_exp)))
            return pairs

        exp_pairs = build_expenses_pairs()
        if len(exp_pairs) >= 2:
            results["cagr_total_expenses_percent"] = calculate_cagr(exp_pairs)

        # Now compute each top metric
        for cagr_key, yoy_key in top_metrics.items():
            pairs = build_pairs(yoy_key)
            if len(pairs) >= 2:
                results[cagr_key] = calculate_cagr(pairs)

        # cost_of_revenue, r_and_d, sga individually
        # cagr_cost_of_revenue_percent, cagr_research_and_development_percent, cagr_selling_marketing_general_admin_percent
        def build_pairs_for_key(key):
            out = []
            for y in sorted_years:
                val = yoy_data[y].get(key)
                if val is not None:
                    out.append((y, float(val)))
            return out

        cor_pairs = build_pairs_for_key("cost_of_revenue")
        if len(cor_pairs) >= 2:
            results["cagr_cost_of_revenue_percent"] = calculate_cagr(cor_pairs)
        rnd_pairs = build_pairs_for_key("research_and_development")
        if len(rnd_pairs) >= 2:
            results["cagr_research_and_development_percent"] = calculate_cagr(rnd_pairs)
        sga_pairs = build_pairs_for_key("selling_gen_admin")
        if len(sga_pairs) >= 2:
            results["cagr_selling_marketing_general_admin_percent"] = calculate_cagr(sga_pairs)

        # If you want to replicate "external_costs" or "breakdown" logic, adapt here:
        # We'll leave it as is or set it to {} for now
        # e.g. results["cagr_external_costs_breakdown_percent"]["cagr_external_costs_interest_expense_percent"] = ...
        # but that's optional.

        # We won't fill them, so they'll remain empty:
        results["cagr_external_costs_breakdown_percent"] = {}
        results["cagr_revenues_breakdown_percent"] = {}
        return results

    def _get_short_quote(self, symbol: str) -> Optional[float]:
        """
        Example placeholder to fetch short quote from FMP or return None.
        If you had a function get_quote_short(symbol) in your old code, you can call it here.
        """
        # For example:
        try:
            quote_data = self.fmp_client._get(f"quote-short/{symbol}")
            if isinstance(quote_data, list) and len(quote_data) > 0:
                return quote_data[0].get("price")
        except:
            pass
        return None
