import os
from datetime import datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import MetaData, create_engine, func, insert, select

from db_config import dbconfig

load_dotenv()

st.title("Add Member")
st.write("Add your family's details to the database")

member = dbconfig.get_table("member")
engine = dbconfig.get_engine()


def add_member(name, birthday) -> bool:
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
        return True
    return False


with st.form("Add Member"):
    name = st.text_input("First Name")
    birthday = st.date_input("Birthday", value=None, min_value=datetime(1970, 1, 1))
    add_member_button = st.form_submit_button()

    if add_member_button:
        add_member(name, birthday)

members = pd.read_sql(select(member.c.name, member.c.birthday), con=engine)
if members.shape[0]:
    st.dataframe(members)
