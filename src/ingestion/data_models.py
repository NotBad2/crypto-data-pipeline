"""
Data models for cryptocurrency data storage.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import json


@dataclass
class CoinMarketData:
    """Data model for coin market information."""
    
    # Basic coin info
    coin_id: str
    symbol: str
    name: str
    
    # Market data
    current_price: Optional[float] = None
    market_cap: Optional[int] = None
    market_cap_rank: Optional[int] = None
    fully_diluted_valuation: Optional[int] = None
    total_volume: Optional[int] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    
    # Price changes
    price_change_24h: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
    price_change_percentage_7d: Optional[float] = None
    price_change_percentage_30d: Optional[float] = None
    price_change_percentage_1y: Optional[float] = None
    
    # Market cap changes
    market_cap_change_24h: Optional[int] = None
    market_cap_change_percentage_24h: Optional[float] = None
    
    # Supply data
    circulating_supply: Optional[float] = None
    total_supply: Optional[float] = None
    max_supply: Optional[float] = None
    
    # Additional metrics
    ath: Optional[float] = None  # All-time high
    ath_change_percentage: Optional[float] = None
    ath_date: Optional[datetime] = None
    atl: Optional[float] = None  # All-time low
    atl_change_percentage: Optional[float] = None
    atl_date: Optional[datetime] = None
    
    # Timestamps
    last_updated: Optional[datetime] = None
    collected_at: datetime = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = asdict(self)
        
        # Convert datetime objects to ISO format strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        
        return data
    
    @classmethod
    def from_coingecko_response(cls, data: Dict[str, Any]) -> 'CoinMarketData':
        """Create instance from CoinGecko API response."""
        
        # Parse datetime fields
        last_updated = None
        if data.get('last_updated'):
            try:
                last_updated = datetime.fromisoformat(data['last_updated'].replace('Z', '+00:00'))
            except:
                pass
        
        ath_date = None
        if data.get('ath_date'):
            try:
                ath_date = datetime.fromisoformat(data['ath_date'].replace('Z', '+00:00'))
            except:
                pass
        
        atl_date = None
        if data.get('atl_date'):
            try:
                atl_date = datetime.fromisoformat(data['atl_date'].replace('Z', '+00:00'))
            except:
                pass
        
        return cls(
            coin_id=data.get('id', ''),
            symbol=data.get('symbol', ''),
            name=data.get('name', ''),
            current_price=data.get('current_price'),
            market_cap=data.get('market_cap'),
            market_cap_rank=data.get('market_cap_rank'),
            fully_diluted_valuation=data.get('fully_diluted_valuation'),
            total_volume=data.get('total_volume'),
            high_24h=data.get('high_24h'),
            low_24h=data.get('low_24h'),
            price_change_24h=data.get('price_change_24h'),
            price_change_percentage_24h=data.get('price_change_percentage_24h'),
            price_change_percentage_7d=data.get('price_change_percentage_7d_in_currency'),
            price_change_percentage_30d=data.get('price_change_percentage_30d_in_currency'),
            price_change_percentage_1y=data.get('price_change_percentage_1y_in_currency'),
            market_cap_change_24h=data.get('market_cap_change_24h'),
            market_cap_change_percentage_24h=data.get('market_cap_change_percentage_24h'),
            circulating_supply=data.get('circulating_supply'),
            total_supply=data.get('total_supply'),
            max_supply=data.get('max_supply'),
            ath=data.get('ath'),
            ath_change_percentage=data.get('ath_change_percentage'),
            ath_date=ath_date,
            atl=data.get('atl'),
            atl_change_percentage=data.get('atl_change_percentage'),
            atl_date=atl_date,
            last_updated=last_updated
        )


@dataclass
class GlobalMarketData:
    """Data model for global cryptocurrency market data."""
    
    active_cryptocurrencies: Optional[int] = None
    upcoming_icos: Optional[int] = None
    ongoing_icos: Optional[int] = None
    ended_icos: Optional[int] = None
    markets: Optional[int] = None
    
    # Market cap data
    total_market_cap_usd: Optional[float] = None
    total_volume_24h_usd: Optional[float] = None
    market_cap_percentage_btc: Optional[float] = None
    market_cap_percentage_eth: Optional[float] = None
    market_cap_change_percentage_24h_usd: Optional[float] = None
    
    # Market dominance
    bitcoin_dominance: Optional[float] = None
    ethereum_dominance: Optional[float] = None
    
    # Timestamps
    updated_at: Optional[datetime] = None
    collected_at: datetime = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = asdict(self)
        
        # Convert datetime objects to ISO format strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        
        return data
    
    @classmethod
    def from_coingecko_response(cls, data: Dict[str, Any]) -> 'GlobalMarketData':
        """Create instance from CoinGecko global API response."""
        
        global_data = data.get('data', {})
        
        # Parse updated timestamp
        updated_at = None
        if global_data.get('updated_at'):
            try:
                updated_at = datetime.fromtimestamp(global_data['updated_at'])
            except:
                pass
        
        # Extract market cap data
        total_market_cap = global_data.get('total_market_cap', {})
        total_volume_24h = global_data.get('total_volume', {})
        market_cap_percentage = global_data.get('market_cap_percentage', {})
        market_cap_change_24h = global_data.get('market_cap_change_percentage_24h_usd')
        
        # Handle market cap change - can be float or dict
        market_cap_change_usd = None
        if market_cap_change_24h is not None:
            if isinstance(market_cap_change_24h, dict):
                market_cap_change_usd = market_cap_change_24h.get('usd')
            elif isinstance(market_cap_change_24h, (int, float)):
                market_cap_change_usd = market_cap_change_24h
        
        return cls(
            active_cryptocurrencies=global_data.get('active_cryptocurrencies'),
            upcoming_icos=global_data.get('upcoming_icos'),
            ongoing_icos=global_data.get('ongoing_icos'),
            ended_icos=global_data.get('ended_icos'),
            markets=global_data.get('markets'),
            total_market_cap_usd=total_market_cap.get('usd') if isinstance(total_market_cap, dict) else None,
            total_volume_24h_usd=total_volume_24h.get('usd') if isinstance(total_volume_24h, dict) else None,
            market_cap_percentage_btc=market_cap_percentage.get('btc') if isinstance(market_cap_percentage, dict) else None,
            market_cap_percentage_eth=market_cap_percentage.get('eth') if isinstance(market_cap_percentage, dict) else None,
            market_cap_change_percentage_24h_usd=market_cap_change_usd,
            bitcoin_dominance=market_cap_percentage.get('btc') if isinstance(market_cap_percentage, dict) else None,
            ethereum_dominance=market_cap_percentage.get('eth') if isinstance(market_cap_percentage, dict) else None,
            updated_at=updated_at
        )


@dataclass 
class PricePoint:
    """Data model for time-series price data."""
    
    coin_id: str
    timestamp: datetime
    price: float
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    collected_at: datetime = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = asdict(self)
        
        # Convert datetime objects to ISO format strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        
        return data
