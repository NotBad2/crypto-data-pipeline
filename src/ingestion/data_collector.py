"""
Main data collector orchestrating cryptocurrency data ingestion.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .coingecko_client import CoinGeckoClient
from .data_models import CoinMarketData, GlobalMarketData, PricePoint
from config import current_config

logger = logging.getLogger(__name__)


class CryptoDataCollector:
    """Main class for collecting cryptocurrency data from multiple sources."""
    
    def __init__(self, coingecko_api_key: Optional[str] = None):
        """
        Initialize the crypto data collector.
        
        Args:
            coingecko_api_key: CoinGecko Pro API key (optional)
        """
        self.coingecko_client = CoinGeckoClient(coingecko_api_key)
        self.supported_coins = []
        self.last_collection_time = None
        
        logger.info("CryptoDataCollector initialized")
    
    def test_connections(self) -> Dict[str, bool]:
        """
        Test connections to all data sources.
        
        Returns:
            Dictionary with connection status for each source
        """
        results = {}
        
        # Test CoinGecko
        logger.info("Testing CoinGecko API connection...")
        results['coingecko'] = self.coingecko_client.health_check()
        
        return results
    
    def get_supported_coins(self, refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get list of supported coins from CoinGecko.
        
        Args:
            refresh: Force refresh of the coins list
            
        Returns:
            List of supported coins
        """
        if not self.supported_coins or refresh:
            logger.info("Fetching supported coins list...")
            try:
                self.supported_coins = self.coingecko_client.get_coins_list()
                logger.info(f"Retrieved {len(self.supported_coins)} supported coins")
            except Exception as e:
                logger.error(f"Failed to fetch supported coins: {e}")
                raise
        
        return self.supported_coins
    
    def collect_market_data(self, limit: int = None) -> List[CoinMarketData]:
        """
        Collect current market data for top cryptocurrencies.
        
        Args:
            limit: Maximum number of coins to collect (default from config)
            
        Returns:
            List of CoinMarketData objects
        """
        if limit is None:
            limit = current_config.TOP_CRYPTOCURRENCIES
        
        logger.info(f"Collecting market data for top {limit} cryptocurrencies...")
        
        collected_data = []
        
        try:
            # Calculate number of pages needed (CoinGecko max 250 per page)
            per_page = min(250, limit)
            pages_needed = (limit + per_page - 1) // per_page
            
            for page in range(1, pages_needed + 1):
                # Calculate how many coins to fetch for this page
                remaining_coins = limit - len(collected_data)
                coins_this_page = min(per_page, remaining_coins)
                
                if coins_this_page <= 0:
                    break
                
                logger.info(f"Fetching page {page}/{pages_needed} ({coins_this_page} coins)")
                
                # Fetch market data
                market_data = self.coingecko_client.get_coins_markets(
                    per_page=coins_this_page,
                    page=page
                )
                
                # Convert to data models
                for coin_data in market_data:
                    try:
                        coin_market_data = CoinMarketData.from_coingecko_response(coin_data)
                        collected_data.append(coin_market_data)
                    except Exception as e:
                        logger.error(f"Failed to parse coin data for {coin_data.get('id', 'unknown')}: {e}")
                        continue
                
                logger.info(f"Successfully collected {len(collected_data)} coins so far")
            
            logger.info(f"Market data collection completed. Total coins: {len(collected_data)}")
            self.last_collection_time = datetime.utcnow()
            
            return collected_data
            
        except Exception as e:
            logger.error(f"Failed to collect market data: {e}")
            raise
    
    def collect_global_data(self) -> GlobalMarketData:
        """
        Collect global cryptocurrency market data.
        
        Returns:
            GlobalMarketData object
        """
        logger.info("Collecting global market data...")
        
        try:
            global_data = self.coingecko_client.get_global_data()
            global_market_data = GlobalMarketData.from_coingecko_response(global_data)
            
            logger.info("Global market data collection completed")
            return global_market_data
            
        except Exception as e:
            logger.error(f"Failed to collect global data: {e}")
            raise
    
    def collect_trending_coins(self) -> Dict[str, Any]:
        """
        Collect trending coins data.
        
        Returns:
            Trending coins data
        """
        logger.info("Collecting trending coins data...")
        
        try:
            trending_data = self.coingecko_client.get_trending_coins()
            logger.info("Trending coins data collection completed")
            return trending_data
            
        except Exception as e:
            logger.error(f"Failed to collect trending coins: {e}")
            raise
    
    def collect_historical_prices(self, coin_id: str, days: int = 30) -> List[PricePoint]:
        """
        Collect historical price data for a specific coin.
        
        Args:
            coin_id: Coin identifier
            days: Number of days of historical data
            
        Returns:
            List of PricePoint objects
        """
        logger.info(f"Collecting {days} days of historical data for {coin_id}...")
        
        try:
            # Determine interval based on days
            interval = 'daily' if days > 90 else 'hourly'
            
            chart_data = self.coingecko_client.get_coin_market_chart(
                coin_id=coin_id,
                days=str(days),
                interval=interval
            )
            
            price_points = []
            
            # Parse price data
            prices = chart_data.get('prices', [])
            market_caps = chart_data.get('market_caps', [])
            volumes = chart_data.get('total_volumes', [])
            
            for i, (timestamp_ms, price) in enumerate(prices):
                timestamp = datetime.fromtimestamp(timestamp_ms / 1000)
                
                # Get corresponding market cap and volume if available
                market_cap = market_caps[i][1] if i < len(market_caps) else None
                volume = volumes[i][1] if i < len(volumes) else None
                
                price_point = PricePoint(
                    coin_id=coin_id,
                    timestamp=timestamp,
                    price=price,
                    market_cap=market_cap,
                    volume_24h=volume
                )
                
                price_points.append(price_point)
            
            logger.info(f"Collected {len(price_points)} price points for {coin_id}")
            return price_points
            
        except Exception as e:
            logger.error(f"Failed to collect historical data for {coin_id}: {e}")
            raise
    
    def save_data_to_json(self, data: Any, filename: str, directory: str = "data") -> str:
        """
        Save collected data to JSON file for testing purposes.
        
        Args:
            data: Data to save
            filename: Name of the file
            directory: Directory to save in
            
        Returns:
            Path to saved file
        """
        # Create data directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Add timestamp to filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(directory, f"{timestamp}_{filename}")
        
        try:
            # Convert data to serializable format
            if hasattr(data, 'to_dict'):
                json_data = data.to_dict()
            elif isinstance(data, list):
                json_data = [item.to_dict() if hasattr(item, 'to_dict') else item for item in data]
            else:
                json_data = data
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Data saved to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save data to {filepath}: {e}")
            raise
    
    def run_collection_cycle(self, save_to_files: bool = False) -> Dict[str, Any]:
        """
        Run a complete data collection cycle.
        
        Args:
            save_to_files: Whether to save data to JSON files
            
        Returns:
            Dictionary with collected data
        """
        logger.info("Starting data collection cycle...")
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'market_data': [],
            'global_data': None,
            'trending_data': None
        }
        
        try:
            # Collect market data
            market_data = self.collect_market_data()
            results['market_data'] = market_data
            
            if save_to_files:
                self.save_data_to_json(market_data, 'market_data.json')
            
            # Collect global data
            global_data = self.collect_global_data()
            results['global_data'] = global_data
            
            if save_to_files:
                self.save_data_to_json(global_data, 'global_data.json')
            
            # Collect trending data
            trending_data = self.collect_trending_coins()
            results['trending_data'] = trending_data
            
            if save_to_files:
                self.save_data_to_json(trending_data, 'trending_data.json')
            
            logger.info("Data collection cycle completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Data collection cycle failed: {e}")
            raise
