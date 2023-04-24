import json
import os

import requests
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from requests.structures import CaseInsensitiveDict
from yaml.loader import SafeLoader
from config import Settings, Config

st.title("Braintree")

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

    txnAmountInput = st.number_input(
        "Enter the amount that you want to transfer (in USD): ", min_value=0
    )

    if st.button("Submit"):
        txnAmount = float(txnAmountInput)
        tmpStmt = (
            "you have successfully transferred " + txnAmount + " USD to our platform!"
        )
        url = "https://payments.sandbox.braintree-api.com/graphql"

        headers = CaseInsensitiveDict()
        headers["Authorization"] = "Basic " + os.environ["BRAINTREE_HASH"]
        headers["Braintree-Version"] = "2023-04-23"
        headers["Content-Type"] = "application/json"

        data = (
            '{"query": "mutation chargePaymentMethod($input: ChargePaymentMethodInput!) {chargePaymentMethod(input: $input) {transaction {id status}}}" ,"variables": {"input": {"paymentMethodId": "fake-valid-nonce","transaction": {"amount": "'
            + txnAmount
            + '"}}}}'
        )
        resp = requests.post(url, headers=headers, data=data)
        reply = json.loads(resp.text)

        if (
            reply["data"]
            and reply["data"]["chargePaymentMethod"]["transaction"]["status"]
            == "SUBMITTED_FOR_SETTLEMENT"
        ):
            st.write(f'*{st.session_state["name"]}*, {tmpStmt}')
        else:
            st.error("Error message: ", reply["errors"]["message"], ".")
