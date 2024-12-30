# src/utils/calculations.py
from typing import List, Tuple, Optional
import pandas as pd
from datetime import datetime

def calculate_cagr(values_by_year: List[Tuple[int, float]], verbose: bool = False) -> Optional[float]:
    """
    Calculate Compound Annual Growth Rate (CAGR) from a list of (year, value) tuples.
    
    Args:
        values_by_year: List of (year, value) tuples, sorted by year ascending
        verbose: If True, print information about adjustments
    
    Returns:
        CAGR as a decimal (e.g., 0.0742 for 7.42% growth), or None if not calculable
    """
    if len(values_by_year) < 2:
        return None

    years = [y for (y, v) in values_by_year]
    vals = [v for (y, v) in values_by_year]

    begin_value = vals[0]
    end_value = vals[-1]
    periods = years[-1] - years[0]

    if periods <= 0:
        return None

    idx = 0
    adjusted = False
    while idx < len(vals) and (vals[idx] is None or vals[idx] <= 0):
        idx += 1

    if idx >= len(vals):
        if verbose:
            print("No positive start value found for CAGR calculation.")
        return None

    if idx > 0:
        begin_value = vals[idx]
        end_value = vals[-1]
        periods = years[-1] - years[idx]
        adjusted = True

    if adjusted and verbose:
        print(f"Start was adjusted for CAGR calculation from year {years[0]} to {years[idx]}")

    if begin_value <= 0 or end_value <= 0 or periods <= 0:
        return None

    try:
        return (end_value / begin_value) ** (1 / periods) - 1
    except:
        return None

def format_number(value: float, is_percentage: bool = False, use_millions: bool = True) -> str:
    """Format numbers according to standard rules."""
    if value is None:
        return ""
        
    if is_percentage:
        return f"{value * 100:.2f}%"
        
    if use_millions and abs(value) > 100000:
        return f"{int(value / 1_000_000)}"
        
    return f"{value:.2f}"

def derive_fiscal_year(fiscal_year_end: str) -> int:
    """
    Determine the most recent completed fiscal year given fiscal year end date.
    
    Args:
        fiscal_year_end: Date string in format "MM-DD"
    
    Returns:
        Integer representing the most recent completed fiscal year
    """
    if not fiscal_year_end:
        return datetime.now().year - 1

    try:
        month, day = map(int, fiscal_year_end.split("-"))
        today = datetime.now()
        
        # If today's date is past the fiscal year end, use current year
        # Otherwise use previous year
        if (today.month > month) or (today.month == month and today.day >= day):
            return today.year
        else:
            return today.year - 1
    except:
        return datetime.now().year - 1

class DataValidator:
    """Utility class for validating financial data."""
    
    @staticmethod
    def validate_series(series: pd.Series) -> bool:
        """Check if a series contains valid numerical data."""
        return not (series.isna().all() or (series == 0).all())
        
    @staticmethod
    def validate_financial_statement(statement: dict, required_fields: List[str]) -> bool:
        """Validate that a financial statement contains required fields."""
        return all(field in statement for field in required_fields)