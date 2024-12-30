# src/utils/calculations.py

import logging
from typing import List, Tuple, Optional
import pandas as pd
from datetime import datetime

# Configure a logger for this module
logger = logging.getLogger(__name__)

def calculate_cagr(values_by_year: List[Tuple[int, float]], verbose: bool = False) -> Optional[float]:
    """
    Calculate Compound Annual Growth Rate (CAGR) from a list of (year, value) tuples.

    Args:
        values_by_year: List of (year, value) tuples, sorted by year ascending
        verbose: If True, log information about adjustments

    Returns:
        CAGR as a decimal (e.g., 0.0742 for 7.42% growth), or None if not calculable
    """
    if len(values_by_year) < 2:
        logger.debug("Insufficient data points to calculate CAGR.")
        return None

    years = [y for (y, v) in values_by_year]
    vals = [v for (y, v) in values_by_year]

    begin_value = vals[0]
    end_value = vals[-1]
    periods = years[-1] - years[0]

    if periods <= 0:
        logger.debug(f"Invalid periods for CAGR calculation: {periods}")
        return None

    idx = 0
    adjusted = False
    while idx < len(vals) and (vals[idx] is None or vals[idx] <= 0):
        idx += 1

    if idx >= len(vals):
        if verbose:
            logger.warning("No positive start value found for CAGR calculation.")
        return None

    if idx > 0:
        begin_value = vals[idx]
        end_value = vals[-1]
        periods = years[-1] - years[idx]
        adjusted = True

    if adjusted and verbose:
        logger.info(f"Start was adjusted for CAGR calculation from year {years[0]} to {years[idx]}")

    if begin_value <= 0 or end_value <= 0 or periods <= 0:
        logger.debug(f"Invalid values after adjustment: begin_value={begin_value}, end_value={end_value}, periods={periods}")
        return None

    try:
        cagr = (end_value / begin_value) ** (1 / periods) - 1
        logger.debug(f"Calculated CAGR: {cagr:.4f} ({cagr * 100:.2f}%)")
        return cagr
    except Exception as e:
        logger.error(f"Error calculating CAGR: {e}")
        return None

def derive_fiscal_year(fiscal_year_end: str) -> int:
    """
    Determine the most recent completed fiscal year given fiscal year end date.

    Args:
        fiscal_year_end: Date string in format "MM-DD"

    Returns:
        Integer representing the most recent completed fiscal year
    """
    if not fiscal_year_end:
        derived_year = datetime.now().year - 1
        logger.debug(f"Fiscal year end not provided. Derived fiscal year: {derived_year}")
        return derived_year

    try:
        month, day = map(int, fiscal_year_end.split("-"))
        today = datetime.now()

        # If today's date is past the fiscal year end, use current year
        # Otherwise use previous year
        if (today.month > month) or (today.month == month and today.day >= day):
            derived_year = today.year
        else:
            derived_year = today.year - 1

        logger.debug(f"Fiscal year end: {fiscal_year_end}. Derived fiscal year: {derived_year}")
        return derived_year
    except Exception as e:
        derived_year = datetime.now().year - 1
        logger.error(f"Invalid fiscal year end format '{fiscal_year_end}': {e}. Derived fiscal year: {derived_year}")
        return derived_year

class DataValidator:
    """Utility class for validating financial data."""

    @staticmethod
    def validate_series(series: pd.Series) -> bool:
        """Check if a series contains valid numerical data."""
        if series.isna().all():
            logger.debug("Series validation failed: All values are NaN.")
            return False
        if (series == 0).all():
            logger.debug("Series validation failed: All values are zero.")
            return False
        logger.debug("Series validation passed.")
        return True

    @staticmethod
    def validate_financial_statement(statement: dict, required_fields: List[str]) -> bool:
        """Validate that a financial statement contains required fields."""
        missing_fields = [field for field in required_fields if field not in statement]
        if missing_fields:
            logger.debug(f"Financial statement validation failed: Missing fields {missing_fields}.")
            return False
        logger.debug("Financial statement validation passed.")
        return True
