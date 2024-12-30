# src/financial_data/transformer.py

def transform_final_output(raw_output: dict, stock_price=None) -> dict:
    """
    Convert the raw final_output from `FinancialDataProcessor` into the multi-level JSON
    structure that your old script used to produce.
    """

    # 1) Basic metadata: This becomes your "summary" section.
    # If raw_output doesn't contain some field, .get(...) will just yield None.
    summary_section = {
        "symbol": raw_output.get("symbol"),
        "company_name": raw_output.get("company_name"),
        "exchange": raw_output.get("exchange"),
        "description": raw_output.get("description"),
        "sector": raw_output.get("sector"),
        "subsector": raw_output.get("subsector")
    }

    # 2) The year-by-year data from "data"
    yoy_data = raw_output.get("data", {})
    sorted_years = sorted(yoy_data.keys())

    # Build the 'company_description' block
    company_description_data = {}
    for year in sorted_years:
        metrics = yoy_data[year]

        # Compute a P/E ratio example: average_price / operating_eps (if both exist)
        pe_val = None
        avg_price = metrics.get("average_price")
        op_eps = metrics.get("operating_eps")
        if avg_price is not None and op_eps and op_eps != 0:
            pe_val = avg_price / op_eps

        company_description_data[str(year)] = {
            "net_profit": metrics.get("net_income"),
            "diluted_eps": metrics.get("diluted_eps"),
            "operating_eps": op_eps,
            # Fill in pe_ratio if we computed it:
            "pe_ratio": pe_val,

            "price_low": metrics.get("yearly_low"),
            "price_high": metrics.get("yearly_high"),
            "dividends_paid": metrics.get("dividends_paid"),
            "shares_outstanding": metrics.get("shares_outstanding"),
            "buyback": metrics.get("buyback"),
            "share_equity": metrics.get("shareholder_equity"),
        }

    # If your raw_output includes a known "fiscal_year_end", you can fetch it. Otherwise keep None.
    fiscal_year_end_val = raw_output.get("fiscal_year_end")  # or some other field name
    company_description_section = {
        "fiscal_year_end": fiscal_year_end_val,
        "stock_price": stock_price,  # pass in if you have a current share price
        "marketCapitalization": raw_output.get("marketCapitalization"),
        "data": company_description_data
    }

    # 3) The 'analyses' section
    analyses_data = {}
    for year in sorted_years:
        metrics = yoy_data[year]

        # If you want "sales_per_share": revenues / shares_outstanding (if both present)
        sps_val = None
        rev = metrics.get("revenues")
        sh_out = metrics.get("shares_outstanding")
        if rev and sh_out and sh_out != 0:
            sps_val = rev / sh_out

        # If yoy_data has "provision_for_taxes" & "pretax_income", compute an approximate tax rate
        tax_rate_val = None
        if metrics.get("provision_for_taxes") and metrics.get("pretax_income"):
            pre_tax = metrics["pretax_income"]
            if pre_tax != 0:
                tax_rate_val = metrics["provision_for_taxes"] / pre_tax

        analyses_data[str(year)] = {
            "revenues": rev,
            "sales_per_share": sps_val,
            "op_margin_percent": metrics.get("operating_margin"),
            # Either we computed tax_rate_val, or None:
            "tax_rate": tax_rate_val,
        }

    analyses_section = {
        "investment_characteristics": raw_output.get("investment_characteristics", {}),
        "data": analyses_data
    }

    # 4) The 'profit_description' section
    profit_description_data = {}
    for year in sorted_years:
        metrics = yoy_data[year]

        # Sum cost_of_revenue + R&D + SG&A if all exist
        total_expenses = None
        cor = metrics.get("cost_of_revenue")
        rnd = metrics.get("research_and_development")
        sga = metrics.get("selling_gen_admin")
        if cor is not None and rnd is not None and sga is not None:
            total_expenses = cor + rnd + sga

        profit_description_data[str(year)] = {
            "revenues": {
                "total_revenues": metrics.get("revenues"),
                "breakdown": metrics.get("revenue_breakdown", {})
            },
            "expenses": {
                "total_expenses": total_expenses,
                "breakdown": {
                    "cost_of_revenue": cor,
                    "research_and_development": rnd,
                    "selling_marketing_general_admin": sga
                }
            },
            "ebitda": metrics.get("ebitda"),
            "free_cash_flow": metrics.get("free_cash_flow"),
            "operating_earnings": metrics.get("operating_earnings"),
            "earnings": metrics.get("net_income"),
        }

    profit_description_section = {
        "profit_description_characteristics": raw_output.get("profit_description_characteristics", {}),
        "data": profit_description_data
    }

    # 5) The 'balance_sheet' section
    # If yoy_data actually stores "total_assets", "total_liabilities", etc., fill them in:
    balance_sheet_data = {}
    for year in sorted_years:
        # Example: yoy_data[year].get("total_assets")
        # If you actually store the balance sheet in yoy_data, do something like:
        total_assets = metrics.get("total_assets")
        total_liab = metrics.get("total_liabilities")
        total_equity = metrics.get("shareholder_equity")  # or a separate field

        balance_sheet_data[str(year)] = {
            "assets": {
                "total_assets": total_assets,
                "breakdown": {}
            },
            "liabilities": {
                "total_liabilities": total_liab,
                "breakdown": {}
            },
            "shareholders_equity": {
                "total_shareholders_equity": total_equity,
                "breakdown": {}
            }
        }

    balance_sheet_section = {
        "balance_sheet_characteristics": raw_output.get("balance_sheet_characteristics", {}),
        "data": balance_sheet_data
    }

    # 6) The 'studies' section: placeholders for deeper analysis
    studies_section = {
        "analysis_of_debt_levels": {
            # Example placeholders; fill with logic if you compute them
            "total_debt_capital": {},
            "long_term_debt": {},
        }
    }

    # 7) Combine everything
    final_json = {
        "summary": summary_section,
        "company_description": company_description_section,
        "analyses": analyses_section,
        "profit_description": profit_description_section,
        "balance_sheet": balance_sheet_section,
        "studies": studies_section,
        # "qualities" can hold your forum summary or other notes:
        "qualities": raw_output.get("qualities")
    }

    return final_json
