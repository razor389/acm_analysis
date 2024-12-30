# src/financial_data/processors/json_formatter.py

import logging
from typing import Dict, Any

from financial_data.models import Metrics

logger = logging.getLogger(__name__)

class JSONFormatter:
    """Formats Metrics dataclass into the desired JSON structure."""

    def __init__(self):
        logger.debug("JSONFormatter initialized.")

    def format_to_json(self, metrics: Metrics, revenue_segmentation: Dict[int, Dict[str, float]],
                      profit_description_char: Dict[str, Any]) -> Dict[str, Any]:
        """Converts Metrics dataclass to the specified JSON format."""
        final_output = {
            "summary": {
                "symbol": metrics.company_profile.symbol,
                "company_name": metrics.company_profile.company_name,
                "exchange": metrics.company_profile.exchange,
                "description": metrics.company_profile.description,
                "sector": metrics.company_profile.sector,
                "subsector": metrics.company_profile.industry
            },
            "company_description": {
                "fiscal_year_end": metrics.company_description.fiscal_year_end,
                "stock_price": f"{metrics.company_description.stock_price:.2f}",
                "marketCapitalization": f"{metrics.company_description.market_cap}",
                "data": {
                    year: {
                        "net_profit": f"{data.net_profit:.2f}" if data.net_profit else "0.00",
                        "diluted_eps": f"{data.diluted_eps:.2f}" if data.diluted_eps else None,
                        "operating_eps": f"{data.operating_eps:.2f}" if data.operating_eps else None,
                        "pe_ratio": f"{data.pe_ratio:.2f}" if data.pe_ratio else None,
                        "price_low": f"{data.price_low:.2f}" if data.price_low else None,
                        "price_high": f"{data.price_high:.2f}" if data.price_high else None,
                        "dividends_paid": f"{data.dividends_paid:.2f}" if data.dividends_paid else "0.00",
                        "dividends_per_share": f"{data.dividends_per_share:.2f}" if data.dividends_per_share else None,
                        "avg_dividend_yield": f"{data.avg_dividend_yield:.2f}%" if data.avg_dividend_yield else None,
                        "shares_outstanding": f"{int(data.shares_outstanding)}" if data.shares_outstanding else "0",
                        "buyback": f"{data.buyback:.2f}" if data.buyback else "0.00",
                        "share_equity": f"{data.share_equity:.2f}" if data.share_equity else "0.00",
                        "book_value_per_share": f"{data.book_value_per_share:.2f}" if data.book_value_per_share else None,
                        "long_term_debt": f"{data.long_term_debt:.2f}" if data.long_term_debt else "0.00",
                        "roe": f"{data.roe:.2f}%" if data.roe else None,
                        "roc": f"{data.roc:.2f}%" if data.roc else None
                    } for year, data in metrics.company_description.yoy_financial_data.items()
                }
            },
            "analyses": {
                "investment_characteristics": {
                    "earnings_analysis": {
                        "growth_rate_percent_operating_eps": f"{metrics.analyses.investment_characteristics.earnings_analysis.growth_rate_percent_operating_eps:.2f}%" if metrics.analyses.investment_characteristics.earnings_analysis.growth_rate_percent_operating_eps else None,
                        "quality_percent": f"{metrics.analyses.investment_characteristics.earnings_analysis.quality_percent:.2f}%" if metrics.analyses.investment_characteristics.earnings_analysis.quality_percent else None
                    },
                    "use_of_earnings_analysis": {
                        "avg_dividend_payout_percent": f"{metrics.analyses.investment_characteristics.use_of_earnings_analysis.avg_dividend_payout_percent:.2f}%" if metrics.analyses.investment_characteristics.use_of_earnings_analysis.avg_dividend_payout_percent else None,
                        "avg_stock_buyback_percent": f"{metrics.analyses.investment_characteristics.use_of_earnings_analysis.avg_stock_buyback_percent:.2f}%" if metrics.analyses.investment_characteristics.use_of_earnings_analysis.avg_stock_buyback_percent else None
                    },
                    "sales_analysis": {
                        "growth_rate_percent_revenues": f"{metrics.analyses.investment_characteristics.sales_analysis.growth_rate_percent_revenues:.2f}%" if metrics.analyses.investment_characteristics.sales_analysis.growth_rate_percent_revenues else None,
                        "growth_rate_percent_sales_per_share": f"{metrics.analyses.investment_characteristics.sales_analysis.growth_rate_percent_sales_per_share:.2f}%" if metrics.analyses.investment_characteristics.sales_analysis.growth_rate_percent_sales_per_share else None
                    },
                    "sales_analysis_last_5_years": {
                        "growth_rate_percent_revenues": f"{metrics.analyses.investment_characteristics.sales_analysis_last_5_years.growth_rate_percent_revenues:.2f}%" if metrics.analyses.investment_characteristics.sales_analysis_last_5_years.growth_rate_percent_revenues else None,
                        "growth_rate_percent_sales_per_share": f"{metrics.analyses.investment_characteristics.sales_analysis_last_5_years.growth_rate_percent_sales_per_share:.2f}%" if metrics.analyses.investment_characteristics.sales_analysis_last_5_years.growth_rate_percent_sales_per_share else None
                    }
                },
                "data": {
                    year: {
                        "revenues": f"{data.revenues:.0f}" if data.revenues else "0",
                        "sales_per_share": f"{data.sales_per_share:.2f}" if data.sales_per_share else "0.00",
                        "op_margin_percent": f"{data.operating_margin_pct:.2f}%" if data.operating_margin_pct else None,
                        "tax_rate": f"{data.tax_rate:.2f}%" if data.tax_rate else None,
                        "depreciation": f"{data.depreciation:.0f}" if data.depreciation else "0",
                        "depreciation_percent": f"{data.depreciation_pct:.2f}%" if data.depreciation_pct else None
                    } for year, data in metrics.analyses.data.items()
                }
            },
            "profit_description": {
                "profit_description_characteristics": {
                    "cagr_revenues_percent": f"{profit_description_char.get('cagr_revenues_percent'):.2f}%" if profit_description_char.get('cagr_revenues_percent') else None,
                    "cagr_total_expenses_percent": f"{profit_description_char.get('cagr_total_expenses_percent'):.2f}%" if profit_description_char.get('cagr_total_expenses_percent') else None,
                    "cagr_ebitda_percent": f"{profit_description_char.get('cagr_ebitda_percent'):.2f}%" if profit_description_char.get('cagr_ebitda_percent') else None,
                    "cagr_free_cash_flow_percent": f"{profit_description_char.get('cagr_free_cash_flow_percent'):.2f}%" if profit_description_char.get('cagr_free_cash_flow_percent') else None,
                    "cagr_operating_earnings_percent": f"{profit_description_char.get('cagr_operating_earnings_percent'):.2f}%" if profit_description_char.get('cagr_operating_earnings_percent') else None,
                    "cagr_total_external_costs_percent": f"{profit_description_char.get('cagr_total_external_costs_percent'):.2f}%" if profit_description_char.get('cagr_total_external_costs_percent') else None,
                    "cagr_earnings_percent": f"{profit_description_char.get('cagr_earnings_percent'):.2f}%" if profit_description_char.get('cagr_earnings_percent') else None,
                    "cagr_cost_of_revenue_percent": f"{profit_description_char.get('cagr_cost_of_revenue_percent'):.2f}%" if profit_description_char.get('cagr_cost_of_revenue_percent') else None,
                    "cagr_research_and_development_percent": f"{profit_description_char.get('cagr_research_and_development_percent'):.2f}%" if profit_description_char.get('cagr_research_and_development_percent') else None,
                    "cagr_selling_marketing_general_admin_percent": f"{profit_description_char.get('cagr_selling_marketing_general_admin_percent'):.2f}%" if profit_description_char.get('cagr_selling_marketing_general_admin_percent') else None,
                    "cagr_external_costs_breakdown_percent": profit_description_char.get("cagr_external_costs_breakdown_percent")
                },
                "data": {
                    year: {
                        "revenues": {
                            "total_revenues": data.revenues,
                            "breakdown": revenue_segmentation.get(int(year), {})
                        },
                        "expenses": {
                            "total_expenses": data.expenses.get("total_expenses", "0.00"),
                            "breakdown": data.expenses.get("breakdown", {})
                        },
                        "ebitda": data.ebitda,
                        "amortization_depreciation": data.amortization_depreciation,
                        "free_cash_flow": data.free_cash_flow,
                        "capex": data.capex,
                        "operating_earnings": data.operating_earnings,
                        "operating_earnings_percent_revenue": data.operating_earnings_percent_revenue,
                        "external_costs": {
                            "total_external_costs": data.external_costs.get("total_external_costs", "0.00"),
                            "breakdown": data.external_costs.get("breakdown", {})
                        },
                        "earnings": data.earnings,
                        "earnings_percent_revenue": data.earnings_percent_revenue,
                        "dividend_paid": data.dividend_paid,
                        "dividend_paid_pct_fcf": data.dividend_paid_pct_fcf,
                        "share_buybacks_from_stmt_cf": data.share_buybacks_from_stmt_cf,
                        "net_biz_acquisition": data.net_biz_acquisition
                    } for year, data in metrics.profit_description.data.items()
                }
            },
            "balance_sheet": {
                "balance_sheet_characteristics": {
                    "cagr_total_assets_percent": f"{metrics.balance_sheet.balance_sheet_characteristics.cagr_total_assets_percent:.2f}%" if metrics.balance_sheet.balance_sheet_characteristics.cagr_total_assets_percent else None,
                    "cagr_total_liabilities_percent": f"{metrics.balance_sheet.balance_sheet_characteristics.cagr_total_liabilities_percent:.2f}%" if metrics.balance_sheet.balance_sheet_characteristics.cagr_total_liabilities_percent else None,
                    "cagr_total_shareholders_equity_percent": f"{metrics.balance_sheet.balance_sheet_characteristics.cagr_total_shareholders_equity_percent:.2f}%" if metrics.balance_sheet.balance_sheet_characteristics.cagr_total_shareholders_equity_percent else None
                },
                "data": {
                    year: {
                        "assets": {
                            "total_assets": f"{bs_data.total_assets:.2f}" if bs_data.total_assets else "0.00",
                            "breakdown": {
                                "cash_and_cash_equivalents": f"{bs_data.assets_breakdown.cash_and_cash_equivalents:.2f}" if bs_data.assets_breakdown.cash_and_cash_equivalents else "0.00",
                                "short_term_investment": f"{bs_data.assets_breakdown.short_term_investment:.2f}" if bs_data.assets_breakdown.short_term_investment else "0.00",
                                "accounts_receivable_net": f"{bs_data.assets_breakdown.accounts_receivable_net:.2f}" if bs_data.assets_breakdown.accounts_receivable_net else "0.00",
                                "other_current_assets": f"{bs_data.assets_breakdown.other_current_assets:.2f}" if bs_data.assets_breakdown.other_current_assets else "0.00",
                                "land_property_equipment_net": f"{bs_data.assets_breakdown.land_property_equipment_net:.2f}" if bs_data.assets_breakdown.land_property_equipment_net else "0.00",
                                "goodwill_and_intangible_assets": f"{bs_data.assets_breakdown.goodwill_and_intangible_assets:.2f}" if bs_data.assets_breakdown.goodwill_and_intangible_assets else "0.00",
                                "other_non_current": f"{bs_data.assets_breakdown.other_non_current:.2f}" if bs_data.assets_breakdown.other_non_current else "0.00",
                                "long_term_equity_investment": f"{bs_data.assets_breakdown.long_term_equity_investment:.2f}" if bs_data.assets_breakdown.long_term_equity_investment else "0.00",
                            }
                        },
                        "liabilities": {
                            "total_liabilities": f"{bs_data.total_liabilities:.2f}" if bs_data.total_liabilities else "0.00",
                            "breakdown": {
                                "accounts_payable": f"{bs_data.liabilities_breakdown.accounts_payable:.2f}" if bs_data.liabilities_breakdown.accounts_payable else "0.00",
                                "tax_payables": f"{bs_data.liabilities_breakdown.tax_payables:.2f}" if bs_data.liabilities_breakdown.tax_payables else "0.00",
                                "other_current_liabilities": f"{bs_data.liabilities_breakdown.other_current_liabilities:.2f}" if bs_data.liabilities_breakdown.other_current_liabilities else "0.00",
                                "deferred_revenue": f"{bs_data.liabilities_breakdown.deferred_revenue:.2f}" if bs_data.liabilities_breakdown.deferred_revenue else "0.00",
                                "short_term_debt": f"{bs_data.liabilities_breakdown.short_term_debt:.2f}" if bs_data.liabilities_breakdown.short_term_debt else "0.00",
                                "long_term_debt_minus_capital_lease_obligation": f"{bs_data.liabilities_breakdown.long_term_debt_minus_capital_lease_obligation:.2f}" if bs_data.liabilities_breakdown.long_term_debt_minus_capital_lease_obligation else "0.00",
                                "other_non_current_liabilities": f"{bs_data.liabilities_breakdown.other_non_current_liabilities:.2f}" if bs_data.liabilities_breakdown.other_non_current_liabilities else "0.00",
                                "capital_lease_obligations": f"{bs_data.liabilities_breakdown.capital_lease_obligations:.2f}" if bs_data.liabilities_breakdown.capital_lease_obligations else "0.00",
                            }
                        },
                        "shareholders_equity": {
                            "total_shareholders_equity": f"{bs_data.total_shareholders_equity:.2f}" if bs_data.total_shareholders_equity else "0.00",
                            "breakdown": {
                                "common_stock": f"{bs_data.shareholders_equity_breakdown.common_stock:.2f}" if bs_data.shareholders_equity_breakdown.common_stock else "0.00",
                                "additional_paid_in_capital": f"{bs_data.shareholders_equity_breakdown.additional_paid_in_capital:.2f}" if bs_data.shareholders_equity_breakdown.additional_paid_in_capital else "0.00",
                                "retained_earnings": f"{bs_data.shareholders_equity_breakdown.retained_earnings:.2f}" if bs_data.shareholders_equity_breakdown.retained_earnings else "0.00",
                                "accumulated_other_comprehensive_income_loss": f"{bs_data.shareholders_equity_breakdown.accum_other_comprehensive_income_loss:.2f}" if bs_data.shareholders_equity_breakdown.accum_other_comprehensive_income_loss else "0.00",
                            }
                        }
                    } for year, bs_data in metrics.balance_sheet.data.items()
                }
            },
            "studies": {
                "analysis_of_debt_levels": {
                    "total_debt_capital": {
                        "total_debt": f"{metrics.studies.analysis_of_debt_levels.total_debt_capital.total_debt:.2f}" if metrics.studies.analysis_of_debt_levels.total_debt_capital.total_debt else "0.00",
                        "total_capital": f"{metrics.studies.analysis_of_debt_levels.total_debt_capital.total_capital:.2f}" if metrics.studies.analysis_of_debt_levels.total_debt_capital.total_capital else "0.00",
                        "total_debt_ratio": f"{metrics.studies.analysis_of_debt_levels.total_debt_capital.total_debt_ratio:.2f}%" if metrics.studies.analysis_of_debt_levels.total_debt_capital.total_debt_ratio else None
                    },
                    "long_term_debt": {
                        "lt_debt": f"{metrics.studies.analysis_of_debt_levels.long_term_debt.lt_debt:.2f}" if metrics.studies.analysis_of_debt_levels.long_term_debt.lt_debt else "0.00",
                        "lt_capital": f"{metrics.studies.analysis_of_debt_levels.long_term_debt.lt_capital:.2f}" if metrics.studies.analysis_of_debt_levels.long_term_debt.lt_capital else "0.00",
                        "lt_debt_ratio": f"{metrics.studies.analysis_of_debt_levels.long_term_debt.lt_debt_ratio:.2f}%" if metrics.studies.analysis_of_debt_levels.long_term_debt.lt_debt_ratio else None
                    },
                    "net_income_payback": {
                        "total_debt": f"{metrics.studies.analysis_of_debt_levels.net_income_payback.total_debt:.2f}" if metrics.studies.analysis_of_debt_levels.net_income_payback.total_debt else "0.00",
                        "net_income": f"{metrics.studies.analysis_of_debt_levels.net_income_payback.net_income:.2f}" if metrics.studies.analysis_of_debt_levels.net_income_payback.net_income else "0.00",
                        "years_payback_total_debt": f"{metrics.studies.analysis_of_debt_levels.net_income_payback.years_payback_total_debt:.2f}" if metrics.studies.analysis_of_debt_levels.net_income_payback.years_payback_total_debt else None,
                        "lt_debt": f"{metrics.studies.analysis_of_debt_levels.net_income_payback.lt_debt:.2f}" if metrics.studies.analysis_of_debt_levels.net_income_payback.lt_debt else "0.00",
                        "years_payback_lt_debt": f"{metrics.studies.analysis_of_debt_levels.net_income_payback.years_payback_lt_debt:.2f}" if metrics.studies.analysis_of_debt_levels.net_income_payback.years_payback_lt_debt else None
                    },
                    "addback_net_inc_payback": {
                        "lt_debt": f"{metrics.studies.analysis_of_debt_levels.addback_net_inc_payback.lt_debt:.2f}" if metrics.studies.analysis_of_debt_levels.addback_net_inc_payback.lt_debt else "0.00",
                        "net_income": f"{metrics.studies.analysis_of_debt_levels.addback_net_inc_payback.net_income:.2f}" if metrics.studies.analysis_of_debt_levels.addback_net_inc_payback.net_income else "0.00",
                        "addback": f"{metrics.studies.analysis_of_debt_levels.addback_net_inc_payback.addback:.2f}" if metrics.studies.analysis_of_debt_levels.addback_net_inc_payback.addback else "0.00",
                        "years_payback": f"{metrics.studies.analysis_of_debt_levels.addback_net_inc_payback.years_payback:.2f}" if metrics.studies.analysis_of_debt_levels.addback_net_inc_payback.years_payback else None
                    }
                }
            }
        }

        logger.debug("Formatted data to JSON structure.")
        return final_output
