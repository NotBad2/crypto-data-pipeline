"""
CoinGecko API client for cryptocurrency data ingestion.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .base_client import BaseAPIClient

logger = logging.getLogger(__name__)


class CoinGeckoClient(BaseAPIClient):
    """Client for CoinGecko API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize CoinGecko API client.
        
        Args:
            api_key: CoinGecko Pro API key (optional for free tier)
        """
        # CoinGecko free tier allows 10-30 calls/minute
        rate_limit = 2.0 if api_key else 6.0  # Pro vs Free tier
        super().__init__(
            base_url="https://api.coingecko.com/api/v3",
            api_key=api_key,
            rate_limit=rate_limit
        )
    
    def _set_auth_headers(self):
        """Set CoinGecko Pro API authentication headers."""
        if self.api_key:
            self.session.headers.update({
                'x-cg-pro-api-key': self.api_key
            })
    
    def get_coins_list(self) -> List[Dict[str, Any]]:
        """
        Get list of all supported coins.
        
        Returns:
            List of coins with id, symbol, and name
        """
        logger.info("Fetching coins list from CoinGecko")
        return self._make_request('coins/list')
    
    def get_coins_markets(self, vs_currency: str = 'usd', 
                         per_page: int = 250, page: int = 1,
                         order: str = 'market_cap_desc') -> List[Dict[str, Any]]:
        """
        Get market data for coins.
        
        Args:
            vs_currency: Target currency (default: usd)
            per_page: Number of results per page (max 250)
            page: Page number
            order: Sort order
            
        Returns:
            List of market data for coins
        """
        params = {
            'vs_currency': vs_currency,
            'per_page': per_page,
            'page': page,
            'order': order,
            'sparkline': True,
            'price_change_percentage': '1h,24h,7d,14d,30d,200d,1y'
        }
        
        logger.info(f"Fetching market data: page {page}, {per_page} coins")
        return self._make_request('coins/markets', params)
    
    def get_coin_by_id(self, coin_id: str, localization: str = 'false',
                      tickers: str = 'true', market_data: str = 'true',
                      community_data: str = 'true', developer_data: str = 'true') -> Dict[str, Any]:
        """
        Get detailed information about a specific coin.
        
        Args:
            coin_id: Coin ID (e.g., 'bitcoin')
            localization: Include localized names
            tickers: Include ticker data
            market_data: Include market data
            community_data: Include community data
            developer_data: Include developer data
            
        Returns:
            Detailed coin information
        """
        params = {
            'localization': localization,
            'tickers': tickers,
            'market_data': market_data,
            'community_data': community_data,
            'developer_data': developer_data
        }
        
        logger.info(f"Fetching detailed data for coin: {coin_id}")
        return self._make_request(f'coins/{coin_id}', params)
    
    def get_coin_history(self, coin_id: str, date: str, 
                        localization: str = 'false') -> Dict[str, Any]:
        """
        Get historical data for a coin on a specific date.
        
        Args:
            coin_id: Coin ID
            date: Date in DD-MM-YYYY format
            localization: Include localized names
            
        Returns:
            Historical data for the specified date
        """
        params = {
            'date': date,
            'localization': localization
        }
        
        logger.info(f"Fetching historical data for {coin_id} on {date}")
        return self._make_request(f'coins/{coin_id}/history', params)
    
    def get_coin_market_chart(self, coin_id: str, vs_currency: str = 'usd',
                             days: str = '1', interval: str = 'hourly') -> Dict[str, Any]:
        """
        Get market chart data (price, market cap, volume) for a coin.
        
        Args:
            coin_id: Coin ID
            vs_currency: Target currency
            days: Number of days (1/7/14/30/90/180/365/max)
            interval: Data interval (daily/hourly)
            
        Returns:
            Market chart data with prices, market caps, and volumes
        """
        params = {
            'vs_currency': vs_currency,
            'days': days,
            'interval': interval
        }
        
        logger.info(f"Fetching market chart for {coin_id}: {days} days")
        return self._make_request(f'coins/{coin_id}/market_chart', params)
    
    def get_global_data(self) -> Dict[str, Any]:
        """
        Get global cryptocurrency data.
        
        Returns:
            Global market data including total market cap, volume, etc.
        """
        logger.info("Fetching global cryptocurrency data")
        return self._make_request('global')
    
    def get_fear_greed_index(self) -> Dict[str, Any]:
        """
        Get Fear & Greed Index data.
        
        Returns:
            Fear & Greed Index data
        """
        logger.info("Fetching Fear & Greed Index")
        # Note: This might require a different endpoint or external API
        # For now, we'll implement a placeholder
        return {'message': 'Fear & Greed Index endpoint to be implemented'}
    
    def get_trending_coins(self) -> Dict[str, Any]:
        """
        Get trending coins data.
        
        Returns:
            List of trending coins
        """
        logger.info("Fetching trending coins")
        return self._make_request('search/trending')
    
    def get_top_gainers_losers(self, vs_currency: str = 'usd') -> Dict[str, Any]:
        """
        Get top gainers and losers.
        
        Args:
            vs_currency: Target currency
            
        Returns:
            Top gainers and losers data
        """
        params = {'vs_currency': vs_currency}
        
        logger.info("Fetching top gainers and losers")
        return self._make_request('coins/top_gainers_losers', params)
    
    def health_check(self) -> bool:
        """
        Check if CoinGecko API is accessible.
        
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            response = self._make_request('ping')
            return response.get('gecko_says') == '(V3) To the Moon!'
        except Exception as e:
            logger.error(f"CoinGecko health check failed: {e}")
            return False
