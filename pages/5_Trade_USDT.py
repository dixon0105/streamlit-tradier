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

st.title("Trade USDT")

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


    i = "825"   # ID of the coin
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
        txnPrice = currentPriceInUSD * 0.01
        buyPrice = currentPriceInUSD + txnPrice
        sellPrice = currentPriceInUSD - txnPrice
        st.write(f'Buy price of {data["data"][i]["name"]} ({data["data"][i]["symbol"]}) in USD: {round(buyPrice, 4)}.')
        st.write(f'Sell price of {data["data"][i]["name"]} ({data["data"][i]["symbol"]}) in USD: {round(sellPrice, 4)}.')

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        st.write(e)


    # Initialize connection.
    def init_connection():
        return psycopg2.connect(
            host=Settings().PGHOST,
            database=Settings().PGDATABASE,
            user=Settings().PGUSER,
            password=Settings().PGPASSWORD,
        )
    conn = init_connection()
    conn.autocommit = True
    # Perform query.
    @st.cache_data(ttl=10)
    def run_query(query,mode):
        with conn.cursor() as cur:
            cur.execute(query)
            if mode:
                return cur.fetchall()

    queryStmt = "SELECT * FROM user_bal WHERE username = '"
    queryStmt += st.session_state["username"]+"';"
    userDetail = run_query(queryStmt,1)
    remainUSD = userDetail[0][1]
    # remainBTC = userDetail[0][2]
    # remainETH = userDetail[0][3]
    # remainLINK = userDetail[0][4]
    remainUSDT = userDetail[0][5]
    # remainLTC = userDetail[0][6]
    st.write("You currently have ",remainUSD," USD and ",remainUSDT," USDT.")


    buyAmount = st.number_input("Enter amount of USDT that you want to buy:", min_value=0.000, step=0.001)
    st.write("Equivalent amount in USD: ", round(buyAmount * buyPrice,4), ".")

    if st.button("Buy", key='buy'):
        txnUSDT = buyAmount
        txnUSD = round(buyAmount * buyPrice, 4)
        if (remainUSD >= txnUSD):
            try:
                queryStmt = "INSERT INTO txn_history (buy_currency, buy_amount, sell_currency, sell_amount, usd_price, username) VALUES ("
                queryStmt += "'USDT',"+str(txnUSDT)+",'USD',"+str(txnUSD)+","+str(round(buyAmount * buyPrice, 4))+",'"+st.session_state["username"]+"');"
                run_query(queryStmt,0)
            except:
                st.warning("Error in writing to database for transaction history.")
            else:
                try:
                    newUSD = remainUSD - txnUSD
                    newUSDT = remainUSDT + txnUSDT
                    fee = round(buyAmount * txnPrice, 4)
                    queryStmt = f"UPDATE user_bal SET usd_bal={newUSD}, usdt_bal={newUSDT} WHERE username='"+st.session_state["username"]+"';"
                    queryStmt += f"UPDATE user_bal SET usd_bal=usd_bal + {fee} WHERE username='system';"
                    run_query(queryStmt,0)
                except:
                    st.warning("Error in writing to database for updating balances.")
                else:
                    st.write("Done!")
        else:
            st.warning("Not enough USD in your account.")


    sellAmount = st.number_input("Enter amount of USDT that you want to sell:", min_value=0.000, step=0.001)
    st.write("Equivalent amount in USD: ", round(sellAmount * sellPrice,4), ".")

    if st.button("Sell", key='sell'):
        txnUSDT = sellAmount
        txnUSD = round(sellAmount * sellPrice, 4)
        if (remainUSDT >= txnUSDT):
            try:
                queryStmt = "INSERT INTO txn_history (buy_currency, buy_amount, sell_currency, sell_amount, usd_price, username) VALUES ("
                queryStmt += "'USD',"+str(txnUSD)+",'USDT',"+str(txnUSDT)+","+str(round(sellAmount * sellPrice, 4))+",'"+st.session_state["username"]+"');"
                run_query(queryStmt,0)
            except:
                st.warning("Error in writing to database for transaction history.")
            else:
                try:
                    newUSD = remainUSD + txnUSD
                    newUSDT = remainUSDT - txnUSDT
                    fee = round(sellAmount * txnPrice, 4)
                    queryStmt = f"UPDATE user_bal SET usd_bal={newUSD}, usdt_bal={newUSDT} WHERE username='"+st.session_state["username"]+"';"
                    queryStmt += f"UPDATE user_bal SET usd_bal=usd_bal + {fee} WHERE username='system';"
                    run_query(queryStmt,0)
                except:
                    st.warning("Error in writing to database for updating balances.")
                else:
                    st.write("Done!")
        else:
            st.warning("Not enough USDT in your account.")