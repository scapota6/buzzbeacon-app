import streamlit as st
from serpapi import GoogleSearch
from textblob import TextBlob


# Define Your API Key
API_KEY = "5d6c30c9990b21dd47dcab8b4458447a921c0f332b5d577ab5d5e166e02d457d"

# Function to search for news articles
def google_search(query):
    params = {
        "q": f"{query} news",  # Focus on news articles
        "location": "United States",
        "api_key": API_KEY,
        "tbm": "nws"  # Target the news search type
    }
    try:
        search = GoogleSearch(params)
        response = search.get_dict()

        if 'error' in response:
            st.error(f"API error: {response['error']}")
            return []

        # Print full response for debugging
        print(f"Full response: {response}")

        return response.get("news_results", [])
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return []

# Streamlit app layout
st.title("Stock News Sentiment Analyzer")

# Get user input for the search query
query = st.text_input("Enter stock ticker or company name:", "AAPL")

# Use session state to store search results and previous results
if 'searched' not in st.session_state:
    st.session_state.searched = False
if 'previous_results' not in st.session_state:
    st.session_state.previous_results = []

# Create two columns for buttons
col1, col2 = st.columns([1, 1])

# Search button
with col1:
    if st.button("Search"):
        st.session_state.searched = True

# Refresh button
with col2:
    if st.session_state.searched:
        if st.button("Refresh"):
            st.experimental_rerun()

# If searched, display news
if st.session_state.searched:
    with st.spinner("Fetching news and analyzing sentiment..."):
        results = google_search(query)

        if not results:
            st.error("No results found or error fetching the data.")
        else:
            # Check if there are new results
            new_results = []
            for result in results:
                if result not in st.session_state.previous_results:
                    new_results.append(result)
                    st.session_state.previous_results.append(result)

            # Create separate lists for positive, negative, and neutral news
            positive_news = []
            negative_news = []
            neutral_news = []

            # Analyze sentiment and categorize
            for result in new_results:
                title = result.get("title")
                link = result.get("link")
                snippet = result.get("snippet", "")

                if title and link:
                    # Perform sentiment analysis using TextBlob
                    content = f"{title}. {snippet}"
                    analysis = TextBlob(content)
                    polarity = analysis.sentiment.polarity

                    if polarity > 0.05:
                        positive_news.append((title, link))
                    elif polarity < -0.05:
                        negative_news.append((title, link))
                    else:
                        neutral_news.append((title, link))

            # Display alerts if new positive or negative news is found
            if positive_news or negative_news:
                st.markdown(
                    "<h3 style='color: green;'>New Positive or Negative News Found!</h3>",
                    unsafe_allow_html=True
                )

            # Sort news by most recent to oldest (assuming newest results come first)
            st.subheader("Positive News")
            if positive_news:
                for title, link in positive_news:
                    st.write(f"**Title**: [{title}]({link})")
                    st.write("---")
            else:
                st.write("No new positive news found.")

            st.subheader("Negative News")
            if negative_news:
                for title, link in negative_news:
                    st.write(f"**Title**: [{title}]({link})")
                    st.write("---")
            else:
                st.write("No new negative news found.")

            st.subheader("Neutral News")
            if neutral_news:
                for title, link in neutral_news:
                    st.write(f"**Title**: [{title}]({link})")
                    st.write("---")
            else:
                st.write("No new neutral news found.")

    # Refresh the app using Streamlit's rerun capability (without sleep)
    st.experimental_rerun()
