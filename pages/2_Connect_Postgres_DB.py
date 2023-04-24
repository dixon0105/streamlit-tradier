import os

import psycopg2
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

st.title("Connect Postgres DB")

with open("./config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
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
    # Uses st.cache_resource to only run once.
    @st.cache_resource
    def init_connection():
        return psycopg2.connect(
            host=os.environ["PGHOST"],
            database=os.environ["PGDATABASE"],
            user=os.environ["PGUSER"],
            password=os.environ["PGPASSWORD"],
        )

    conn = init_connection()

    # Perform query.
    # Uses st.cache_data to only rerun when the query changes or after 5 minutes
    @st.cache_data(ttl=300)
    def run_query(query):
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

    rows = run_query("SELECT * from mytable;")

    # Print results.
    for row in rows:
        st.write(f"{row[0]} has a :{row[1]}:")
