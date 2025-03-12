"""
Setup script for CryptoPulse project.
"""

from setuptools import setup, find_packages

setup(
    name="cryptopulse",
    version="0.1.0",
    description="Cryptocurrency Market Sentiment Analysis & Price Prediction",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        'tweepy>=4.14.0',
        'praw>=7.7.1',
        'yfinance>=0.2.36',
        'requests>=2.31.0',
        'pandas>=2.2.1',
        'numpy>=1.26.4',
        'python-dotenv>=1.0.1',
        'transformers>=4.37.2',
        'torch>=2.2.1',
        'nltk>=3.8.1',
        'spacy>=3.7.4',
        'emoji>=2.10.1',
        'scikit-learn>=1.4.1',
        'xgboost>=2.0.3',
        'prophet>=1.1.5',
        'tensorflow>=2.15.0',
        'keras>=2.15.0',
        'streamlit>=1.31.1',
        'plotly>=5.18.0',
        'matplotlib>=3.8.3',
        'seaborn>=0.13.2',
        'fastapi>=0.109.2',
        'uvicorn>=0.27.1',
        'schedule>=1.2.1',
    ],
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
) 