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
from pdf2image import convert_from_path
from sqlalchemy import MetaData, create_engine, select

load_dotenv()

st.title("Transaction Tracker")

username = os.getenv("POSTGRES_USERNAME")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
database_name = os.getenv("POSTGRES_DBNAME")

connection_url = f"postgresql+psycopg2://{username}:{password}@{host}/{database_name}"
engine = create_engine(connection_url)

tx_file = st.file_uploader("Upload PDF file", type="pdf")
if not tx_file:
    st.stop()

with TemporaryDirectory() as tempdir:
    with open(os.path.join(tempdir, tx_file.name), mode="wb") as f:
        f.write(tx_file.getvalue())

    images = convert_from_path(os.path.join(tempdir, tx_file.name))
    texts = [pytesseract.image_to_string(image=image) for image in images]

    for i, text in enumerate(texts, 1):
        with open(f"page_{i}.txt", mode="w") as f:
            f.write(text)

regex = r"^(?P<card_no>\d{4})\s+(?P<txn_date>\d{2}/\d{2})\s+(?P<post_date>\d{2}/\d{2})\s(?P<ref_no>[a-zA-Z0-9]+)\s*(?P<desc>.*?)(?P<txn_amt>\d+\.\d{2})"
punctuation_remover = str.maketrans("", "", string.punctuation)

df = pd.DataFrame(columns=["card_no", "txn_date", "desc", "amount"])
for i, text in enumerate(texts):
    matches = re.finditer(regex, text, re.MULTILINE)
    for match in matches:
        card_no = match.group("card_no")
        txn_date = date_parser.parse(match.group("txn_date")).strftime("%Y-%m-%d")
        post_date = date_parser.parse(match.group("post_date")).strftime("%Y-%m-%d")
        desc = match.group("desc").translate(punctuation_remover).strip()
        txn_amt = match.group("txn_amt").strip().strip("$")
        df.loc[df.shape[0], :] = (card_no, txn_date, desc, txn_amt)

st.dataframe(df)

metadata = MetaData()
metadata.reflect(bind=engine)
member = metadata.tables["member"]
query = select(member.c.name, member.c.birthday).order_by(member.c.birthday)
st.write(query)

with engine.connect() as connect:
    result = list(connect.execute(query))
