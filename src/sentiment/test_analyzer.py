"""
Test script for the sentiment analyzer using sample data.
"""

import json
import logging
from analyzer import SentimentAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_sample_data():
    """Load sample posts from JSON file."""
    try:
        with open('data/reddit/sample_posts.json', 'r') as f:
            data = json.load(f)
            return data['posts']
    except Exception as e:
        logger.error(f"Error loading sample data: {str(e)}")
        return []

def main():
    """Main function to test sentiment analyzer."""
    # Initialize sentiment analyzer
    analyzer = SentimentAnalyzer()
    
    # Load sample data
    posts = load_sample_data()
    if not posts:
        logger.error("No sample data available")
        return
    
    # Prepare texts for analysis
    texts = [f"{post['title']} {post['text']}" for post in posts]
    
    # Analyze sentiments
    logger.info("Analyzing sentiments...")
    results = analyzer.analyze_batch(texts)
    
    # Print results
    for post, sentiment in zip(posts, results):
        print("\nPost:")
        print(f"Title: {post['title']}")
        print(f"Text: {post['text']}")
        print("Sentiment Analysis:")
        print(f"Label: {sentiment['sentiment']}")
        print(f"Confidence: {sentiment['confidence']:.2f}")
        print(f"Scores: {sentiment['scores']}")
        print("-" * 80)

if __name__ == '__main__':
    main() 