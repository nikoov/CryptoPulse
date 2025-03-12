"""
Test suite for CryptoPulse data collectors.
"""

import os
import unittest
from datetime import datetime

import pandas as pd

from src.data.twitter_collector import TwitterCollector
from src.data.reddit_collector import RedditCollector
from src.data.price_collector import PriceCollector

class TestTwitterCollector(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.collector = TwitterCollector()

    def test_initialization(self):
        """Test Twitter collector initialization."""
        self.assertIsNotNone(self.collector.api_key)
        self.assertIsNotNone(self.collector.api_secret)
        self.assertIsNotNone(self.collector.access_token)
        self.assertIsNotNone(self.collector.access_token_secret)
        self.assertIsNotNone(self.collector.api)

    def test_collect_tweets(self):
        """Test tweet collection."""
        tweets = self.collector.collect_tweets('#bitcoin', count=5)
        self.assertIsInstance(tweets, list)
        if tweets:  # Only test if API returns results
            self.assertGreater(len(tweets), 0)
            self.assertIsInstance(tweets[0], dict)
            self.assertIn('text', tweets[0])

class TestRedditCollector(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.collector = RedditCollector()

    def test_initialization(self):
        """Test Reddit collector initialization."""
        self.assertIsNotNone(self.collector.client_id)
        self.assertIsNotNone(self.collector.client_secret)
        self.assertIsNotNone(self.collector.user_agent)
        self.assertIsNotNone(self.collector.reddit)

    def test_collect_posts(self):
        """Test post collection."""
        posts = self.collector.collect_posts('cryptocurrency', limit=5)
        self.assertIsInstance(posts, list)
        if posts:  # Only test if API returns results
            self.assertGreater(len(posts), 0)
            self.assertIsInstance(posts[0], dict)
            self.assertIn('title', posts[0])

class TestPriceCollector(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.collector = PriceCollector()

    def test_initialization(self):
        """Test price collector initialization."""
        self.assertIsNotNone(self.collector.base_url)
        self.assertIsInstance(self.collector.cryptocurrencies, dict)
        self.assertIsInstance(self.collector.fiat_currencies, list)

    def test_get_current_prices(self):
        """Test current price collection."""
        prices = self.collector.get_current_prices(['usd'])
        self.assertIsInstance(prices, dict)
        if prices:  # Only test if API returns results
            self.assertIn('bitcoin', prices)
            self.assertIn('usd', prices['bitcoin'])

    def test_get_historical_prices(self):
        """Test historical price collection."""
        prices = self.collector.get_historical_prices('bitcoin', days=7)
        self.assertIsInstance(prices, pd.DataFrame)
        if not prices.empty:  # Only test if API returns results
            self.assertIn('price', prices.columns)
            self.assertIn('volume', prices.columns)
            self.assertIn('market_cap', prices.columns)

def main():
    """Run the test suite."""
    unittest.main()

if __name__ == '__main__':
    main() 