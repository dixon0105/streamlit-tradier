import json
import os

import streamlit as st
import streamlit_authenticator as stauth
import yaml

# Below for CoinMarketCap API
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from yaml.loader import SafeLoader
from config import Settings, Config

# Ref.: https://coinmarketcap.com/api/documentation/v1/#

st.title("Get Crypto Prices")

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

    # Actual link: 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    # Sandbox link: 'https://sandbox-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    # Below 2 lines for finding the IDs of corresponding coins only
    # url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/map'
    # parameters = {'symbol':'BTC,ETH,LINK,USDT,SHIB'}
    url = "https://sandbox-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
    parameters = {"convert": "USD", "id": "825,1,1027,1975,5994"}
    # ID: 1 (BTC), 1027 (ETH), 1975 (LINK), 5994 (SHIB), 825 (USDT)

    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": Settings().CMC_APIKEY,
    }
    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        for i in data["data"]:
            if data["data"][i]["symbol"] == "SHIB":
                st.write(
                    f'Price of {data["data"][i]["name"]} ({data["data"][i]["symbol"]}): {data["data"][i]["quote"]["USD"]["price"]:.8f}'
                )
            else:
                st.write(
                    f'Price of {data["data"][i]["name"]} ({data["data"][i]["symbol"]}): {round(data["data"][i]["quote"]["USD"]["price"],4)}'
                )

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        st.write(e)
