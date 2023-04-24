import os

# For 2FA
import pyotp
import qrcode
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from PIL import Image
from yaml.loader import SafeLoader
from config import Settings, Config

st.title("2FA QR Code")

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

    # OTP verified for current time
    totp = pyotp.TOTP(Settings().base32secret)

    imgData = pyotp.totp.TOTP(Settings().base32secret).provisioning_uri(
        name=st.session_state["username"] + "@comp5521.com",
        issuer_name="COMP Project App",
    )
    img = qrcode.make(imgData)
    img.save("2FA.png")
    image = Image.open("2FA.png")
    st.image(image)
