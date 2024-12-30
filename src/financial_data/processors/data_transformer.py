# src/financial_data/processors/data_transformer.py

import logging
from typing import Dict, List, Optional

from financial_data.models import (
    CompanyProfile,
    FinancialData,
    CompanyDescription,
    Metrics,
    # ... other dataclasses
)

logger = logging.getLogger(__name__)

class DataTransformer:
    """Transforms raw API data into structured dataclass instances."""

    def __init__(self):
        logger.debug("DataTransformer initialized.")

    def transform_company_profile(self, raw_profile: Dict) -> CompanyProfile:
        """Transforms raw company profile data into CompanyProfile dataclass."""
        return CompanyProfile(
            symbol=raw_profile.get("symbol"),
            company_name=raw_profile.get("companyName"),
            exchange=raw_profile.get("exchange"),
            description=raw_profile.get("description"),
            sector=raw_profile.get("sector"),
            industry=raw_profile.get("industry")
        )

    def transform_company_description(self, fiscal_year_end: Optional[str], stock_price: float,
                                     market_cap: int, yoy_financial_data: Dict[str, FinancialData]) -> CompanyDescription:
        """Transforms data into CompanyDescription dataclass."""
        return CompanyDescription(
            fiscal_year_end=fiscal_year_end or "12-31",
            stock_price=stock_price,
            market_cap=market_cap,
            yoy_financial_data=yoy_financial_data
        )

    # Add more transformation methods as needed
