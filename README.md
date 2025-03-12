# CryptoPulse 📈

A cryptocurrency market sentiment analysis and price prediction platform that combines social media sentiment with historical price data to forecast market movements.

## Features
- Real-time social media sentiment analysis (Twitter, Reddit)
- Historical cryptocurrency price analysis
- Advanced price prediction using machine learning
- Interactive dashboard for market insights
- Sentiment trend visualization

## Project Structure
```
CryptoPulse/
├── data/               # Data storage
├── notebooks/          # Jupyter notebooks for analysis
├── src/               # Source code
│   ├── data/          # Data collection and processing
│   ├── models/        # ML models
│   ├── sentiment/     # Sentiment analysis
│   └── visualization/ # Dashboard and plots
├── tests/             # Unit tests
└── webapp/           # Streamlit web application
```

## Setup
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Usage
1. Start the data collection:
```bash
python src/data/collector.py
```

2. Run the sentiment analysis:
```bash
python src/sentiment/analyzer.py
```

3. Launch the web dashboard:
```bash
streamlit run webapp/app.py
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.