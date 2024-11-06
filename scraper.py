from serpapi import GoogleSearch
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# Download the necessary NLTK data
nltk.download('vader_lexicon')

# Initialize the Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

# Define Your API Key
API_KEY = "72ff7b0a75800c716ba57898246cbff53ff6c7b5b59c6794507dcc127fcc07fb"

def google_search(query):
    # Define parameters for the Google Search
    params = {
        "q": query,                 # Your search term
        "location": "United States", # Define location
        "api_key": API_KEY          # Your API key
    }

    # Perform the search
    search = GoogleSearch(params)
    results = search.get_dict()

    # Extract articles from the results
    for result in results.get("organic_results", []):
        title = result.get('title')
        link = result.get('link')

        # Perform sentiment analysis on the title
        sentiment = sia.polarity_scores(title)
        sentiment_label = "Neutral"
        if sentiment['compound'] > 0.05:
            sentiment_label = "Positive"
        elif sentiment['compound'] < -0.05:
            sentiment_label = "Negative"

        # Print the results with sentiment
        print(f"Title: {title}")
        print(f"Link: {link}")
        print(f"Sentiment: {sentiment_label}")
        print("---")

if __name__ == "__main__":
    google_search("AAPL stock news")
