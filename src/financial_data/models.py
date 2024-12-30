# src/financial_data/models.py
from dataclasses import dataclass
from typing import Dict, Optional, List

@dataclass
class FinancialStatement:
    date: str
    data: Dict[str, float]

@dataclass
class CompanyProfile:
    symbol: str
    company_name: str
    exchange: str
    description: str
    market_cap: float
    sector: str
    subsector: str
    fiscal_year_end: str

@dataclass
class YearMetrics:
    net_profit: Optional[float] = None
    diluted_eps: Optional[float] = None
    operating_eps: Optional[float] = None
    revenues: Optional[float] = None
    expenses: Optional[float] = None
    ebitda: Optional[float] = None
    operating_margin: Optional[float] = None
    # Add other metrics as needed
