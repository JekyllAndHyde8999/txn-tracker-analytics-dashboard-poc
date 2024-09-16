import os
import re
import string
import time
from tempfile import TemporaryDirectory

import pandas as pd
import psycopg2
import pytesseract
import streamlit as st
from dateutil import parser as date_parser
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_cohere import ChatCohere
from pdf2image import convert_from_path
from sqlalchemy import MetaData, create_engine, insert, select

from db_config import dbconfig

load_dotenv()

st.title("Transaction Tracker")

engine = dbconfig.get_engine()
member = dbconfig.get_table("member")
transaction = dbconfig.get_table("transaction")

prompt = PromptTemplate.from_template(
    """Determine the appropriate category for a detailed description of a credit card transaction. The category should only be 1-2 words long.
Ensure that the category chosen aligns with common classification standards in financial record-keeping.
This exercise aims to enhance your proficiency in accurately categorizing credit card transactions based on given information.
Give only the category. NO OTHER EXPLANATION IS NECESSARY.
Description: {description}"""
)
llm = ChatCohere(model="command-r")
chain = prompt | llm

tx_file = st.file_uploader("Upload PDF file", type="pdf")
if not tx_file:
    st.stop()

with TemporaryDirectory() as tempdir:
    with open(os.path.join(tempdir, tx_file.name), mode="wb") as f:
        f.write(tx_file.getvalue())

    images = convert_from_path(os.path.join(tempdir, tx_file.name))
    texts = [pytesseract.image_to_string(image=image) for image in images]

regex = r"^(?P<card_no>\d{4})\s+(?P<txn_date>\d{2}/\d{2})\s+(?P<post_date>\d{2}/\d{2})\s(?P<ref_no>[a-zA-Z0-9]+)\s*(?P<desc>.*?)(?P<txn_amt>\d+\.\d{2})"
punctuation_remover = str.maketrans("", "", string.punctuation)

df = pd.DataFrame(columns=["card_no", "txn_date", "desc", "amount", "category"])
for i, text in enumerate(texts):
    matches = re.finditer(regex, text, re.MULTILINE)
    for match in matches:
        card_no = match.group("card_no")
        txn_date = date_parser.parse(match.group("txn_date")).strftime("%Y-%m-%d")
        post_date = date_parser.parse(match.group("post_date")).strftime("%Y-%m-%d")
        desc = match.group("desc").translate(punctuation_remover).strip()
        txn_amt = match.group("txn_amt").strip().strip("$")
        category = chain.invoke({"description": desc}).content
        df.loc[df.shape[0], :] = (card_no, txn_date, desc, txn_amt, category)


def insert_into_db(df):
    with engine.connect() as connect:
        for i, row in df.iterrows():
            query = insert(transaction).values(
                txn_date=row.txn_date,
                txn_amount=row.amount,
                txn_desc=row.desc,
                txn_cc=1,
                txn_category=row.category,
            )
            connect.execute(query)
            connect.commit()


@st.fragment
def show_data_editor(df: pd.DataFrame):
    edited_df = st.data_editor(df)
    st.dataframe(edited_df)
    if st.button("Looks good!"):
        insert_into_db(edited_df)


show_data_editor(df)
