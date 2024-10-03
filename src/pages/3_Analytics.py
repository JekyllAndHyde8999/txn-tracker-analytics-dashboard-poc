import calendar
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import func, select, and_

from db_config import dbconfig

engine = dbconfig.get_engine()
transaction = dbconfig.get_table("transaction")
creditcard = dbconfig.get_table("creditcard")
all_months = list(calendar.month_name)

existing_months_query = select(
    func.distinct(func.extract("MONTH", transaction.c.txn_date)).label("month")
).order_by("month")
existing_months = []
with engine.connect() as conn:
    results = conn.execute(existing_months_query)
    for r in results:
        existing_months.append(all_months[int(r.month)])

month = all_months.index(
    st.sidebar.selectbox(label="Select a month", options=existing_months)
)

# all_txns = pd.read_sql(select(transaction), con=engine)
# st.dataframe(all_txns)


#### TIME SERIES PLOT ####
with engine.connect() as conn:
    r = conn.execute(
        select(
            func.min(transaction.c.txn_date).label("start_date"),
            func.max(transaction.c.txn_date).label("end_date"),
        )
    ).fetchall()[0]

start_date, end_date = st.date_input(
    "Date Range",
    value=[r.start_date, r.end_date],
    min_value=datetime(1970, 1, 1),
    format="MM/DD/YYYY",
)
df = pd.read_sql(
    select(
        transaction.c.txn_date,
        transaction.c.txn_amount,
        transaction.c.txn_cc,
        creditcard.c.cc_provider,
    )
    .join(creditcard, transaction.c.txn_cc == creditcard.c.id)
    .where(
        and_(start_date <= transaction.c.txn_date, transaction.c.txn_date <= end_date)
    ),
    con=engine,
    parse_dates=True,
)

df["txn_date_short"] = df.txn_date.apply(lambda x: x.strftime("%B %Y"))
df["sorter"] = df.txn_date.apply(lambda x: x.strftime("%Y%m"))
df = (
    df.groupby(["cc_provider", "txn_date_short", "sorter"])
    .agg({"txn_amount": "sum"})
    .reset_index()
    .sort_values(by="sorter")
)
fig = px.line(df, x="sorter", y="txn_amount", color="cc_provider")
fig.update_layout(
    xaxis={
        "tickmode": "array",
        "ticktext": df.txn_date_short,
        "tickvals": df.sorter,
        "title": "Month",
        "rangeslider_visible": True,
    },
    yaxis={"title": "Amount"},
)

st.plotly_chart(fig)

col1, col2 = st.columns(2)

# bar chart of category wise sums
query = (
    select(
        transaction.c.txn_category.label("category"),
        creditcard.c.cc_provider,
        func.sum(transaction.c.txn_amount).label("Total Amount"),
    )
    .where(func.extract("MONTH", transaction.c.txn_date) == month)
    .group_by(creditcard.c.cc_provider, transaction.c.txn_category)
    .order_by("Total Amount")
)
st.write(query)
df = pd.read_sql(query, con=engine)
col1.plotly_chart(px.bar(df, x="category", y="Total Amount", color='cc_provider'))

# pie chart of total credit used
query = (
    select(creditcard.c.cc_provider, func.sum(transaction.c.txn_amount))
    .join(creditcard, transaction.c.txn_cc == creditcard.c.id)
    .where(func.extract("MONTH", transaction.c.txn_date) == month)
    .group_by(creditcard.c.cc_provider)
)
st.write(query)
cc_usage = pd.read_sql(query, con=engine)
st.dataframe(cc_usage)
col2.plotly_chart(px.pie(cc_usage, values="sum_1", names="cc_provider"))
