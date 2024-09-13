import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import MetaData, create_engine, insert

load_dotenv()

st.title("Add Member")
st.write("Add your family's details to the database")

username = os.getenv("POSTGRES_USERNAME")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
database_name = os.getenv("POSTGRES_DBNAME")

connection_url = f"postgresql+psycopg2://{username}:{password}@{host}/{database_name}"
engine = create_engine(connection_url)
metadata = MetaData()
metadata.reflect(bind=engine)
member = metadata.tables["member"]


def add_member(name, birthday):
    if not name:
        st.error("`name` field required")
    if not birthday:
        st.error("`birthday` field required")

    if name and birthday:
        query = insert(member).values(name=name, birthday=birthday)
        with engine.connect() as conn:
            conn.execute(query)
            conn.commit()
        st.success(f"Added '{name}' member")


with st.form("Add Member"):
    name = st.text_input("First Name")
    birthday = st.date_input("Birthday", value=None, min_value=datetime(1970, 1, 1))
    add_member_button = st.form_submit_button()

    if add_member_button:
        add_member(name, birthday)
