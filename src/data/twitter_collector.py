"""
Twitter data collector for CryptoPulse.
Collects cryptocurrency-related tweets using the Twitter API.
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

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
        
        # Load Twitter API credentials
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            raise ValueError("Missing Twitter API credentials in .env file")
        
        # Initialize Twitter API client
        self.auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True)
        
        # Define cryptocurrency-related keywords and hashtags
        self.crypto_keywords = [
            '#bitcoin', '#crypto', '#ethereum', '#cryptocurrency',
            'bitcoin', 'crypto', 'ethereum', 'btc', 'eth'
        ]

    def collect_tweets(self, query: str, count: int = 100) -> List[Dict[Any, Any]]:
        """
        Collect tweets based on a search query.
        
        Args:
            query: Search query string
            count: Number of tweets to collect (default: 100)
            
        Returns:
            List of collected tweets as dictionaries
        """
        tweets = []
        try:
            for tweet in tweepy.Cursor(self.api.search_tweets,
                                     q=query,
                                     lang='en',
                                     tweet_mode='extended').items(count):
                tweet_data = {
                    'id': tweet.id_str,
                    'created_at': tweet.created_at.isoformat(),
                    'text': tweet.full_text,
                    'user': tweet.user.screen_name,
                    'retweet_count': tweet.retweet_count,
                    'favorite_count': tweet.favorite_count,
                }
                tweets.append(tweet_data)
                
        except tweepy.TweepError as e:
            logger.error(f"Error collecting tweets: {str(e)}")
            
        return tweets

    def save_tweets(self, tweets: List[Dict[Any, Any]], filename: str = None) -> None:
        """
        Save collected tweets to a JSON file.
        
        Args:
            tweets: List of tweet dictionaries
            filename: Output filename (optional)
        """
        if filename is None:
            filename = f'data/tweets_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(tweets, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(tweets)} tweets to {filename}")
            
        except IOError as e:
            logger.error(f"Error saving tweets: {str(e)}")

    def collect_crypto_tweets(self, count_per_keyword: int = 100) -> List[Dict[Any, Any]]:
        """
        Collect tweets for all cryptocurrency keywords.
        
        Args:
            count_per_keyword: Number of tweets to collect per keyword
            
        Returns:
            List of collected tweets
        """
        all_tweets = []
        for keyword in self.crypto_keywords:
            logger.info(f"Collecting tweets for keyword: {keyword}")
            tweets = self.collect_tweets(keyword, count_per_keyword)
            all_tweets.extend(tweets)
            
        return all_tweets

def main():
    """Main function to demonstrate usage."""
    collector = TwitterCollector()
    tweets = collector.collect_crypto_tweets(count_per_keyword=100)
    collector.save_tweets(tweets)

if __name__ == '__main__':
    main() 