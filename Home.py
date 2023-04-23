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

st.set_page_config(page_title="COMP Project", page_icon="random")

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

st.title("COMP5521 Group Project")

name, authentication_status, username = authenticator.login('Login', 'main')

# Check log in status
if st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')
elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == True:
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome, *{st.session_state["name"]}*')
    st.write("Please feel free to visit other pages!")