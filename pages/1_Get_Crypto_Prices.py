import os, streamlit as st

st.title("Get Crypto Prices")

# Check log in status
if st.session_state["authentication_status"] != True:
    st.warning('Please log in first!')
else:
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome, *{st.session_state["name"]}*')

    # Actual link: 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    # Sandbox link: 'https://sandbox-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    # Below 2 lines for finding the IDs of corresponding coins only
    # url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/map'
    # parameters = {'symbol':'BTC,ETH,LINK,USDT,SHIB'}
    url = 'https://sandbox-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    parameters = {'convert':'USD', 'id':'825,1,1027,1975,5994'}
    # ID: 1 (BTC), 1027 (ETH), 1975 (LINK), 5994 (SHIB), 825 (USDT)

    headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': os.environ["CMC_APIKEY"]}
    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        # st.write(data)
        for i in data["data"]:
            if (data["data"][i]["symbol"] == "SHIB"):
                st.write(f'Price of {data["data"][i]["name"]} ({data["data"][i]["symbol"]}): {data["data"][i]["quote"]["USD"]["price"]:.8f}')
            else:
                st.write(f'Price of {data["data"][i]["name"]} ({data["data"][i]["symbol"]}): {round(data["data"][i]["quote"]["USD"]["price"],4)}')

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        st.write(e)