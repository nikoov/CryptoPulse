"""
Main data collection script for CryptoPulse.
Combines Twitter, Reddit, and cryptocurrency price data collection.
"""

import logging
import time
from datetime import datetime
import schedule

from twitter_collector import TwitterCollector
from reddit_collector import RedditCollector
from price_collector import PriceCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self):
        """Initialize all data collectors."""
        self.twitter_collector = TwitterCollector()
        self.reddit_collector = RedditCollector()
        self.price_collector = PriceCollector()

    def collect_all_data(self):
        """Collect data from all sources."""
        try:
            logger.info("Starting data collection...")
            
            # Collect Twitter data
            logger.info("Collecting Twitter data...")
            self.twitter_collector.collect_crypto_tweets()
            
            # Collect Reddit data
            logger.info("Collecting Reddit data...")
            self.reddit_collector.collect_crypto_data()
            
            # Collect price data
            logger.info("Collecting cryptocurrency price data...")
            self.price_collector.collect_all_data()
            
            logger.info("Data collection completed successfully!")
            
        except Exception as e:
            logger.error(f"Error during data collection: {str(e)}")

def schedule_collection(collector: DataCollector, interval_minutes: int = 60):
    """
    Schedule periodic data collection.
    
    Args:
        collector: DataCollector instance
        interval_minutes: Collection interval in minutes
    """
    logger.info(f"Scheduling data collection every {interval_minutes} minutes")
    
    # Run initial collection
    collector.collect_all_data()
    
    # Schedule periodic collection
    schedule.every(interval_minutes).minutes.do(collector.collect_all_data)
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check schedule every minute
        except KeyboardInterrupt:
            logger.info("Data collection stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in scheduled collection: {str(e)}")
            time.sleep(300)  # Wait 5 minutes before retrying

def main():
    """Main function to start data collection."""
    collector = DataCollector()
    
    # Schedule collection every hour
    schedule_collection(collector, interval_minutes=60)

if __name__ == '__main__':
    main() 