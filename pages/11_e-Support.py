import streamlit as st
import json
import psycopg2

st.title("e-Support")

st.write('Please fill in the following details.')

name = st.text_input('Your name:')
email = st.text_input('E-mail address:')
comment = st.text_area('Comment:', height=300)
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
        queryStmt = f"INSERT INTO e_support (name,email,comment) VALUES ('{name}','{email}','{comment}');"
        run_query(queryStmt, 0)
    except:
        st.warning("Error in saving e-Support request.")
    else:
        st.success("e-Support request submitted successfully!")