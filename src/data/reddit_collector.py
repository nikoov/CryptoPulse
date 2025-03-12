"""
Reddit data collector for CryptoPulse.
Collects cryptocurrency-related posts and comments from Reddit.
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

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
        self.user_agent = os.getenv('REDDIT_USER_AGENT')
        
        if not all([self.client_id, self.client_secret, self.user_agent]):
            raise ValueError("Missing Reddit API credentials in .env file")
        
        # Initialize Reddit API client
        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent
        )
        
        # Define cryptocurrency-related subreddits
        self.crypto_subreddits = [
            'cryptocurrency',
            'bitcoin',
            'ethereum',
            'CryptoMarkets',
            'CryptoCurrencyTrading'
        ]

    def collect_posts(self, subreddit: str, limit: int = 100, sort: str = 'hot') -> List[Dict[Any, Any]]:
        """
        Collect posts from a subreddit.
        
        Args:
            subreddit: Name of the subreddit
            limit: Number of posts to collect (default: 100)
            sort: Sort method ('hot', 'new', 'top', etc.)
            
        Returns:
            List of collected posts as dictionaries
        """
        posts = []
        try:
            subreddit_instance = self.reddit.subreddit(subreddit)
            
            if sort == 'hot':
                submissions = subreddit_instance.hot(limit=limit)
            elif sort == 'new':
                submissions = subreddit_instance.new(limit=limit)
            elif sort == 'top':
                submissions = subreddit_instance.top(limit=limit)
            else:
                submissions = subreddit_instance.hot(limit=limit)
            
            for submission in submissions:
                post_data = {
                    'id': submission.id,
                    'created_utc': datetime.fromtimestamp(submission.created_utc).isoformat(),
                    'title': submission.title,
                    'text': submission.selftext,
                    'score': submission.score,
                    'upvote_ratio': submission.upvote_ratio,
                    'num_comments': submission.num_comments,
                    'url': submission.url,
                    'subreddit': subreddit,
                }
                posts.append(post_data)
                
        except Exception as e:
            logger.error(f"Error collecting posts from r/{subreddit}: {str(e)}")
            
        return posts

    def collect_comments(self, post_id: str, limit: int = 100) -> List[Dict[Any, Any]]:
        """
        Collect comments from a specific post.
        
        Args:
            post_id: Reddit post ID
            limit: Number of comments to collect (default: 100)
            
        Returns:
            List of collected comments as dictionaries
        """
        comments = []
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)  # Flatten comment tree
            
            for comment in submission.comments.list()[:limit]:
                comment_data = {
                    'id': comment.id,
                    'created_utc': datetime.fromtimestamp(comment.created_utc).isoformat(),
                    'text': comment.body,
                    'score': comment.score,
                    'author': str(comment.author),
                    'post_id': post_id,
                }
                comments.append(comment_data)
                
        except Exception as e:
            logger.error(f"Error collecting comments from post {post_id}: {str(e)}")
            
        return comments

    def save_data(self, data: List[Dict[Any, Any]], data_type: str) -> None:
        """
        Save collected data to a JSON file.
        
        Args:
            data: List of post or comment dictionaries
            data_type: Type of data ('posts' or 'comments')
        """
        filename = f'data/reddit_{data_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(data)} {data_type} to {filename}")
            
        except IOError as e:
            logger.error(f"Error saving {data_type}: {str(e)}")

    def collect_crypto_data(self, posts_per_subreddit: int = 100) -> None:
        """
        Collect posts and comments from all cryptocurrency subreddits.
        
        Args:
            posts_per_subreddit: Number of posts to collect per subreddit
        """
        all_posts = []
        all_comments = []
        
        for subreddit in self.crypto_subreddits:
            logger.info(f"Collecting posts from r/{subreddit}")
            posts = self.collect_posts(subreddit, limit=posts_per_subreddit)
            all_posts.extend(posts)
            
            # Collect comments for each post
            for post in posts:
                comments = self.collect_comments(post['id'])
                all_comments.extend(comments)
        
        # Save collected data
        self.save_data(all_posts, 'posts')
        self.save_data(all_comments, 'comments')

def main():
    """Main function to demonstrate usage."""
    collector = RedditCollector()
    collector.collect_crypto_data(posts_per_subreddit=100)

if __name__ == '__main__':
    main() 