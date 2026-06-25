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


def get_country_name(code):
    country = pycountry.countries.get(alpha_2=code)
    return country.name if country else code

country_df["country_iso3"] = country_df["conn_country"].apply(alpha2_to_alpha3)
country_df["country_name"] = country_df["conn_country"].apply(get_country_name)

# odflitrowanie wierszy które się nie skonwertowały
country_df = country_df.dropna(subset=["country_iso3"])

# znalezienie prawdopodobnego home country
home_country = country_df.loc[country_df["percent_of_listening"].idxmax(), "conn_country"]
home_country_name = get_country_name(home_country)

# tytul
st.title("Where you listened from")

# metryki na poczatku strony
col1, col2 = st.columns(2)

with col1:
    st.metric(
        label="You have visited",
        value=f"{len(country_df)} countries",
        delta="based on your Spotify data",
        delta_color="off",
    )

with col2:
    st.metric(
        label="Your home country is",
        value=home_country_name,
        delta="(probably)",
        delta_color="off",
    )


# wizualne powiększenie checkboxa
st.markdown(
    """
    <style>
    [data-testid="stCheckbox"] {
        transform: scale(1.5);
        transform-origin: left;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# checkbox do ukrycia home country
hide_home = st.checkbox(f"Hide home country ({home_country_name})")

# dane do wykresu slupkowego
chart_df = country_df.copy()
if hide_home:
    chart_df = chart_df[chart_df["conn_country"] != home_country]

chart_df["is_home"] = chart_df["conn_country"] == home_country

top_10_countries = chart_df.sort_values("percent_of_listening", ascending=False).head(10)


# wykres słupkowy
fig_bar = px.bar(
    top_10_countries,
    x="country_name",
    y="percent_of_listening",
    color="is_home",
    color_discrete_map={True: "#1DB954", False: "#555555"},
)

fig_bar.update_traces(
    hovertemplate="<b style='font-size:18px'>%{x}</b><br>%{y:.1f}% of listening<extra></extra>"
)

fig_bar.update_layout(
    xaxis_title=None,
    yaxis_title="% of listening",
    showlegend=False,
    hoverlabel=dict(font_size=14),
)

st.plotly_chart(fig_bar, use_container_width=True)

# sekcja mapy
fig = px.choropleth(
    country_df,
    locations="country_iso3",
    color="percent_of_listening",
    color_continuous_scale=["#b1e6c8", "#14833B"],
    labels={"percent_of_listening": "% of listening", "plays": "Plays"},
    hover_name="country_name",
    custom_data=["conn_country", "plays"],
    hover_data={"plays": True, "country_iso3": False}
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
    height=600,
    margin=dict(l=0, r=0, t=40, b=0),
    font=dict(color="white"),
)

fig.update_traces(
    hovertemplate="<b style='font-size:16px'>%{hovertext}</b><br>"
                  "Plays: %{customdata[1]}<br>"
                  "%{z:.1f}% of listening<extra></extra>"
)

# proporcje mapa statystyki 2:1
map_col, stats_col = st.columns([2, 1])


with map_col:
    # klikniecie na mape
    event = st.plotly_chart(
        fig,
        use_container_width=True,
        on_select="rerun",
        key="country_map_chart",
    )

with stats_col:
    if event.selection and event.selection["points"]:
        # wyciagniecie nazwy panstwa
        clicked_point = event.selection["points"][0]
        clicked_country_code = clicked_point["customdata"][0]
        clicked_country_name = clicked_point["hovertext"]
        st.subheader(f"{clicked_country_name}")

        if "stats_view" not in st.session_state:
            st.session_state["stats_view"] = "artists"
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button(
                "Top artists",
                use_container_width=True,
                type="primary" if st.session_state["stats_view"] == "artists" else "secondary",
            ):
                st.session_state["stats_view"] = "artists"
                st.rerun()
        with btn_col2:
            if st.button(
                "Top songs",
                use_container_width=True,
                type="primary" if st.session_state["stats_view"] == "songs" else "secondary",
            ):
                st.session_state["stats_view"] = "songs"
                st.rerun()

        country_df_filtered = df[df["conn_country"] == clicked_country_code]

        if st.session_state["stats_view"] == "artists":
            top_artists = (
                country_df_filtered.groupby("artist_name")
                .agg(plays=("ms_played", "count"), total_ms=("ms_played", "sum"))
                .reset_index()
            )
            top_artists["minutes"] = (top_artists["total_ms"] / 60_000).round(1)
            top_artists = top_artists.drop(columns=["total_ms"]).sort_values("minutes", ascending=False)
            
            st.dataframe(top_artists.head(10), hide_index=True, width="stretch")

        if st.session_state["stats_view"] == "songs":

            top_songs = (
                country_df_filtered.groupby(["track_name", "artist_name"])
                .agg(plays=("ms_played", "count"), total_ms=("ms_played", "sum"))
                .reset_index()
                .sort_values("plays", ascending=False)
            )
            top_songs["minutes"] = (top_songs["total_ms"] / 60_000).round(1)
            top_songs = top_songs.drop(columns=["total_ms"]).sort_values("minutes", ascending=False)

            st.dataframe(top_songs.head(10), hide_index=True, width="stretch")
    else:
        st.info("Click a country on the map to see stats.")
