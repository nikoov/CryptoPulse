"""
Reddit data collector for CryptoPulse.
Collects posts and comments from cryptocurrency-related subreddits.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

import praw
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RedditCollector:
    def __init__(self):
        """Initialize the Reddit collector with API credentials."""
        load_dotenv()
        
        # Load Reddit API credentials
        self.client_id = os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = os.getenv('REDDIT_USER_AGENT', 'CryptoPulse/1.0')
        self.username = os.getenv('REDDIT_USERNAME')
        self.password = os.getenv('REDDIT_PASSWORD')
        
        if not all([self.client_id, self.client_secret]):
            logger.error("Missing Reddit API credentials in .env file")
            raise ValueError("Reddit API credentials not found")
        
        # Initialize Reddit client
        self.reddit = self._init_client()
        
        # Subreddits and keywords to track
        self.crypto_subreddits = {
            'bitcoin': ['bitcoin', 'btc'],
            'ethereum': ['ethereum', 'ethtrader', 'ethfinance'],
            'binancecoin': ['binance'],
            'ripple': ['ripple', 'XRP'],
            'cardano': ['cardano', 'ADA'],
            'dogecoin': ['dogecoin']
        }
        
        self.crypto_keywords = {
            'bitcoin': ['bitcoin', 'btc'],
            'ethereum': ['ethereum', 'eth'],
            'binancecoin': ['bnb', 'binance coin'],
            'ripple': ['ripple', 'xrp'],
            'cardano': ['cardano', 'ada'],
            'dogecoin': ['dogecoin', 'doge']
        }
    
    def _init_client(self) -> praw.Reddit:
        """Initialize and return the Reddit API client."""
        try:
            reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent,
                read_only=True  # Explicitly set read-only mode
            )
            logger.info("Reddit API client initialized successfully")
            return reddit
        except Exception as e:
            logger.error(f"Failed to initialize Reddit API client: {str(e)}")
            raise
    
    def collect_subreddit_posts(self, crypto_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Collect recent posts from cryptocurrency-specific subreddits.
        
        Args:
            crypto_id: The cryptocurrency identifier
            limit: Maximum number of posts to collect per subreddit
            
        Returns:
            List of collected posts with metadata
        """
        if crypto_id not in self.crypto_subreddits:
            logger.error(f"Unknown cryptocurrency: {crypto_id}")
            return []
        
        posts = []
        subreddits = self.crypto_subreddits[crypto_id]
        
        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Collect hot posts
                for submission in subreddit.hot(limit=limit):
                    post_data = {
                        'id': submission.id,
                        'title': submission.title,
                        'text': submission.selftext,
                        'created_utc': datetime.fromtimestamp(submission.created_utc).isoformat(),
                        'score': submission.score,
                        'upvote_ratio': submission.upvote_ratio,
                        'num_comments': submission.num_comments,
                        'subreddit': subreddit_name,
                        'crypto_id': crypto_id,
                        'url': f"https://reddit.com{submission.permalink}"
                    }
                    posts.append(post_data)
                
                logger.info(f"Collected {len(posts)} posts from r/{subreddit_name}")
                
            except Exception as e:
                logger.error(f"Error collecting posts from r/{subreddit_name}: {str(e)}")
                continue
        
        return posts
    
    def save_posts(self, posts: List[Dict[str, Any]], crypto_id: str) -> None:
        """
        Save collected Reddit posts to a JSON file.
        
        Args:
            posts: List of collected posts
            crypto_id: Cryptocurrency identifier for filename
        """
        if not posts:
            logger.warning(f"No posts to save for {crypto_id}")
            return
        
        # Create data directory if it doesn't exist
        os.makedirs('data/reddit', exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'data/reddit/posts_{crypto_id}_{timestamp}.json'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(posts)} posts to {filename}")
            
        except IOError as e:
            logger.error(f"Error saving posts to {filename}: {str(e)}")
    
    def collect_all_posts(self, limit_per_subreddit: int = 100) -> None:
        """Collect posts for all tracked cryptocurrencies."""
        for crypto_id in self.crypto_subreddits:
            logger.info(f"Collecting Reddit posts for {crypto_id}")
            posts = self.collect_subreddit_posts(crypto_id, limit_per_subreddit)
            if posts:
                self.save_posts(posts, crypto_id)

def main():
    """Main function to demonstrate usage."""
    collector = RedditCollector()
    collector.collect_all_posts()

if __name__ == '__main__':
    main() 