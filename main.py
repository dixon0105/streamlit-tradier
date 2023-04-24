import os
import time

# For 2FA
import pyotp
import qrcode
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

st.set_page_config(page_title="COMP Project", page_icon="random")

with open("./config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
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
        totp = pyotp.TOTP(os.environ["BASE32SECRET"])

        code_2FA = st.text_input("Please enter your 2FA code: ")
        if st.button("Submit", key="for2FA"):
            if totp.verify(code_2FA):
                st.session_state["status_2FA"] = True
                # st.code_2FA.empty()
                success = st.success("You have passed the 2FA test!", icon="✅")
                time.sleep(2)  # Wait for 2 seconds
                success.empty()
                st.write("Please feel free to visit other pages!")
                if authentication_status:
                    try:
                        if authenticator.reset_password(username, "Reset password"):
                            success = st.success("Password modified successfully")
                            time.sleep(2)  # Wait for 2 seconds
                            success.empty()
                    except Exception as e:
                        st.error(e)
            else:
                st.error("2FA code is incorrect.")
                st.session_state["status_2FA"] = False
                st.session_state["authentication_status"] = None
    else:
        st.write("Please feel free to visit other pages!")
