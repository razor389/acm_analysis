# src/financial_data/fmp_client.py

import requests
import logging
from typing import Dict, List, Optional
from ..models import CompanyProfile

logger = logging.getLogger(__name__)

class FMPError(Exception):
    """Base exception for FMP API errors."""
    pass

class FMPClient:
    """Client for Financial Modeling Prep API."""
    
    def __init__(self, api_key: str, base_url: str = "https://financialmodelingprep.com/api/v3"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        logger.debug(f"FMPClient initialized with base_url={self.base_url}")

    def _get(self, endpoint: str, params: Optional[Dict] = None, base_url: Optional[str] = None) -> Dict:
        """Make GET request to FMP API."""
        if params is None:
            params = {}
        params["apikey"] = self.api_key
        
        # Use the overridden base_url if provided, else default to self.base_url
        final_base_url = base_url if base_url else self.base_url
        url = f"{final_base_url}/{endpoint}"
        logger.debug(f"Requesting {url} with params={params}")
        
        try:
            response = self.session.get(url, params=params)
            logger.debug(f"Response status code: {response.status_code}")
            response.raise_for_status()
            json_data = response.json()
            logger.debug(f"Response JSON (truncated): {str(json_data)[:200]}...")
            return json_data
        except requests.exceptions.RequestException as e:
            logger.exception(f"FMP API request failed for endpoint {endpoint}")
            raise FMPError(f"FMP API request failed: {str(e)}")

    def get_company_profile(self, symbol: str) -> CompanyProfile:
        """Fetch company profile."""
        logger.info(f"Fetching company profile for '{symbol}'")
        data = self._get(f"profile/{symbol}")
        if not data or not isinstance(data, list):
            raise FMPError(f"Invalid profile data for {symbol}")
        
        profile = data[0]
        return CompanyProfile(
            symbol=profile.get("symbol"),
            company_name=profile.get("companyName"),
            exchange=profile.get("exchange"),
            description=profile.get("description"),
            sector=profile.get("sector"),
            industry=profile.get("industry")
        )

    def get_income_statement(self, symbol: str, period: str = "annual") -> List[Dict]:
        """Fetch income statements."""
        logger.info(f"Fetching income statements for '{symbol}', period={period}")
        return self._get(f"income-statement/{symbol}", {"period": period})

    def get_balance_sheet(self, symbol: str, period: str = "annual") -> List[Dict]:
        """Fetch balance sheet statements."""
        logger.info(f"Fetching balance sheet for '{symbol}', period={period}")
        return self._get(f"balance-sheet-statement/{symbol}", {"period": period})

    def get_balance_sheet_as_reported(self, symbol: str, period: str = "annual") -> List[Dict]:
        """Fetch balance sheet as reported."""
        logger.info(f"Fetching balance sheet as reported for '{symbol}', period={period}")
        return self._get(f"balance-sheet-statement-as-reported/{symbol}", {"period": period})

    def get_cash_flow_statement(self, symbol: str, period: str = "annual") -> List[Dict]:
        """Fetch cash flow statements."""
        logger.info(f"Fetching cash flow statements for '{symbol}', period={period}")
        return self._get(f"cash-flow-statement/{symbol}", {"period": period})

    def get_key_metrics(self, symbol: str) -> List[Dict]:
        """Fetch key metrics."""
        logger.info(f"Fetching key metrics for '{symbol}'")
        return self._get(f"key-metrics/{symbol}")

    def get_revenue_segmentation(self, symbol: str) -> Dict[int, Dict[str, float]]:
        """Fetch revenue segmentation."""
        logger.info(f"Fetching revenue segmentation for '{symbol}'")
        endpoint = "revenue-product-segmentation"
        base_url_v4 = "https://financialmodelingprep.com/api/v4"
        
        params = {
            "symbol": symbol,
            "structure": "flat",
            "period": "annual"
        }
        
        data = self._get(endpoint, params=params, base_url=base_url_v4)
        
        result = {}
        for entry in data:
            for date_str, segments in entry.items():
                if date_str and segments:
                    try:
                        year = int(date_str.split('-')[0])
                        if isinstance(segments, dict):
                            result[year] = segments
                    except ValueError:
                        logger.warning(f"Invalid date format: {date_str}")
                        continue
        return result

    def get_fiscal_year_end(self, symbol: str) -> Optional[str]:
        """Fetch fiscal year end from company core information."""
        logger.debug(f"Fetching fiscalYearEnd for '{symbol}' from /v4/company-core-information")
        endpoint = "company-core-information"
        base_url_v4 = "https://financialmodelingprep.com/api/v4"
        params = {"symbol": symbol}
        return self._get_fiscal_year_end(symbol, base_url_v4, endpoint, params)
    
    def _get_fiscal_year_end(self, symbol: str, base_url: str, endpoint: str, params: Dict) -> Optional[str]:
        """Helper method to fetch fiscal year end."""
        try:
            data = self._get(endpoint, params=params, base_url=base_url)
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("fiscalYearEnd")
            return None
        except FMPError as e:
            logger.error(f"Error fetching fiscalYearEnd for {symbol}: {e}")
            return None

    def get_quote_short(self, symbol: str) -> Optional[float]:
        """Fetch short quote price."""
        logger.debug(f"Fetching short quote for '{symbol}'")
        try:
            data = self._get(f"quote-short/{symbol}")
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("price")
        except FMPError:
            pass
        return None
