import yfinance as yf
import requests
import logging
from bs4 import BeautifulSoup
from textblob import TextBlob
from ta.volume import OnBalanceVolumeIndicator
from ta.trend import ADXIndicator
from ta.momentum import RSIIndicator
from sklearn.preprocessing import MinMaxScaler
import pandas as pd

logging.basicConfig(level=logging.INFO)

def get_sentiment(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}/news?p={ticker}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    headlines = []

    for item in soup.select('h3[class="Mb(5px)"]'):
        text = item.get_text()
        headlines.append(text)
    
    sentiment_score = 0
    for headline in headlines:
        blob = TextBlob(headline)
        sentiment_score += blob.sentiment.polarity

    avg_sentiment = sentiment_score / len(headlines) if headlines else 0
    return avg_sentiment

def normalize_series(s):
    scaler = MinMaxScaler()
    return pd.DataFrame(scaler.fit_transform(pd.DataFrame(s)), columns=[s.name]).iloc[-1][0]

def technical_indicators(data):
    try:
        obv = OnBalanceVolumeIndicator(data['Close'], data['Volume']).on_balance_volume()
        adx = ADXIndicator(data['High'], data['Low'], data['Close']).adx()
        rsi = RSIIndicator(data['Close']).rsi()

        indicators = {
            'obv': normalize_series(obv),
            'adx': normalize_series(adx),
            'rsi': normalize_series(rsi)
        }

        return indicators

    except Exception as e:
        logging.error(f"Error in calculating technical indicators: {e}")
        return None

def main():
    tickers = ['AAPL', 'GOOGL', 'AMZN', 'MSFT', 'TSLA']

    print("Ticker | Confidence (%) | Decision")
    print("----------------------------------")
    
    for ticker in tickers:
        try:
            stock_data = yf.Ticker(ticker).history(period='70d')
            sentiment = get_sentiment(ticker)
            technical_data = technical_indicators(stock_data)

            if technical_data is not None:
                weights = {
                    'sentiment': 0.3,
                    'obv': 0.3,
                    'adx': 0.2,
                    'rsi': 0.2
                }
                
                final_score = sum(technical_data[k]*weights[k] for k in technical_data) + sentiment * weights['sentiment']
                decision = "Buy" if final_score > 0.5 else "Don't Buy"
                confidence = final_score * 100

                print(f"{ticker} | {confidence:.2f}% | {decision}")

            else:
                print(f"Skipping {ticker} due to errors.")
                
        except Exception as e:
            logging.error(f"Error for ticker {ticker}: {e}")

if __name__ == "__main__":
    main()
