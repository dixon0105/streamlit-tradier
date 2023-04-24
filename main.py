import os
import time

# For 2FA
import pyotp
import qrcode
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from config import Settings, Config

st.set_page_config(page_title="COMP Project", page_icon="random")

with open("./config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)
    cfg = Config.parse_obj(config)


authenticator = stauth.Authenticate(
    cfg.credentials,
    cfg.cookie["name"],
    cfg.cookie["key"],
    cfg.cookie["expiry_days"],
)

st.title("COMP5521 Group Project")

name, authentication_status, username = authenticator.login("Login", "main")

# Check log in status
if st.session_state["authentication_status"] == None:
    st.warning("Please enter your username and password.")
    st.session_state["status_2FA"] = False
elif st.session_state["authentication_status"] == False:
    st.error("Username/password is incorrect.")
    st.session_state["status_2FA"] = False
elif st.session_state["authentication_status"] == True:
    authenticator.logout("Logout", "main")
    st.write(f'Welcome, *{st.session_state["name"]}*')
    if "status_2FA" not in st.session_state or st.session_state["status_2FA"] != True:
        # OTP verified for current time
        totp = pyotp.TOTP(Settings().base32secret)

        code_2FA_container = st.empty()
        code_2FA = code_2FA_container.text_input("Please enter your 2FA code: ")
        Submit_2FA_btn = st.empty()
        btn = Submit_2FA_btn.button("Submit", disabled=False, key="for2FA")
        if btn:
            if totp.verify(code_2FA):
                st.session_state["status_2FA"] = True
                code_2FA_container.empty()
                Submit_2FA_btn.empty()
                success = st.success("You have passed the 2FA test!", icon="✅")
                time.sleep(2)  # Wait for 2 seconds
                success.empty()
                st.write("Please feel free to visit other pages!")
            else:
                st.error("2FA code is incorrect.")
                st.session_state["status_2FA"] = False
                st.session_state["authentication_status"] = None
    else:
        st.write("Please feel free to visit other pages!")
