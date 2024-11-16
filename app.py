import streamlit as st
from firebase_admin import credentials, firestore, initialize_app, auth
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import firebase_admin

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["FIREBASE_CREDENTIALS"])
    initialize_app(cred)
db = firestore.client()

# Streamlit App
def send_verification_email(user_email):
    try:
        # Get the SendGrid API key from Streamlit Secrets
        sendgrid_api_key = st.secrets["SENDGRID_API_KEY"]

        message = Mail(
            from_email='buzzbeaconinfo@gmail.com',
            to_emails=user_email,
            subject='Welcome to BuzzBeacon - Confirm Your Email',
            html_content="""
            <p>Hi there,</p>
            <p>Thank you for registering with BuzzBeacon! Please click the link below to confirm your email address and get started:</p>
            <a href="#">Confirm Your Email</a>
            <p>We're excited to have you onboard!</p>
            <p>Best,<br>BuzzBeacon Team</p>
            """
        )

        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)

        if response.status_code == 202:
            st.success("A verification email has been sent to your inbox.")
        else:
            st.error(f"Failed to send verification email. Status Code: {response.status_code}, Body: {response.body}")

    except Exception as e:
        st.error(f"Failed to send verification email: {e}")

# Streamlit app layout
st.title("BuzzBeacon Stock News & Watchlist")

# User Authentication - Login, Register, or Continue as Guest
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_email = ""

with st.sidebar:
    if st.session_state.authenticated:
        st.success(f"Logged in as {st.session_state.user_email}")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user_email = ""
            st.experimental_rerun()
    else:
        auth_option = st.selectbox("Authentication", ["Login", "Register", "Continue as Guest"])
        if auth_option == "Login":
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                try:
                    user = auth.get_user_by_email(email)
                    # Here, you would typically verify the password using your own implementation
                    # This code assumes a password verification step is implemented elsewhere.
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.success("Successfully logged in!")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Failed to log in: {e}")
        elif auth_option == "Register":
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("Register"):
                try:
                    user = auth.create_user(email=email, password=password)
                    send_verification_email(email)
                    st.success("Successfully registered! Please check your email to confirm your registration.")
                except Exception as e:
                    st.error(f"Failed to register: {e}")
        elif auth_option == "Continue as Guest":
            if st.button("Continue"):
                st.session_state.authenticated = True
                st.success("Continuing as guest.")
                st.experimental_rerun()

# Watchlist Feature
if st.session_state.authenticated:
    user_watchlist = db.collection('watchlists').document(st.session_state.user_email).get()
    if user_watchlist.exists:
        watchlist = user_watchlist.to_dict().get('stocks', [])
    else:
        watchlist = []

    st.sidebar.header("Your Watchlist")
    if watchlist:
        for stock in watchlist:
            if st.sidebar.button(stock):
                st.session_state.selected_stock = stock
    else:
        st.sidebar.write("Your watchlist is empty.")

    new_stock = st.text_input("Add a stock to your watchlist:")
    if st.button("Add to Watchlist") and new_stock:
        if new_stock not in watchlist:
            watchlist.append(new_stock)
            db.collection('watchlists').document(st.session_state.user_email).set({'stocks': watchlist})
            st.success(f"Added {new_stock} to your watchlist.")
        else:
            st.warning(f"{new_stock} is already in your watchlist.")

# Stock News Search
from serpapi import GoogleSearch

def google_search(query):
    params = {
        "q": f"{query} news",
        "location": "United States",
        "api_key": st.secrets["SERPAPI_API_KEY"],
        "tbm": "nws"
    }
    search = GoogleSearch(params)
    response = search.get_dict()
    return response.get("news_results", [])

if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = "AAPL"

query = st.text_input("Enter stock ticker or company name:", st.session_state.selected_stock)
if st.button("Search"):
    results = google_search(query)
    if not results:
        st.error("No results found or error fetching the data.")
    else:
        st.write(f"News for {query}")
        for result in results:
            title = result.get("title")
            link = result.get("link")
            snippet = result.get("snippet", "")
            if title and link:
                st.write(f"**[{title}]({link})**")
                st.write(f"{snippet}")
                st.write("---")
