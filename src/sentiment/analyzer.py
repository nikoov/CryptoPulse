"""
Sentiment analyzer for CryptoPulse.
Uses transformers for sentiment analysis of social media content.
"""

import os
import json
import logging
from typing import List, Dict, Any, Union, Tuple
from datetime import datetime

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self, model_name: str = "finiteautomata/bertweet-base-sentiment-analysis"):
        """
        Initialize the sentiment analyzer.
        
        Args:
            model_name: Name of the pre-trained model to use
        """
        load_dotenv()
        
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load model and tokenizer
        logger.info(f"Loading model {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.to(self.device)
        
        # Label mapping
        self.labels = ['negative', 'neutral', 'positive']
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text before sentiment analysis.
        
        Args:
            text: Input text
            
        Returns:
            Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = ' '.join(word for word in text.split() if not word.startswith('http'))
        
        # Remove multiple spaces
        text = ' '.join(text.split())
        
        return text
    
    def analyze_text(self, text: str) -> Dict[str, Union[str, float]]:
        """
        Analyze sentiment of a single text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary containing sentiment label and scores
        """
        # Preprocess text
        text = self.preprocess_text(text)
        
        try:
            # Tokenize and prepare for model
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get model prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                scores = torch.softmax(outputs.logits, dim=1)
                prediction = torch.argmax(scores, dim=1)
            
            # Convert to numpy for easier handling
            scores = scores.cpu().numpy()[0]
            label = self.labels[prediction.item()]
            
            return {
                'text': text,
                'sentiment': label,
                'confidence': float(scores[prediction.item()]),
                'scores': {
                    'negative': float(scores[0]),
                    'neutral': float(scores[1]),
                    'positive': float(scores[2])
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing text: {str(e)}")
            return {
                'text': text,
                'sentiment': 'neutral',
                'confidence': 0.0,
                'scores': {'negative': 0.0, 'neutral': 1.0, 'positive': 0.0}
            }
    
    def analyze_batch(self, texts: List[str], batch_size: int = 32) -> List[Dict[str, Union[str, float]]]:
        """
        Analyze sentiment of multiple texts in batches.
        
        Args:
            texts: List of input texts
            batch_size: Number of texts to process at once
            
        Returns:
            List of sentiment analysis results
        """
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_texts = [self.preprocess_text(text) for text in batch_texts]
            
            try:
                # Tokenize batch
                inputs = self.tokenizer(batch_texts, return_tensors="pt", truncation=True,
                                     max_length=512, padding=True)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # Get model predictions
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    scores = torch.softmax(outputs.logits, dim=1)
                    predictions = torch.argmax(scores, dim=1)
                
                # Convert to numpy
                scores = scores.cpu().numpy()
                predictions = predictions.cpu().numpy()
                
                # Process each result
                for j, (text, pred, score) in enumerate(zip(batch_texts, predictions, scores)):
                    results.append({
                        'text': text,
                        'sentiment': self.labels[pred],
                        'confidence': float(score[pred]),
                        'scores': {
                            'negative': float(score[0]),
                            'neutral': float(score[1]),
                            'positive': float(score[2])
                        }
                    })
                
            except Exception as e:
                logger.error(f"Error analyzing batch: {str(e)}")
                # Add neutral sentiment for failed batch
                for text in batch_texts:
                    results.append({
                        'text': text,
                        'sentiment': 'neutral',
                        'confidence': 0.0,
                        'scores': {'negative': 0.0, 'neutral': 1.0, 'positive': 0.0}
                    })
        
        return results
    
    def analyze_social_data(self, data_path: str, data_type: str) -> None:
        """
        Analyze sentiment of social media data from files.
        
        Args:
            data_path: Path to data directory
            data_type: Type of data ('twitter' or 'reddit')
        """
        # Create output directory
        output_dir = f'data/sentiment/{data_type}'
        os.makedirs(output_dir, exist_ok=True)
        
        # Find all JSON files in the data directory
        for filename in os.listdir(data_path):
            if not filename.endswith('.json'):
                continue
            
            try:
                # Load data
                with open(os.path.join(data_path, filename), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract texts for analysis
                if data_type == 'twitter':
                    texts = [item['text'] for item in data]
                else:  # reddit
                    texts = [f"{item['title']} {item['text']}" for item in data]
                
                # Analyze sentiments
                sentiments = self.analyze_batch(texts)
                
                # Add sentiment data to original items
                for item, sentiment in zip(data, sentiments):
                    item['sentiment_analysis'] = sentiment
                
                # Save results
                output_filename = f"sentiment_{filename}"
                output_path = os.path.join(output_dir, output_filename)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Analyzed and saved sentiment data to {output_path}")
                
            except Exception as e:
                logger.error(f"Error processing file {filename}: {str(e)}")

def main():
    """Main function to demonstrate usage."""
    analyzer = SentimentAnalyzer()
    
    # Analyze Twitter data
    if os.path.exists('data/tweets'):
        analyzer.analyze_social_data('data/tweets', 'twitter')
    
    # Analyze Reddit data
    if os.path.exists('data/reddit'):
        analyzer.analyze_social_data('data/reddit', 'reddit')

if __name__ == '__main__':
    main() 