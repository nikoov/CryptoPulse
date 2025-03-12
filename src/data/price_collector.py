"""
Cryptocurrency price data collector for CryptoPulse.
Collects historical and current price data using the CoinGecko API.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

import requests
import pandas as pd
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PriceCollector:
    def __init__(self):
        """Initialize the price collector."""
        self.base_url = "https://api.coingecko.com/api/v3"
        
        # List of cryptocurrencies to track (id: display_name)
        self.cryptocurrencies = {
            'bitcoin': 'Bitcoin',
            'ethereum': 'Ethereum',
            'binancecoin': 'BNB',
            'ripple': 'XRP',
            'cardano': 'Cardano',
            'solana': 'Solana',
            'polkadot': 'Polkadot',
            'dogecoin': 'Dogecoin'
        }
        
        # Supported fiat currencies
        self.fiat_currencies = ['usd', 'eur', 'gbp', 'jpy']

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
            
        try:
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
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching current prices: {str(e)}")
            return {}

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
        try:
            url = f"{self.base_url}/coins/{crypto_id}/market_chart"
            params = {
                'vs_currency': vs_currency,
                'days': days,
                'interval': 'daily'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Add volume and market cap
            df['volume'] = [x[1] for x in data['total_volumes']]
            df['market_cap'] = [x[1] for x in data['market_caps']]
            
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching historical prices for {crypto_id}: {str(e)}")
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
        
        # Collect historical prices
        for crypto_id in self.cryptocurrencies:
            logger.info(f"Collecting historical prices for {self.cryptocurrencies[crypto_id]}")
            historical_prices = self.get_historical_prices(crypto_id)
            if not historical_prices.empty:
                self.save_price_data(historical_prices, f'historical_{crypto_id}')

def main():
    """Main function to demonstrate usage."""
    collector = PriceCollector()
    collector.collect_all_data()

if __name__ == '__main__':
    main() 