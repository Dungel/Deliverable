# %%
import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

connection_string = os.environ["POSTGRES_CONNECTION_STRING"]
engine = create_engine(connection_string)


# %%
# Get covid data grouped by municipality and date
def read_coviddata():
    df_covid = pd.read_sql_query(
        """
        select municipality_name, date_of_publication, sum(total_reported) as total_reported
        from covid.municipality_totals_daily mtd
        where municipality_name in ('Groningen', 'Amsterdam', 'Rotterdam')
        and date_of_publication > '2021-12-31'
        group by municipality_name, date_of_publication
        order by municipality_name, date_of_publication
        """,
        con=engine,
    )
    return df_covid


df_covid = read_coviddata()
# Get review data grouped by municipality and date

df_reviews = pd.read_sql_query(
    """
    select review_date, location_city, count(*) as n_reviews,
    AVG(rating_delivery) as avg_del_score, AVG(rating_food) as avg_food_score from (
        select DATE(datetime) review_date, rating_delivery, rating_food, location_city from public.reviews rv
        left join (select restaurant_id, location_city from restaurants) locs
        on rv.restaurant_id = locs.restaurant_id
        where datetime > '2021-12-31'
        and location_city in ('Groningen', 'Amsterdam', 'Rotterdam')
    ) t
    group by review_date, location_city
    """,
    con=engine,
)

# %%
############################################################################################
### Plots
############################################################################################
# Plot infections per city
fig = px.line(
    df_covid,
    x="date_of_publication",
    y="total_reported",
    color="municipality_name",
    labels={"date_of_publication": "", "total_reported": "Cases reported"},
)
st.plotly_chart(fig)
# %%
# Plot reviews per city
reviewspercity = px.line(df_reviews, x="review_date", y="n_reviews", color="location_city")
st.plotly_chart(reviewspercity)

# %%
