import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
import base64
import json
from serpapi import GoogleSearch
from textblob import TextBlob

# Read the credentials from the environment variable
firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
if firebase_credentials:
    # Decode the base64-encoded credentials
    decoded_credentials = base64.b64decode(firebase_credentials)
    credentials_dict = json.loads(decoded_credentials)
    
    # Initialize Firebase Admin SDK only if not already initialized
    if not firebase_admin._apps:
        cred = credentials.Certificate(credentials_dict)
        firebase_admin.initialize_app(cred)

    db = firestore.client()
else:
    raise FileNotFoundError("Firebase credentials are not set in the environment variables.")

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

        return response.get("news_results", [])
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return []

# Function to handle user registration
def register_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        st.success("Account created successfully.")
        return user.uid
    except Exception as e:
        st.error(f"Error creating user: {e}")

# Function to handle user login
def login_user(email, password):
    try:
        user_record = auth.get_user_by_email(email)
        st.success(f"Logged in as {email}")
        return user_record.uid
    except Exception as e:
        st.error(f"Login failed: {e}")
        return None

# Streamlit app layout
st.title("Stock News Sentiment Analyzer")

# Handle login/signup
if 'user_uid' not in st.session_state:
    st.session_state.user_uid = None
    st.session_state.is_logged_in = False

# Pop-up modal for login/signup
if not st.session_state.is_logged_in:
    st.write("### Log in or Register")
    login_option = st.radio("Choose an option:", ["Log In", "Register", "Continue as Guest"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if login_option == "Log In":
        if st.button("Log In"):
            uid = login_user(email, password)
            if uid:
                st.session_state.user_uid = uid
                st.session_state.is_logged_in = True

    elif login_option == "Register":
        if st.button("Register"):
            uid = register_user(email, password)
            if uid:
                st.session_state.user_uid = uid
                st.session_state.is_logged_in = True

    elif login_option == "Continue as Guest":
        if st.button("Continue as Guest"):
            st.session_state.is_logged_in = True

# Initialize Streamlit session state for watchlist
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

# If the user is logged in, load their watchlist from Firestore
if st.session_state.is_logged_in and st.session_state.user_uid:
    user_doc = db.collection('users').document(st.session_state.user_uid)
    user_data = user_doc.get()
    if user_data.exists:
        st.session_state.watchlist = user_data.to_dict().get('watchlist', [])

# Get user input for the search query
query = st.text_input("Enter stock ticker or company name:", "AAPL")

# Create two columns for adding to watchlist and searching
col1, col2 = st.columns([1, 1])

# Add to Watchlist Button
with col1:
    if st.button("Add to Watchlist"):
        if query not in st.session_state.watchlist:
            st.session_state.watchlist.append(query)
            if st.session_state.is_logged_in and st.session_state.user_uid:
                # Save updated watchlist to Firestore
                db.collection('users').document(st.session_state.user_uid).set({
                    'watchlist': st.session_state.watchlist
                })
            st.success(f"Added {query} to your watchlist.")
        else:
            st.warning(f"{query} is already in your watchlist.")

# Search button
with col2:
    if st.button("Search"):
        st.session_state.searched = True
        st.session_state.selected_stock = query  # Save the current stock being searched

# Display the user's watchlist
st.subheader("Your Watchlist")
if st.session_state.watchlist:
    for stock in st.session_state.watchlist:
        if st.button(stock):
            st.session_state.searched = True
            st.session_state.selected_stock = stock  # Save the stock name from the watchlist that was clicked
else:
    st.write("Your watchlist is empty. Add stocks using the button above.")

# If searched, display news
if 'searched' in st.session_state and st.session_state.searched:
    selected_stock = st.session_state.selected_stock
    st.subheader(f"News for {selected_stock}")

    with st.spinner(f"Fetching news and analyzing sentiment for {selected_stock}..."):
        results = google_search(selected_stock)

        if not results:
            st.error("No results found or error fetching the data.")
        else:
            st.write("News and sentiment analysis here...")
