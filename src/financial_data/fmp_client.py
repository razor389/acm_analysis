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
        """Fetch financial statements."""
        return self._get(f"{statement_type}/{symbol}", {"period": period})

    def get_key_metrics(self, symbol: str) -> List[Dict]:
        """Fetch key metrics."""
        return self._get(f"key-metrics/{symbol}")

    def get_revenue_segmentation(self, symbol: str) -> Dict[int, Dict[str, float]]:
        """Fetch revenue segmentation data."""
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