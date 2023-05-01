import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from config import Settings, Config
import json
import psycopg2
import pandas as pd

st.title("Check User Balances")

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
    @st.cache_data(ttl=300)
    def run_query(query,mode):
        with conn.cursor() as cur:
            cur.execute(query)
            if mode:
                return cur.fetchall()

    queryStmt = "SELECT * FROM txn_history;"
    rows = run_query(queryStmt, 1)
    df = pd.DataFrame(rows)
    st.write(df)
    st.table(df)

