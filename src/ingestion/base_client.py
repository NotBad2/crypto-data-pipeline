"""
Base API client for cryptocurrency data ingestion.
"""

import time
import logging
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class BaseAPIClient(ABC):
    """Base class for cryptocurrency API clients."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, rate_limit: float = 1.0):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API
            api_key: API key for authentication (if required)
            rate_limit: Minimum seconds between requests
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'CryptoDataPipeline/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        if self.api_key:
            self._set_auth_headers()
    
    @abstractmethod
    def _set_auth_headers(self):
        """Set authentication headers. Must be implemented by subclasses."""
        pass
    
    def _wait_for_rate_limit(self):
        """Enforce rate limiting between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None, 
                     method: str = 'GET') -> Dict[str, Any]:
        """
        Make a request to the API with error handling and rate limiting.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters
            method: HTTP method
            
        Returns:
            JSON response data
            
        Raises:
            requests.RequestException: If the request fails
        """
        self._wait_for_rate_limit()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"Making {method} request to {url} with params: {params}")
            
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                timeout=30
            )
            
            response.raise_for_status()
            
            # Log successful request
            logger.info(f"Successfully fetched data from {endpoint}")
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {url}: {e}")
            if response.status_code == 429:  # Rate limit exceeded
                logger.warning("Rate limit exceeded, waiting 60 seconds...")
                time.sleep(60)
                # Increase rate limit to be more conservative
                self.rate_limit = max(self.rate_limit * 2, 10)
                logger.info(f"Increased rate limit to {self.rate_limit} seconds")
                return self._make_request(endpoint, params, method)  # Retry
            raise
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            raise
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response from {url}: {e}")
            raise
    
    def health_check(self) -> bool:
        """
        Check if the API is accessible.
        
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Most APIs have a ping or status endpoint
            response = self._make_request('ping')
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
