import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

st.title("Get Stock Quote")

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Check log in status
if 'authentication_status' not in st.session_state or st.session_state["authentication_status"] != True or 'status_2FA' not in st.session_state or st.session_state["status_2FA"] != True:
    st.warning('Please log in first!')
elif st.session_state["authentication_status"] == True and st.session_state["status_2FA"] == True:
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome, *{st.session_state["name"]}*')

    # Define a function to get stock quotes
    def get_stock_quote():
        # quotes = tradier.get_quotes(symbol)
        #for quote in quotes:
        #    if quote.symbol == symbol:
        #        return quote.last
        # return None
        return 100

    symbol = st.text_input("Enter a stock symbol", "AAPL")
    if st.button("Get Quote"):
        quote = get_stock_quote()
        st.write(f"The current price for {symbol} is {quote}")
