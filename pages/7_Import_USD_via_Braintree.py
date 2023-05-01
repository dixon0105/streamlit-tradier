import json
import os
import psycopg2
import requests
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from requests.structures import CaseInsensitiveDict
from yaml.loader import SafeLoader
from config import Settings, Config

st.set_page_config(page_title="COMP5521 Group Project", page_icon=":100:")

st.title("Import USD via Braintree")

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
        tmpStmt = f'you have successfully transferred {txnAmount} USD to our platform!'
        url = "https://payments.sandbox.braintree-api.com/graphql"

        headers = CaseInsensitiveDict()
        headers["Authorization"] = "Basic " + os.environ["BRAINTREE_HASH"]
        headers["Braintree-Version"] = "2023-04-23"
        headers["Content-Type"] = "application/json"

        data = '{"query": "mutation chargePaymentMethod($input: ChargePaymentMethodInput!) {chargePaymentMethod(input: $input) {transaction {id status}}}" ,"variables": {"input": {"paymentMethodId": "fake-valid-nonce","transaction": {"amount": "' + f'{txnAmount}' + '"}}}}'
        resp = requests.post(url, headers=headers, data=data)
        reply = json.loads(resp.text)

        if reply["data"] and reply["data"]["chargePaymentMethod"]["transaction"]["status"] == "SUBMITTED_FOR_SETTLEMENT":
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
            def run_query(query, mode):
                with conn.cursor() as cur:
                    cur.execute(query)
                    if mode:
                        return cur.fetchall()

            try:
                queryStmt = f"UPDATE user_bal SET usd_bal=usd_bal+{txnAmount} WHERE username='"+st.session_state["username"]+"';"
                run_query(queryStmt, 0)
            except:
                st.warning("Error in writing to database for updating USD balance.")
            else:
                st.success(f'*{st.session_state["name"]}*, {tmpStmt}')
        else:
            st.error("Error message: ", reply["errors"]["message"], ".")
