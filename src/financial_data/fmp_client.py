# src/financial_data/fmp_client.py

import requests
from typing import Dict, List, Optional
from .models import CompanyProfile, FinancialStatement

class FMPError(Exception):
    """Base exception for FMP API errors."""
    pass

class FMPClient:
    """Client for Financial Modeling Prep API."""
    
    def __init__(self, api_key: str, base_url: str = "https://financialmodelingprep.com/api/v3"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make GET request to FMP API."""
        if params is None:
            params = {}
        params["apikey"] = self.api_key
        
        try:
            response = self.session.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise FMPError(f"FMP API request failed: {str(e)}")

    def get_company_profile(self, symbol: str) -> CompanyProfile:
        """Fetch company profile."""
        data = self._get(f"profile/{symbol}")
        if not data or not isinstance(data, list):
            raise FMPError(f"Invalid profile data for {symbol}")
        
        profile = data[0]
        return CompanyProfile(
            symbol=profile.get("symbol"),
            company_name=profile.get("companyName"),
            exchange=profile.get("exchange"),
            description=profile.get("description"),
            market_cap=profile.get("mktCap"),
            sector=profile.get("sector"),
            subsector=profile.get("industry"),
            fiscal_year_end=profile.get("fiscalYearEnd")
        )

    def get_financial_statements(self, symbol: str, statement_type: str, period: str = "annual") -> List[Dict]:
        """Fetch financial statements from e.g. /income-statement, /balance-sheet-statement, etc."""
        return self._get(f"{statement_type}/{symbol}", {"period": period})

    def get_key_metrics(self, symbol: str) -> List[Dict]:
        """Fetch key metrics from /key-metrics/<symbol>."""
        return self._get(f"key-metrics/{symbol}")

    def get_revenue_segmentation(self, symbol: str) -> Dict[int, Dict[str, float]]:
        """Fetch revenue segmentation data (v4/revenue-product-segmentation)."""
        endpoint = "v4/revenue-product-segmentation"
        data = self._get(endpoint, {
            "symbol": symbol,
            "structure": "flat",
            "period": "annual"
        })
        
        result = {}
        for entry in data:
            for date_str, segments in entry.items():
                try:
                    year = int(date_str.split('-')[0])
                    if isinstance(segments, dict):
                        result[year] = segments
                except ValueError:
                    continue
        return result

    # *** ADDED ***
    def get_fiscal_year_end(self, symbol: str) -> Optional[str]:
        """
        Fetch the fiscalYearEnd from the company-core-information endpoint.
        e.g. /v4/company-core-information?symbol=<SYMBOL>
        Returns the FYE string like "09-30" or None if not found.
        """
        try:
            # Endpoint differs from self.base_url because it's a /v4
            # but we can override base_url or manually build the full path:
            url = "https://financialmodelingprep.com/api/v4/company-core-information"
            params = {"symbol": symbol, "apikey": self.api_key}
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("fiscalYearEnd")
            return None
        except requests.exceptions.RequestException as e:
            raise FMPError(f"Error fetching fiscalYearEnd for {symbol}: {str(e)}")
    
    # *** ADDED ***
    def get_quote_short(self, symbol: str) -> Optional[float]:
        """
        Fetch the short quote from /quote-short/<symbol> to get current price.
        Returns a float (price) or None if not found.
        """
        try:
            data = self._get(f"quote-short/{symbol}")
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("price")
        except FMPError:
            pass
        return None
