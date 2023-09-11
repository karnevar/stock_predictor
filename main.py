import yfinance as yf
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob

def get_sentiment(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}/news?p={ticker}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    headlines = []

    for item in soup.select('h3'):
        text = item.get_text()
        headlines.append(text)
    
    sentiment_score = 0
    for headline in headlines:
        blob = TextBlob(headline)
        sentiment_score += blob.sentiment.polarity

    avg_sentiment = sentiment_score / len(headlines) if headlines else 0
    
    if avg_sentiment > 0.1:
        sentiment_category = "Strong sentiment"
    elif avg_sentiment > -0.1:
        sentiment_category = "Neutral sentiment"
    else:
        sentiment_category = "Low sentiment"

    return avg_sentiment, sentiment_category

def main():
    tickers = ['AAPL', 'GOOGL', 'AMZN', 'MSFT', 'TSLA']
    recommendations = {}

    for ticker in tickers:
        try:
            stock_data = yf.Ticker(ticker).history(period='7d')
            volume = stock_data['Volume'].mean()
            sentiment, sentiment_category = get_sentiment(ticker)

            # Replace with your own technical analysis formulas
            technical_score = 7.0

            # A basic, illustrative scoring system
            final_score = (volume + technical_score) / 2

            if final_score > 10000000:
                recommendation = "Strong Buy"
            else:
                recommendation = "Don't Buy"

            recommendations[ticker] = (recommendation, sentiment_category)

        except Exception as e:
            print(f"Could not fetch data for {ticker}. Skipping.")
            print(e)

    print("Recommended stocks:")
    for ticker, (recommendation, sentiment_category) in recommendations.items():
        print(f"{ticker} {recommendation} {sentiment_category}")

if __name__ == "__main__":
    main()
