from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class CompanyProfile:
    symbol: str
    company_name: str
    exchange: str
    description: str
    sector: str
    industry: str

@dataclass
class FinancialData:
    net_profit: Optional[float] = None
    diluted_eps: Optional[float] = None
    operating_eps: Optional[float] = None
    pe_ratio: Optional[float] = None
    price_low: Optional[float] = None
    price_high: Optional[float] = None
    dividends_paid: Optional[float] = None
    dividends_per_share: Optional[float] = None
    avg_dividend_yield: Optional[float] = None
    shares_outstanding: Optional[float] = None
    buyback: Optional[float] = None
    share_equity: Optional[float] = None
    book_value_per_share: Optional[float] = None
    long_term_debt: Optional[float] = None
    roe: Optional[float] = None
    roc: Optional[float] = None

@dataclass
class CompanyDescription:
    fiscal_year_end: str  
    stock_price: float
    market_cap: int
    yoy_financial_data: Dict[str, FinancialData] = field(default_factory=dict)

@dataclass
class InvestmentCharacteristics:
    growth_rate_percent_operating_eps: Optional[float] = None
    quality_percent: Optional[float] = None

@dataclass
class UseOfEarningsAnalysis:
    avg_dividend_payout_percent: Optional[float] = None
    avg_stock_buyback_percent: Optional[float] = None

@dataclass
class SalesAnalysis:
    growth_rate_percent_revenues: Optional[float] = None
    growth_rate_percent_sales_per_share: Optional[float] = None

@dataclass
class InvestmentCharacteristicsSection:
    earnings_analysis: Optional[InvestmentCharacteristics] = None
    use_of_earnings_analysis: Optional[UseOfEarningsAnalysis] = None
    sales_analysis: Optional[SalesAnalysis] = None
    sales_analysis_last_5_years: Optional[SalesAnalysis] = None

@dataclass
class AnalysesYoYData:
    revenues: Optional[float]
    sales_per_share: Optional[float]
    operating_margin_pct: Optional[float]
    tax_rate: Optional[float]
    depreciation: Optional[float]
    depreciation_pct: Optional[float]

@dataclass
class Analyses:
    investment_characteristics: Optional[InvestmentCharacteristicsSection] = None
    data: Dict[str, AnalysesYoYData] = field(default_factory=dict)

@dataclass
class ExpensesBreakdown:
    cost_of_revenue: Optional[float] = None
    research_and_development: Optional[float] = None
    selling_marketing_general_admin: Optional[float] = None

@dataclass
class ExternalCostBreakdown:
    income_taxes: Optional[float] = None
    interest_and_other_income: Optional[float] = None

@dataclass
class ProfitDescriptionData:
    total_revenues: Optional[float] = None
    revenue_breakdown: Dict[str, float] = field(default_factory=dict)
    total_expenses: Optional[float] = None
    expenses_breakdown: ExpensesBreakdown = field(default_factory=ExpensesBreakdown)
    ebitda: Optional[float] = None
    amortization_depreciation: Optional[float] = None
    free_cash_flow: Optional[float] = None
    capex: Optional[float] = None
    operating_earnings: Optional[float] = None
    operating_earnings_percent_revenue: Optional[str] = None
    total_external_costs: Optional[float] = None
    external_cost_breakdown: ExternalCostBreakdown = field(default_factory=ExternalCostBreakdown)
    earnings: Optional[float] = None
    earnings_percent_revenue: Optional[str] = None
    dividend_paid: Optional[str] = None
    dividend_paid_pct_fcf: Optional[float] = None
    share_buybacks_from_stmt_cf: Optional[float] = None
    net_biz_acquisition: Optional[float] = None

