import streamlit as st
import json
import psycopg2
from config import Settings, Config
from io import StringIO

st.set_page_config(page_title="COMP5521 Group Project", page_icon=":100:")

st.title("eKYC")

st.write('Please fill in the following details.')

name = st.text_input('Full name:')
email = st.text_input('E-mail Address:')
Residential_address = st.text_input('Residential Address:')
Date_of_birth = st.date_input("Date of birth:")
phone_no = st.number_input('Mobile phone number:',min_value=0,step=1)
annual_income = st.number_input('Annual income (in USD):',min_value=0,step=1)
ID_DOC_Image = st.file_uploader("Please upload your ID Document image",type=['png', 'jpg'], accept_multiple_files=False)
descriptions = st.text_area('Descriptions about yourself:', height=300)
link = st.text_input('Link to the required documents:')


if st.button("Submit"):
    def convert_image(ID_DOC_Image):
        if ID_DOC_Image is not None:
            # To read file as bytes:
            bytes_data = ID_DOC_Image.getvalue()
            st.write(bytes_data)
            # To convert to a string based IO:
            ID_DOC_Image_stringio = StringIO(ID_DOC_Image.getvalue().decode("utf-8"))
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