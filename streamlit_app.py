import os, streamlit as st
import streamlit_authenticator as stauth
import psycopg2
import yaml
from yaml.loader import SafeLoader
# Below for CoinMarketCap API
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
# Ref.: https://coinmarketcap.com/api/documentation/v1/#

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

st.set_page_config(page_title="COMP Project", page_icon="random")

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

st.title("COMP5521 Group Project")

name, authentication_status, username = authenticator.login('Login', 'main')

if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome, *{st.session_state["name"]}*')
    st.write(f'User name: *{st.session_state["username"]}*')
elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')


# url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
url = 'https://sandbox-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
parameters = {
    'convert':'USD',
    'slug':'bitcoin,ethereum'
}
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': os.environ["CMC_APIKEY"],
}

session = Session()
session.headers.update(headers)

try:
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    st.write(data)
except (ConnectionError, Timeout, TooManyRedirects) as e:
    st.write(e)



# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    return psycopg2.connect(
        host=os.environ["PGHOST"],
        database=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"]
    )
conn = init_connection()

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 5 minutes
@st.cache_data(ttl=300)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

rows = run_query("SELECT * from mytable;")

# Print results.
for row in rows:
    st.write(f"{row[0]} has a :{row[1]}:")



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
