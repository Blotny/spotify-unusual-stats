import streamlit as st
from db.queries import load_events_df
import pandas as pd
import plotly.express as px
import pycountry


st.set_page_config(layout="wide")

if "upload_id" not in st.session_state:
    st.warning("Load file on main page.")
    st.stop()

upload_id = st.session_state["upload_id"]

df = load_events_df(upload_id)

# agregacja
country_df = df.groupby("conn_country").agg(
    plays=("ms_played", "count"),
    total_ms=("ms_played", "sum")
).reset_index()

country_df["percent_of_listening"] = country_df["total_ms"] / \
    country_df["total_ms"].sum() * 100


# konwersja kodow krajow na alpha-3
def alpha2_to_alpha3(code):
    try:
        return pycountry.countries.get(alpha_2=code).alpha_3
    except (AttributeError, KeyError):
        return None


country_df["country_iso3"] = country_df["conn_country"].apply(alpha2_to_alpha3)

# odflitrowanie wierszy które się nie skonwertowały
country_df = country_df.dropna(subset=["country_iso3"])


fig = px.choropleth(
    country_df,
    locations="country_iso3",
    color="percent_of_listening",
    color_continuous_scale=["#b1e6c8", "#1DB954", "#0b5c2e"],
    labels={"percent_of_listening": "% of listening"},
    hover_name="conn_country"
)

fig.update_geos(
    showland=True,
    bgcolor="#0d1117",
    landcolor="#1e2235",
    showframe=False,
    showcoastlines=False,
    showcountries=True,
    countrycolor="rgba(255,255,255,0.15)",
    projection_type="natural earth",
)

fig.update_layout(
    paper_bgcolor="#0d1117",
    plot_bgcolor="#0d1117",
    height=700,
    margin=dict(l=0, r=0, t=40, b=0),
    title=dict(
        text="Where you listened from",
        font=dict(color="white", size=16),
        x=0.01,
    ),
    font=dict(color="white"),
)

st.plotly_chart(fig, use_container_width=True)
