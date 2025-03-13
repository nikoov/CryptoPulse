"""
Advanced sentiment analysis features for CryptoPulse.
Includes topic modeling, named entity recognition, and aspect-based sentiment analysis.
"""

import logging
from typing import Dict, List, Any, Tuple
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdvancedSentimentAnalyzer:
    def __init__(self):
        """Initialize the advanced sentiment analyzer."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.info("Downloading spaCy model...")
            import os
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        self.aspects = {
            'price': ['price', 'value', 'worth', 'cost', 'expensive', 'cheap'],
            'technology': ['blockchain', 'protocol', 'network', 'transaction', 'mining'],
            'adoption': ['adoption', 'usage', 'acceptance', 'mainstream', 'institutional'],
            'regulation': ['regulation', 'sec', 'government', 'law', 'legal'],
            'market': ['market', 'trading', 'volume', 'exchange', 'volatility']
        }
    
    def extract_entities(self, text: str) -> Dict[str, str]:
        """
        Extract named entities from text using spaCy.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary of entity text and labels
        """
        doc = self.nlp(text)
        entities = {ent.text: ent.label_ for ent in doc.ents}
        
        # Add custom cryptocurrency entity recognition
        crypto_keywords = ['bitcoin', 'ethereum', 'crypto', 'blockchain']
        for token in doc:
            if token.text.lower() in crypto_keywords:
                entities[token.text] = 'CRYPTO'
        
        return entities
    
    def perform_topic_modeling(self, texts: List[str], n_topics: int = 5) -> Tuple[List[str], np.ndarray]:
        """
        Perform topic modeling on a collection of texts.
        
        Args:
            texts: List of text documents
            n_topics: Number of topics to extract
            
        Returns:
            Tuple of (feature names, topic-term matrix)
        """
        try:
            # Transform texts to TF-IDF matrix
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Apply LDA
            lda = LatentDirichletAllocation(
                n_components=n_topics,
                random_state=42,
                learning_method='online'
            )
            
            lda.fit(tfidf_matrix)
            
            # Get feature names
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Get top words for each topic
            n_top_words = 10
            topic_summaries = []
            
            for topic_idx, topic in enumerate(lda.components_):
                top_words = [feature_names[i] for i in topic.argsort()[:-n_top_words-1:-1]]
                topic_summaries.append(f"Topic {topic_idx + 1}: {', '.join(top_words)}")
            
            return topic_summaries, lda.transform(tfidf_matrix)
            
        except Exception as e:
            logger.error(f"Error in topic modeling: {str(e)}")
            return [], np.array([])
    
    def analyze_aspects(self, text: str, sentiment_scores: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
        """
        Perform aspect-based sentiment analysis.
        
        Args:
            text: Input text to analyze
            sentiment_scores: Dictionary of sentiment scores from main analyzer
            
        Returns:
            Dictionary of aspects and their sentiment analysis
        """
        results = {}
        
        # Analyze each aspect
        for aspect, keywords in self.aspects.items():
            # Check if any keyword is present in the text
            relevant_keywords = [k for k in keywords if k in text.lower()]
            
            if relevant_keywords:
                # Find sentences containing aspect keywords
                doc = self.nlp(text)
                aspect_sentences = []
                
                for sent in doc.sents:
                    if any(keyword in sent.text.lower() for keyword in relevant_keywords):
                        aspect_sentences.append(sent.text)
                
                results[aspect] = {
                    'present': True,
                    'keywords_found': relevant_keywords,
                    'sentences': aspect_sentences,
                    'sentiment': sentiment_scores
                }
        
        return results
    
    def get_key_metrics(self, texts: List[str]) -> Dict[str, Any]:
        """
        Calculate key metrics from a collection of texts.
        
        Args:
            texts: List of text documents
            
        Returns:
            Dictionary of metrics
        """
        metrics = {
            'total_documents': len(texts),
            'avg_length': np.mean([len(text.split()) for text in texts]),
            'entities': {},
            'aspects': {aspect: 0 for aspect in self.aspects}
        }
        
        # Analyze entities and aspects across all texts
        for text in texts:
            entities = self.extract_entities(text)
            for entity, label in entities.items():
                if label not in metrics['entities']:
                    metrics['entities'][label] = []
                metrics['entities'][label].append(entity)
            
            # Count aspect mentions
            for aspect, keywords in self.aspects.items():
                if any(keyword in text.lower() for keyword in keywords):
                    metrics['aspects'][aspect] += 1
        
        # Calculate percentages for aspects
        total_docs = metrics['total_documents']
        metrics['aspect_percentages'] = {
            aspect: (count / total_docs) * 100 
            for aspect, count in metrics['aspects'].items()
        }
        
        return metrics

def main():
    """Main function to demonstrate usage."""
    analyzer = AdvancedSentimentAnalyzer()
    
    # Example texts
    texts = [
        "Bitcoin's price reached new highs as institutional adoption grows.",
        "The blockchain protocol shows promising technological advancement.",
        "Regulatory concerns affect crypto market sentiment."
    ]
    
    # Demonstrate functionality
    for text in texts:
        entities = analyzer.extract_entities(text)
        print(f"\nEntities in: {text}")
        print(entities)
    
    topics, _ = analyzer.perform_topic_modeling(texts)
    print("\nTopics:")
    for topic in topics:
        print(topic)

if __name__ == '__main__':
    main() 