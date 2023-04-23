import streamlit as st

st.title("Get Stock Quote")

# Check log in status
if st.session_state["authentication_status"] != True:
    st.warning('Please log in first!')
else:
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
