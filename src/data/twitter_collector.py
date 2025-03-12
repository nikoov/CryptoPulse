"""
Twitter data collector for CryptoPulse.
Collects tweets related to cryptocurrencies using the Twitter API v2.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import time

import tweepy
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TwitterCollector:
    def __init__(self):
        """Initialize the Twitter collector with API credentials."""
        load_dotenv()
        
        # Load Twitter API credentials from environment variables
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            logger.error("Missing Twitter API credentials in .env file")
            raise ValueError("Twitter API credentials not found")
        
        # Initialize API client
        self.client = self._init_client()
        
        # Cryptocurrency keywords to track
        self.crypto_keywords = {
            'bitcoin': ['bitcoin', 'btc', '#bitcoin', '#btc'],
            'ethereum': ['ethereum', 'eth', '#ethereum', '#eth'],
            'binancecoin': ['bnb', 'binance coin', '#bnb'],
            'ripple': ['ripple', 'xrp', '#ripple', '#xrp'],
            'cardano': ['cardano', 'ada', '#cardano', '#ada'],
            'dogecoin': ['dogecoin', 'doge', '#dogecoin', '#doge']
        }
        
    def _init_client(self) -> tweepy.Client:
        """Initialize and return the Twitter API client."""
        try:
            client = tweepy.Client(
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )
            logger.info("Twitter API client initialized successfully")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API client: {str(e)}")
            raise
    
    def collect_tweets(self, crypto_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Collect recent tweets for a specific cryptocurrency.
        
        Args:
            crypto_id: The cryptocurrency identifier
            max_results: Maximum number of tweets to collect
            
        Returns:
            List of collected tweets with metadata
        """
        if crypto_id not in self.crypto_keywords:
            logger.error(f"Unknown cryptocurrency: {crypto_id}")
            return []
        
        query = ' OR '.join(self.crypto_keywords[crypto_id])
        tweets = []
        
        try:
            # Search recent tweets
            response = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'lang', 'public_metrics']
            )
            
            if not response.data:
                logger.warning(f"No tweets found for {crypto_id}")
                return []
            
            # Process tweets
            for tweet in response.data:
                tweet_data = {
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat(),
                    'lang': tweet.lang,
                    'likes': tweet.public_metrics['like_count'],
                    'retweets': tweet.public_metrics['retweet_count'],
                    'replies': tweet.public_metrics['reply_count'],
                    'crypto_id': crypto_id
                }
                tweets.append(tweet_data)
            
            logger.info(f"Collected {len(tweets)} tweets for {crypto_id}")
            return tweets
            
        except Exception as e:
            logger.error(f"Error collecting tweets for {crypto_id}: {str(e)}")
            return []
    
    def save_tweets(self, tweets: List[Dict[str, Any]], crypto_id: str) -> None:
        """
        Save collected tweets to a JSON file.
        
        Args:
            tweets: List of collected tweets
            crypto_id: Cryptocurrency identifier for filename
        """
        if not tweets:
            logger.warning(f"No tweets to save for {crypto_id}")
            return
        
        # Create data directory if it doesn't exist
        os.makedirs('data/tweets', exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'data/tweets/tweets_{crypto_id}_{timestamp}.json'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(tweets, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(tweets)} tweets to {filename}")
            
        except IOError as e:
            logger.error(f"Error saving tweets to {filename}: {str(e)}")
    
    def collect_all_tweets(self, max_results_per_crypto: int = 100) -> None:
        """Collect tweets for all tracked cryptocurrencies."""
        for crypto_id in self.crypto_keywords:
            logger.info(f"Collecting tweets for {crypto_id}")
            tweets = self.collect_tweets(crypto_id, max_results_per_crypto)
            if tweets:
                self.save_tweets(tweets, crypto_id)
            # Add delay between cryptocurrencies to respect rate limits
            time.sleep(2)

def main():
    """Main function to demonstrate usage."""
    collector = TwitterCollector()
    collector.collect_all_tweets()

if __name__ == '__main__':
    main() 