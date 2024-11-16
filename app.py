import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import json
from google_search_results import GoogleSearch
from textblob import TextBlob

# Firebase initialization
if not firebase_admin._apps:
    firebase_credentials = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)

# Streamlit App for BuzzBeacon - Stock News Sentiment
st.title("BuzzBeacon - Stock News Sentiment Analyzer")

# Registration/Login Section
st.sidebar.title("Account Management")
choice = st.sidebar.radio("Select Action", ["Login", "Register", "Continue as Guest"])

if choice == "Register":
    st.sidebar.subheader("Create a New Account")
    email = st.sidebar.text_input("Enter your email", key="email")
    password = st.sidebar.text_input("Enter your password", type="password", key="password")
    if st.sidebar.button("Register"):
        if email and password:
            try:
                # Register user in Firebase
                user = auth.create_user(
                    email=email,
                    password=password,
                )
                st.success(f"User {email} created successfully!")

                # Send confirmation email using SendGrid
                try:
                    sendgrid_api_key = st.secrets["SENDGRID_API_KEY"]
                    sg = SendGridAPIClient(sendgrid_api_key)
                    message = Mail(
                        from_email='buzzbeaconinfo@gmail.com',
                        to_emails=email,
                        subject='BuzzBeacon Registration Confirmation',
                        html_content=f'''<strong>Thank you for registering at BuzzBeacon!</strong>
                        <p>Click the link below to verify your email address:</p>
                        <a href="https://example.com/verify?uid={user.uid}">Verify Email</a>
                        '''
                    )
                    response = sg.send(message)
                    st.success("Verification email sent successfully!")
                except Exception as e:
                    st.error(f"Failed to send verification email: {e}")

            except Exception as e:
                st.error(f"Failed to create user: {e}")
        else:
            st.error("Please provide both email and password.")

elif choice == "Login":
    st.sidebar.subheader("Login to Your Account")
    login_email = st.sidebar.text_input("Enter your email", key="login_email")
    login_password = st.sidebar.text_input("Enter your password", type="password", key="login_password")
    if st.sidebar.button("Login Now"):
        # This example does not implement the full login mechanism.
        st.write("Login functionality can be implemented here.")

# Main app functionality for guest and logged-in users
st.subheader("Search Stock News Sentiment")
query = st.text_input("Enter stock ticker or company name:", "AAPL")

if st.button("Search"):
    if query:
        # Perform Google Search using SerpApi
        params = {
            "q": f"{query} news",
            "location": "United States",
            "api_key": st.secrets["SERPAPI_API_KEY"],
            "tbm": "nws"
        }
        search = GoogleSearch(params)
        response = search.get_dict()

        # Display Debugging Info (Optional)
        st.write("Debugging Info: Full API Response")
        st.json(response)

        # Extract news results and display
        news_results = response.get("news_results", [])
        if news_results:
            for result in news_results:
                title = result.get("title")
                link = result.get("link")
                snippet = result.get("snippet", "")

                if title and link:
                    # Perform sentiment analysis using TextBlob
                    analysis = TextBlob(f"{title}. {snippet}")
                    polarity = analysis.sentiment.polarity
                    sentiment = "Neutral"
                    if polarity > 0.05:
                        sentiment = "Positive"
                    elif polarity < -0.05:
                        sentiment = "Negative"

                    # Display news with sentiment
                    st.write(f"**[{title}]({link})**")
                    st.write(f"Sentiment: {sentiment}")
                    st.write("---")
        else:
            st.error("No news results found.")

# Watchlist Functionality
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

if st.checkbox("Add to Watchlist"):
    if query not in st.session_state.watchlist:
        st.session_state.watchlist.append(query)
        st.success(f"{query} added to watchlist.")
    else:
        st.info(f"{query} is already in your watchlist.")

st.subheader("Your Watchlist")
for stock in st.session_state.watchlist:
    if st.button(f"View News for {stock}"):
        # Perform Google Search using SerpApi for the watchlist item
        params = {
            "q": f"{stock} news",
            "location": "United States",
            "api_key": st.secrets["SERPAPI_API_KEY"],
            "tbm": "nws"
        }
        search = GoogleSearch(params)
        response = search.get_dict()

        # Extract news results and display
        news_results = response.get("news_results", [])
        if news_results:
            for result in news_results:
                title = result.get("title")
                link = result.get("link")
                snippet = result.get("snippet", "")

                if title and link:
                    # Perform sentiment analysis using TextBlob
                    analysis = TextBlob(f"{title}. {snippet}")
                    polarity = analysis.sentiment.polarity
                    sentiment = "Neutral"
                    if polarity > 0.05:
                        sentiment = "Positive"
                    elif polarity < -0.05:
                        sentiment = "Negative"

                    # Display news with sentiment
                    st.write(f"**[{title}]({link})**")
                    st.write(f"Sentiment: {sentiment}")
                    st.write("---")
        else:
            st.error("No news results found.")
