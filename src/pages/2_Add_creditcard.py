import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import MetaData, create_engine, insert, select, func

from db_config import dbconfig

load_dotenv()

st.title("Add Member")
st.write("Add your family's details to the database")

member = dbconfig.get_table("member")
creditcard = dbconfig.get_table("creditcard")
engine = dbconfig.get_engine()


def add_card(cc_number, cc_provider, cc_owner) -> bool:
    if not cc_number:
        st.error("`Credit Card Number` field required")
    if not cc_provider:
        st.error("`Credit Card Provider` field required")
    if not cc_owner:
        st.error("`Credit Card Holder` field required")

    # get id of cc_owner
    get_owner_id_query = select(member.c.id).where(member.c.name == cc_owner)
    with engine.connect() as conn:
        cc_owner = conn.execute(get_owner_id_query).fetchall()[0][0]

    if all([cc_number, cc_provider, cc_owner]):
        query = insert(creditcard).values(
            cc_number=cc_number, cc_provider=cc_provider, cc_owner=cc_owner
        )
        with engine.connect() as conn:
            conn.execute(query)
            conn.commit()
        st.success(f"Added '{cc_provider}' credit card")
        return True
    return False


member_query = select(member.c.name)
with engine.connect() as conn:
    all_members = conn.execute(member_query).fetchall()

if all_members:
    with st.form("Add Credit Card"):
        cc_number = st.text_input("Credit Card Number")
        cc_provider = st.text_input("Credit Card Provider")
        cc_owner = st.selectbox(
            label="Credit Card Holder",
            options=[""] + [name[0] for name in all_members],
        )
        add_cc_button = st.form_submit_button()

        if add_cc_button:
            add_card(cc_number, cc_provider, cc_owner)
else:
    st.info("Add family members into database first")
