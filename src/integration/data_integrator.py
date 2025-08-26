"""
Data Integration Module - Connects data ingestion with database storage.
"""

import logging
import sys
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ingestion.data_collector import CryptoDataCollector
from ingestion.data_models import CoinMarketData, GlobalMarketData
from database import DatabaseManager
from config import current_config
import psycopg2
from psycopg2.extras import RealDictCursor
import redis

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataIntegrator:
    """Integrates data collection with database storage."""
    
    def __init__(self):
        """Initialize the data integrator."""
        self.collector = CryptoDataCollector()
        self.redis_client = None
        self._init_connections()
    
    def _init_connections(self):
        """Initialize database connections."""
        try:
            # Initialize Redis for caching
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True
            )
            # Test Redis connection
            self.redis_client.ping()
            logger.info("✅ Redis connection established")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            self.redis_client = None
    
    def get_postgres_connection(self):
        """Get PostgreSQL connection with correct parameters."""
        try:
            conn = psycopg2.connect(
                host='localhost',
                port=5432,
                database='crypto_data',
                user='crypto_user',
                password='crypto_pass',
                cursor_factory=RealDictCursor
            )
            return conn
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {e}")
            return None
    
    def store_market_data(self, market_data: List[CoinMarketData]) -> bool:
        """Store market data in PostgreSQL."""
        if not market_data:
            return False
        
        conn = self.get_postgres_connection()
        if not conn:
            logger.error("Cannot store market data - no database connection")
            return False
        
        try:
            cursor = conn.cursor()
            
            # Insert market data
            insert_query = """
                INSERT INTO raw_data.market_data (
                    coin_id, symbol, name, current_price, market_cap, market_cap_rank,
                    fully_diluted_valuation, total_volume, high_24h, low_24h,
                    price_change_24h, price_change_percentage_24h,
                    price_change_percentage_7d, price_change_percentage_30d,
                    market_cap_change_24h, market_cap_change_percentage_24h,
                    circulating_supply, total_supply, max_supply, ath, ath_change_percentage,
                    ath_date, atl, atl_change_percentage, atl_date, last_updated, collected_at
                ) VALUES (
                    %(coin_id)s, %(symbol)s, %(name)s, %(current_price)s, %(market_cap)s, %(market_cap_rank)s,
                    %(fully_diluted_valuation)s, %(total_volume)s, %(high_24h)s, %(low_24h)s,
                    %(price_change_24h)s, %(price_change_percentage_24h)s,
                    %(price_change_percentage_7d)s, %(price_change_percentage_30d)s,
                    %(market_cap_change_24h)s, %(market_cap_change_percentage_24h)s,
                    %(circulating_supply)s, %(total_supply)s, %(max_supply)s, %(ath)s, %(ath_change_percentage)s,
                    %(ath_date)s, %(atl)s, %(atl_change_percentage)s, %(atl_date)s, %(last_updated)s, %(collected_at)s
                )
                ON CONFLICT (coin_id, collected_at) DO UPDATE SET
                    current_price = EXCLUDED.current_price,
                    market_cap = EXCLUDED.market_cap,
                    total_volume = EXCLUDED.total_volume,
                    price_change_percentage_24h = EXCLUDED.price_change_percentage_24h,
                    last_updated = EXCLUDED.last_updated;
            """
            
            records_inserted = 0
            for coin in market_data:
                data = {
                    'coin_id': coin.coin_id,
                    'symbol': coin.symbol,
                    'name': coin.name,
                    'current_price': coin.current_price,
                    'market_cap': coin.market_cap,
                    'market_cap_rank': coin.market_cap_rank,
                    'fully_diluted_valuation': coin.fully_diluted_valuation,
                    'total_volume': coin.total_volume,
                    'high_24h': coin.high_24h,
                    'low_24h': coin.low_24h,
                    'price_change_24h': coin.price_change_24h,
                    'price_change_percentage_24h': coin.price_change_percentage_24h,
                    'price_change_percentage_7d': coin.price_change_percentage_7d,
                    'price_change_percentage_30d': coin.price_change_percentage_30d,
                    'market_cap_change_24h': coin.market_cap_change_24h,
                    'market_cap_change_percentage_24h': coin.market_cap_change_percentage_24h,
                    'circulating_supply': coin.circulating_supply,
                    'total_supply': coin.total_supply,
                    'max_supply': coin.max_supply,
                    'ath': coin.ath,
                    'ath_change_percentage': coin.ath_change_percentage,
                    'ath_date': coin.ath_date,
                    'atl': coin.atl,
                    'atl_change_percentage': coin.atl_change_percentage,
                    'atl_date': coin.atl_date,
                    'last_updated': coin.last_updated,
                    'collected_at': datetime.now()
                }
                
                cursor.execute(insert_query, data)
                records_inserted += 1
            
            conn.commit()
            logger.info(f"✅ Stored {records_inserted} market data records in PostgreSQL")
            
            # Cache latest data in Redis
            if self.redis_client:
                try:
                    latest_data = [
                        {
                            'coin_id': coin.coin_id,
                            'name': coin.name,
                            'symbol': coin.symbol,
                            'current_price': float(coin.current_price) if coin.current_price else None,
                            'market_cap_rank': coin.market_cap_rank,
                            'price_change_percentage_24h': float(coin.price_change_percentage_24h) if coin.price_change_percentage_24h else None
                        }
                        for coin in market_data[:10]  # Cache top 10
                    ]
                    
                    self.redis_client.setex(
                        'latest_market_data',
                        3600,  # 1 hour expiry
                        json.dumps(latest_data)
                    )
                    logger.info("✅ Cached latest market data in Redis")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to cache in Redis: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store market data: {e}")
            conn.rollback()
            return False
        
        finally:
            cursor.close()
            conn.close()
    
    def store_global_data(self, global_data: GlobalMarketData) -> bool:
        """Store global market data in PostgreSQL."""
        if not global_data:
            return False
        
        conn = self.get_postgres_connection()
        if not conn:
            logger.error("Cannot store global data - no database connection")
            return False
        
        try:
            cursor = conn.cursor()
            
            insert_query = """
                INSERT INTO raw_data.global_market_data (
                    active_cryptocurrencies, upcoming_icos, ongoing_icos, ended_icos,
                    markets, total_market_cap_usd, total_volume_24h_usd,
                    market_cap_percentage_btc, market_cap_percentage_eth,
                    market_cap_change_percentage_24h_usd, bitcoin_dominance,
                    ethereum_dominance, updated_at, collected_at
                ) VALUES (
                    %(active_cryptocurrencies)s, %(upcoming_icos)s, %(ongoing_icos)s, %(ended_icos)s,
                    %(markets)s, %(total_market_cap_usd)s, %(total_volume_24h_usd)s,
                    %(market_cap_percentage_btc)s, %(market_cap_percentage_eth)s,
                    %(market_cap_change_percentage_24h_usd)s, %(bitcoin_dominance)s,
                    %(ethereum_dominance)s, %(updated_at)s, %(collected_at)s
                );
            """
            
            data = {
                'active_cryptocurrencies': global_data.active_cryptocurrencies,
                'upcoming_icos': global_data.upcoming_icos,
                'ongoing_icos': global_data.ongoing_icos,
                'ended_icos': global_data.ended_icos,
                'markets': global_data.markets,
                'total_market_cap_usd': global_data.total_market_cap_usd,
                'total_volume_24h_usd': global_data.total_volume_24h_usd,
                'market_cap_percentage_btc': global_data.market_cap_percentage_btc,
                'market_cap_percentage_eth': global_data.market_cap_percentage_eth,
                'market_cap_change_percentage_24h_usd': global_data.market_cap_change_percentage_24h_usd,
                'bitcoin_dominance': global_data.bitcoin_dominance,
                'ethereum_dominance': global_data.ethereum_dominance,
                'updated_at': global_data.updated_at,
                'collected_at': datetime.now()
            }
            
            cursor.execute(insert_query, data)
            conn.commit()
            
            logger.info("✅ Stored global market data in PostgreSQL")
            
            # Cache global data in Redis
            if self.redis_client:
                try:
                    global_cache = {
                        'total_market_cap_usd': float(global_data.total_market_cap_usd) if global_data.total_market_cap_usd else None,
                        'bitcoin_dominance': float(global_data.bitcoin_dominance) if global_data.bitcoin_dominance else None,
                        'ethereum_dominance': float(global_data.ethereum_dominance) if global_data.ethereum_dominance else None,
                        'active_cryptocurrencies': global_data.active_cryptocurrencies,
                        'collected_at': datetime.now().isoformat()
                    }
                    
                    self.redis_client.setex(
                        'latest_global_data',
                        3600,  # 1 hour expiry
                        json.dumps(global_cache)
                    )
                    logger.info("✅ Cached global data in Redis")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to cache global data in Redis: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store global data: {e}")
            conn.rollback()
            return False
        
        finally:
            cursor.close()
            conn.close()
    
    def collect_and_store_all(self, limit: int = 50) -> Dict[str, Any]:
        """Collect all data and store in databases."""
        logger.info(f"🚀 Starting full data collection and storage (limit: {limit})")
        
        results = {
            'market_data': {'collected': False, 'stored': False, 'count': 0},
            'global_data': {'collected': False, 'stored': False},
            'trending_data': {'collected': False, 'count': 0},
            'errors': []
        }
        
        try:
            # Collect market data
            logger.info("📈 Collecting market data...")
            market_data = self.collector.collect_market_data(limit=limit)
            
            if market_data:
                results['market_data']['collected'] = True
                results['market_data']['count'] = len(market_data)
                logger.info(f"✅ Collected {len(market_data)} market data records")
                
                # Store in database
                if self.store_market_data(market_data):
                    results['market_data']['stored'] = True
                else:
                    results['errors'].append("Failed to store market data")
            else:
                results['errors'].append("Failed to collect market data")
            
            # Wait between requests
            import time
            time.sleep(5)
            
            # Collect global data
            logger.info("🌍 Collecting global market data...")
            global_data = self.collector.collect_global_data()
            
            if global_data:
                results['global_data']['collected'] = True
                logger.info("✅ Collected global market data")
                
                # Store in database
                if self.store_global_data(global_data):
                    results['global_data']['stored'] = True
                else:
                    results['errors'].append("Failed to store global data")
            else:
                results['errors'].append("Failed to collect global data")
            
            # Wait between requests
            time.sleep(5)
            
            # Collect trending data (for analytics)
            logger.info("🔥 Collecting trending data...")
            trending_data = self.collector.collect_trending_coins()
            
            if trending_data and 'coins' in trending_data:
                results['trending_data']['collected'] = True
                results['trending_data']['count'] = len(trending_data['coins'])
                logger.info(f"✅ Collected {len(trending_data['coins'])} trending coins")
                
                # Cache trending data in Redis
                if self.redis_client:
                    try:
                        self.redis_client.setex(
                            'trending_data',
                            1800,  # 30 minutes expiry
                            json.dumps(trending_data)
                        )
                        logger.info("✅ Cached trending data in Redis")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to cache trending data: {e}")
            else:
                results['errors'].append("Failed to collect trending data")
        
        except Exception as e:
            logger.error(f"❌ Data collection and storage failed: {e}")
            results['errors'].append(str(e))
        
        return results
    
    def get_latest_data_from_cache(self) -> Dict[str, Any]:
        """Get latest data from Redis cache."""
        if not self.redis_client:
            return {'error': 'Redis not available'}
        
        try:
            cached_data = {}
            
            # Get market data
            market_data = self.redis_client.get('latest_market_data')
            if market_data:
                cached_data['market_data'] = json.loads(market_data)
            
            # Get global data
            global_data = self.redis_client.get('latest_global_data')
            if global_data:
                cached_data['global_data'] = json.loads(global_data)
            
            # Get trending data
            trending_data = self.redis_client.get('trending_data')
            if trending_data:
                cached_data['trending_data'] = json.loads(trending_data)
            
            return cached_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get cached data: {e}")
            return {'error': str(e)}
    
    def test_connections(self) -> Dict[str, bool]:
        """Test all database connections."""
        results = {}
        
        # Test PostgreSQL
        conn = self.get_postgres_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                results['postgresql'] = True
                cursor.close()
                conn.close()
                logger.info("✅ PostgreSQL connection successful")
            except Exception as e:
                results['postgresql'] = False
                logger.error(f"❌ PostgreSQL test failed: {e}")
        else:
            results['postgresql'] = False
        
        # Test Redis
        if self.redis_client:
            try:
                self.redis_client.ping()
                results['redis'] = True
                logger.info("✅ Redis connection successful")
            except Exception as e:
                results['redis'] = False
                logger.error(f"❌ Redis test failed: {e}")
        else:
            results['redis'] = False
        
        # Test API
        api_connections = self.collector.test_connections()
        results['coingecko_api'] = api_connections.get('coingecko', False)
        
        return results
