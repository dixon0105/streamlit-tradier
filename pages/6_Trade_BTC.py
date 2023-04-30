import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from config import Settings, Config
import json
import psycopg2

# Below for CoinMarketCap API
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from yaml.loader import SafeLoader
from config import Settings, Config

st.title("Trade BTC")

with open("./config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)
    cfg = Config.parse_obj(config)


authenticator = stauth.Authenticate(
    cfg.credentials,
    cfg.cookie["name"],
    cfg.cookie["key"],
    cfg.cookie["expiry_days"],
)

# Check log in status
if (
    "authentication_status" not in st.session_state
    or st.session_state["authentication_status"] != True
    or "status_2FA" not in st.session_state
    or st.session_state["status_2FA"] != True
):
    st.warning("Please log in first!")
elif (
    st.session_state["authentication_status"] == True
    and st.session_state["status_2FA"] == True
):
    authenticator.logout("Logout", "main")
    st.write(f'Welcome, *{st.session_state["name"]}*')

    # Define a function to get stock quotes
    def get_stock_quote():
        # quotes = tradier.get_quotes(symbol)
        # for quote in quotes:
        #    if quote.symbol == symbol:
        #        return quote.last
        # return None
        return 100

    i = "1"   # ID of the coin
    # url = "https://sandbox-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
    url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
    parameters = {"convert": "USD", "id": i}
    # ID: 1 (BTC), 1027 (ETH), 1975 (LINK), 825 (USDT), 2 (LTC), 5994 (SHIB)

    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": Settings().CMC_APIKEY,
    }
    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        currentPriceInUSD = data["data"][i]["quote"]["USD"]["price"]
        st.write(f'Price of {data["data"][i]["name"]} ({data["data"][i]["symbol"]}) in USD: {round(currentPriceInUSD, 4)}')

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        st.write(e)

    amt = st.number_input("Enter amount of BTC that you want to buy or sell", min_value=0.00, step=0.01)
    st.write("Equivalent amount in USD: ", round(amt*currentPriceInUSD,4), ".")

    if st.button("Buy", key='buy'):
        try:
            # Initialize connection.
            # Uses st.cache_resource to only run once.
            @st.cache_resource
            def init_connection():
                return psycopg2.connect(
                    host=Settings().PGHOST,
                    database=Settings().PGDATABASE,
                    user=Settings().PGUSER,
                    password=Settings().PGPASSWORD,
                )
                conn = init_connection()
                # Perform query.

            def run_query(query):
                with conn.cursor() as cur:
                    cur.execute(query)
                    return cur.fetchall()

            queryStmt = "INSERT INTO txn_history (buy_currency, buy_amount, sell_currency, sell_amount, usd_price, username) VALUES ("
            queryStmt += '"BTC",' + str(amt) + ',"USD",' + str(round(amt*currentPriceInUSD,4)) + ',' + str(round(currentPriceInUSD, 4)) + ',' + st.session_state["username"] + ');'
            run_query(queryStmt)

            queryStmt = "SELECT * FROM user_bal WHERE username = 'roy';"
            rows = run_query(queryStmt)
            print(rows)

            queryStmt = "UPDATE user_bal SET xxx = xxx WHERE username = username;"

            run_query(queryStmt)

            st.write("Done!")
        except:
            st.write("Something went wrong, try again later.")