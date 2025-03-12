"""
Cryptocurrency price data collector for CryptoPulse.
Collects historical and current price data using the CoinGecko API.
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

import requests
import pandas as pd
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter for API calls."""
    def __init__(self, calls_per_minute: int = 30, calls_per_second: int = 10):
        self.calls_per_minute = calls_per_minute
        self.calls_per_second = calls_per_second
        self.minute_calls = []
        self.second_calls = []
        
    def wait_if_needed(self) -> None:
        """Wait if we've exceeded our rate limit."""
        now = time.time()
        
        # Remove calls older than 1 minute
        self.minute_calls = [call_time for call_time in self.minute_calls 
                           if now - call_time < 60]
        
        # Remove calls older than 1 second
        self.second_calls = [call_time for call_time in self.second_calls 
                           if now - call_time < 1]
        
        # Check minute limit
        if len(self.minute_calls) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.minute_calls[0])
            if sleep_time > 0:
                logger.info(f"Minute rate limit reached. Waiting {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                # Reset calls after waiting
                self.minute_calls = []
                self.second_calls = []
                
        # Check second limit
        elif len(self.second_calls) >= self.calls_per_second:
            sleep_time = 1 - (now - self.second_calls[0])
            if sleep_time > 0:
                logger.debug(f"Second rate limit reached. Waiting {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                self.second_calls = []
        
        now = time.time()  # Update time after potential sleep
        self.minute_calls.append(now)
        self.second_calls.append(now)

class PriceCollector:
    def __init__(self):
        """Initialize the price collector."""
        self.base_url = "https://api.coingecko.com/api/v3"
        self.rate_limiter = RateLimiter()
        
        # List of cryptocurrencies to track (id: display_name)
        self.cryptocurrencies = {
            'bitcoin': 'Bitcoin',
            'ethereum': 'Ethereum',
            'binancecoin': 'BNB',
            'ripple': 'XRP',
            'cardano': 'Cardano',
            'dogecoin': 'Dogecoin'
        }
        
        # Supported fiat currencies
        self.fiat_currencies = ['usd', 'eur', 'gbp', 'jpy']
        
        # Retry configuration
        self.max_retries = 3
        self.base_delay = 2  # Base delay in seconds for exponential backoff

    def _make_request(self, url: str, params: Dict[str, Any], 
                     retry_count: int = 0) -> Optional[Dict]:
        """
        Make an API request with retry logic.
        
        Args:
            url: API endpoint URL
            params: Query parameters
            retry_count: Current retry attempt number
            
        Returns:
            JSON response or None if all retries failed
        """
        try:
            self.rate_limiter.wait_if_needed()
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            
            if response.status_code == 429:  # Too Many Requests
                if retry_count < self.max_retries:
                    delay = self.base_delay * (2 ** retry_count)
                    logger.warning(f"Rate limit exceeded. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    return self._make_request(url, params, retry_count + 1)
                else:
                    logger.error("Max retries reached for rate limit.")
                    return None
            
            if response.status_code >= 500 and retry_count < self.max_retries:
                delay = self.base_delay * (2 ** retry_count)
                logger.warning(f"Server error {response.status_code}. Retrying in {delay} seconds...")
                time.sleep(delay)
                return self._make_request(url, params, retry_count + 1)
            
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            if retry_count < self.max_retries:
                delay = self.base_delay * (2 ** retry_count)
                logger.warning(f"Request failed: {str(e)}. Retrying in {delay} seconds...")
                time.sleep(delay)
                return self._make_request(url, params, retry_count + 1)
            else:
                logger.error(f"Max retries reached. Error: {str(e)}")
                return None

    def get_current_prices(self, vs_currencies: List[str] = None) -> Dict[str, Dict[str, float]]:
        """
        Get current prices for all tracked cryptocurrencies.
        
        Args:
            vs_currencies: List of fiat currencies to get prices in (default: all supported)
            
        Returns:
            Dictionary of current prices
        """
        if vs_currencies is None:
            vs_currencies = self.fiat_currencies
            
        crypto_ids = ','.join(self.cryptocurrencies.keys())
        vs_currencies_str = ','.join(vs_currencies)
        
        url = f"{self.base_url}/simple/price"
        params = {
            'ids': crypto_ids,
            'vs_currencies': vs_currencies_str,
            'include_24hr_change': 'true',
            'include_24hr_vol': 'true',
            'include_market_cap': 'true'
        }
        
        response_data = self._make_request(url, params)
        return response_data if response_data else {}

    def get_historical_prices(self, crypto_id: str, vs_currency: str = 'usd',
                            days: int = 365) -> pd.DataFrame:
        """
        Get historical price data for a cryptocurrency.
        
        Args:
            crypto_id: CoinGecko cryptocurrency ID
            vs_currency: Fiat currency to get prices in
            days: Number of days of historical data to fetch
            
        Returns:
            DataFrame with historical price data
        """
        url = f"{self.base_url}/coins/{crypto_id}/market_chart"
        params = {
            'vs_currency': vs_currency,
            'days': days,
            'interval': 'daily'
        }
        
        response_data = self._make_request(url, params)
        if not response_data:
            return pd.DataFrame()
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(response_data['prices'], columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Add volume and market cap
            df['volume'] = [x[1] for x in response_data['total_volumes']]
            df['market_cap'] = [x[1] for x in response_data['market_caps']]
            
            return df
            
        except (KeyError, ValueError) as e:
            logger.error(f"Error processing data for {crypto_id}: {str(e)}")
            return pd.DataFrame()

    def save_price_data(self, data: Any, data_type: str) -> None:
        """
        Save collected price data to a file.
        
        Args:
            data: Price data to save
            data_type: Type of data ('current' or 'historical')
        """
        filename = f'data/prices_{data_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        try:
            if isinstance(data, pd.DataFrame):
                data.to_csv(f"{filename}.csv")
                logger.info(f"Saved {data_type} price data to {filename}.csv")
            else:
                with open(f"{filename}.json", 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info(f"Saved {data_type} price data to {filename}.json")
                
        except IOError as e:
            logger.error(f"Error saving {data_type} price data: {str(e)}")

    def collect_all_data(self) -> None:
        """Collect both current and historical price data for all tracked cryptocurrencies."""
        # Collect current prices
        current_prices = self.get_current_prices()
        if current_prices:
            self.save_price_data(current_prices, 'current')
            # Add delay after bulk request
            time.sleep(2)
        
        # Collect historical prices
        for crypto_id in self.cryptocurrencies:
            logger.info(f"Collecting historical prices for {self.cryptocurrencies[crypto_id]}")
            historical_prices = self.get_historical_prices(crypto_id)
            if not historical_prices.empty:
                self.save_price_data(historical_prices, f'historical_{crypto_id}')
            
            # Add delay between cryptocurrencies to avoid rate limits
            # Use longer delay (10 seconds) as historical data requires more API calls
            logger.info("Waiting 10 seconds before next request...")
            time.sleep(10)

def main():
    """Main function to demonstrate usage."""
    collector = PriceCollector()
    collector.collect_all_data()

if __name__ == '__main__':
    main() 