@dataclass
class ProfitDescriptionCharacteristics:
    cagr_external_costs_income_taxes_percent: Optional[float] = None
    cagr_external_costs_interest_and_other_income_percent: Optional[float] = None
    cagr_revenues_breakdown_percent: Dict[str, Optional[float]] = field(default_factory=dict)
    cagr_revenues_percent: Optional[float] = None
    cagr_total_expenses_percent: Optional[float] = None
    cagr_ebitda_percent: Optional[float] = None
    cagr_free_cash_flow_percent: Optional[float] = None
    cagr_operating_earnings_percent: Optional[float] = None
    cagr_total_external_costs_percent: Optional[float] = None
    cagr_earnings_percent: Optional[float] = None
    cagr_cost_of_revenue_percent: Optional[float] = None
    cagr_research_and_development_percent: Optional[float] = None
    cagr_selling_marketing_general_admin_percent: Optional[float] = None

@dataclass
class ProfitDescription:
    profit_description_characteristics: Optional[ProfitDescriptionCharacteristics] = None
    data: Dict[str, ProfitDescriptionData] = field(default_factory=dict)

@dataclass
class AssetsBreakdown:
    cash_and_cash_equivalents: Optional[float] = None
    short_term_investment: Optional[float] = None
    accounts_receivable_net: Optional[float] = None
    other_current_assets: Optional[float] = None
    land_property_equipment_net: Optional[float] = None
    goodwill_and_intangible_assets: Optional[float] = None
    other_non_current: Optional[float] = None
    long_term_equity_investment: Optional[float] = None

@dataclass
class LiabilitiesBreakdown:
    accounts_payable: Optional[float] = None
    tax_payables: Optional[float] = None
    other_current_liabilities: Optional[float] = None
    deferred_revenue: Optional[float] = None
    short_term_debt: Optional[float] = None
    long_term_debt_minus_capital_lease_obligation: Optional[float] = None
    other_non_current_liabilities: Optional[float] = None
    capital_lease_obligations: Optional[float] = None

@dataclass
class ShareholdersEquityBreakdown:
    common_stock: Optional[float] = None
    additional_paid_in_capital: Optional[float] = None
    retained_earnings: Optional[float] = None
    accum_other_comprehensive_income_loss: Optional[float] = None

@dataclass
class BalanceSheetData:
    total_assets: Optional[float] = None
    assets_breakdown: AssetsBreakdown = field(default_factory=AssetsBreakdown)
    total_liabilities: Optional[float] = None
    liabilities_breakdown: LiabilitiesBreakdown = field(default_factory=LiabilitiesBreakdown)
    total_shareholders_equity: Optional[float] = None
    shareholders_equity_breakdown: ShareholdersEquityBreakdown = field(default_factory=ShareholdersEquityBreakdown)

@dataclass
class BalanceSheetCharacteristics:
    cagr_total_assets_percent: Optional[float] = None
    cagr_total_liabilities_percent: Optional[float] = None
    cagr_total_shareholders_equity_percent: Optional[float] = None

@dataclass
class BalanceSheet:
    balance_sheet_characteristics: Optional[BalanceSheetCharacteristics] = None
    data: Dict[str, BalanceSheetData] = field(default_factory=dict)

@dataclass
class AnalysisOfDebtLevels:
    total_debt: Optional[float] = None
    total_capital: Optional[float] = None
    total_debt_ratio: Optional[float] = None
    lt_debt: Optional[float] = None
    net_income: Optional[float] = None
    lt_capital: Optional[float] = None
    lt_debt_ratio: Optional[float] = None
    years_payback_total_debt: Optional[float] = None
    years_payback_lt_debt: Optional[float] = None
    addback: Optional[float] = None
    years_payback: Optional[float] = None

@dataclass
class Studies:
    total_debt_capital: AnalysisOfDebtLevels = field(default_factory=AnalysisOfDebtLevels)
    long_term_debt: AnalysisOfDebtLevels = field(default_factory=AnalysisOfDebtLevels)
    net_income_payback: AnalysisOfDebtLevels = field(default_factory=AnalysisOfDebtLevels)
    addback_net_inc_payback: AnalysisOfDebtLevels = field(default_factory=AnalysisOfDebtLevels)

@dataclass
class Metrics:
    company_profile: CompanyProfile
    company_description: CompanyDescription
    analyses: Analyses
    profit_description: ProfitDescription
    balance_sheet: BalanceSheet
    studies: Studies