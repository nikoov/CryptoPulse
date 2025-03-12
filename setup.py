"""
Setup script for CryptoPulse project.
"""

from setuptools import setup, find_packages

setup(
    name="CryptoPulse",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "tweepy>=4.14.0",
        "praw>=7.7.1",
        "yfinance>=0.2.35",
        "tensorflow>=2.15.0",
        "transformers>=4.36.0",
        "torch>=2.1.0",
        "streamlit>=1.31.0",
        "plotly>=5.18.0",
        "pytest>=8.0.0"
    ],
    extras_require={
        "dev": [
            "black",
            "flake8",
            "isort",
            "mypy",
            "pytest",
            "pytest-cov"
        ]
    },
    python_requires=">=3.9",
    author="Your Name",
    author_email="your.email@example.com",
    description="A cryptocurrency market sentiment analysis and price prediction platform",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="cryptocurrency, sentiment-analysis, price-prediction, machine-learning",
    url="https://github.com/yourusername/CryptoPulse",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
) 