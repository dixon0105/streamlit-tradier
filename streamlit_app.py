import os, streamlit as st
import streamlit_authenticator as stauth
import psycopg2
import yaml
from yaml.loader import SafeLoader
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
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.title('Some content')
elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')

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
