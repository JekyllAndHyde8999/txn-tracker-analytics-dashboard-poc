import os
import time

import psycopg2
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import MetaData, create_engine, select

load_dotenv()

st.title("ST+PostgreSQL+Docker Integration Test")

username = os.getenv("POSTGRES_USERNAME")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
database_name = os.getenv("POSTGRES_DBNAME")
connection_url = f"postgresql+psycopg2://{username}:{password}@{host}/{database_name}"
engine = create_engine(connection_url)

metadata = MetaData()
metadata.reflect(bind=engine)
st.write(metadata.tables)
member = metadata.tables["member"]
query = select(member.c.name, member.c.birthday).order_by(member.c.birthday)
st.write(query)

with engine.connect() as connect:
    result = list(connect.execute(query))
    st.write(result[0])
