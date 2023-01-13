import os

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

POSTGRES_CONNECTION_STRING = os.environ["POSTGRES_CONNECTION_STRING"]


@st.cache(suppress_st_warning=True)
def load_covid_data(connection):
    engine = create_engine(connection)
    """Get COVID-19 data from database"""
    return pd.read_sql_query(
        """
        select municipality_name, date(date_of_publication), total_reported, deceased from covid.municipality_totals_daily mtd
        where municipality_name in ('Amsterdam', 'Rotterdam', 'Groningen')
        and extract(year from mtd.date_of_publication) = 2022
        order by municipality_name, date(date_of_publication)
        limit 1000;
        """,
        con=engine,
    )


@st.cache
def load_review_data(connection):
    """Get review data from database"""
    engine = create_engine(connection)
    return pd.read_sql_query(
        """
        select rest.location_city, date(r.datetime), count(*),
        AVG(r.rating_delivery) as rating_delivery,
        AVG(r.rating_food) as rating_food
        from reviews r
        join restaurants rest using(restaurant_id)
        where rest.location_city in ('Amsterdam', 'Rotterdam', 'Groningen')
        and extract(year from r.datetime) = 2022
        group by rest.location_city, date(r.datetime)
        order by rest.location_city, date(r.datetime)
        limit 1000;
        """,
        con=engine,
    )


df_case = load_covid_data(connection=POSTGRES_CONNECTION_STRING)
df_rev = load_review_data(connection=POSTGRES_CONNECTION_STRING)

st.title("COVID-19 cases and number of orders per day")

# st.header("COVID data")
# st.table(df_case.iloc[0:5])

# st.header("Review data")
# st.table(df_rev.iloc[0:5])

start_date, end_date = st.slider("Select timeframe", value=(min(df_case.date), max(df_case.date)))
df_case_filtered = df_case.loc[(df_case.date >= start_date) & (df_case.date <= end_date)]
df_rev_filtered = df_rev.loc[(df_rev.date >= start_date) & (df_rev.date <= end_date)]

# st.write("Timeframe:", start_date, "-", end_date)
# st.write("Test:", df_case_filtered)

fig2 = px.line(
    df_case_filtered,
    x="date",
    y="total_reported",
    color="municipality_name",
    title="COVID-19 cases per day (2022)",
    labels={"date": "2022", "total_reported": "Cases", "municipality_name": "City"},
)

fig2.update_xaxes(dtick="M1", tickformat="%b", ticklabelmode="period")

st.plotly_chart(fig2)

fig1 = px.line(
    df_rev_filtered,
    x="date",
    y="count",
    color="location_city",
    title="Number of orders per day (2022)",
    labels={"date": "2022", "count": "Orders", "location_city": "City"},
)

fig1.update_xaxes(dtick="M1", tickformat="%b", ticklabelmode="period")

st.plotly_chart(fig1)
