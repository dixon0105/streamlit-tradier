import streamlit as st
import json
import psycopg2

st.title("eKYC")

st.write('Please fill in the following details.')

name = st.text_input('Your name:')
email = st.text_input('E-mail address:')
phone_no = st.number_input('Mobile phone number:')
annual_income = st.number_input('Annual income (in USD):')
descriptions = st.text_area('Descriptions about yourself:', height=300)
link = st.text_input('Link to the required documents:')

if st.button("Submit"):
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
    def run_query(query,mode):
        with conn.cursor() as cur:
            cur.execute(query)
            if mode:
                return cur.fetchall()

    try:
        queryStmt = f"INSERT INTO e_kyc (name,email,phone_no,annual_income,descriptions,link) VALUES ('{name}','{email}','{phone_no}','{annual_income}','{descriptions}','{link}');"
        run_query(queryStmt, 0)
    except:
        st.warning("Error in saving eKYC information.")
    else:
        st.success("eKYC information saved successfully!")