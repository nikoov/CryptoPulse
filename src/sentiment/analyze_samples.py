"""
Script to analyze sample data and save results.
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

def main():
    """Analyze sample data and save results."""
    try:
        # Load sample data
        with open('data/reddit/sample_posts.json', 'r') as f:
            data = json.load(f)
        
        # Initialize analyzer
        analyzer = SentimentAnalyzer()
        
        # Analyze each post
        for post in data['posts']:
            text = f"{post['title']} {post['text']}"
            sentiment = analyzer.analyze_text(text)
            post['sentiment_analysis'] = sentiment
        
        # Save results back to file
        with open('data/reddit/sample_posts.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info("Successfully analyzed and saved sentiment data")
        
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")

if __name__ == '__main__':
    main() 