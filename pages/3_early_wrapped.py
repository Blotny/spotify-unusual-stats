import streamlit as st
import pandas as pd
from db.queries import load_events_df
from datetime import datetime


st.set_page_config(layout="wide")

if "upload_id" not in st.session_state:
    st.warning("Load file on main page.")
    st.stop()

upload_id = st.session_state["upload_id"]
df = load_events_df(upload_id)

today = datetime.now()
current_year = today.year
day_of_year = today.timetuple().tm_yday

# df dla tego roku
df_current_year = df[df["ts"].dt.year == current_year]

# metryki

# czas
total_ms = df_current_year["ms_played"].sum()

total_minutes = int(total_ms // 60_000)
total_hours = total_minutes // 60
total_days = total_hours // 24

remaining_hours = total_hours % 24
remaining_minutes = total_minutes % 60

# unikalni artysci i piosenki
unique_artists = df_current_year["artist_name"].nunique()

unique_tracks = df_current_year.groupby(["track_name", "artist_name"]).ngroups

# unikalne dni słuchania
days_of_listening = df_current_year["ts"].dt.date.nunique()


st.title("Early Spotify Wrapped")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total minutes", 
              total_minutes,
              delta=f"{total_days}d {remaining_hours}h {remaining_minutes}m",
              delta_color="off")

with col2:
    st.metric("Unique artists", unique_artists)

with col3:
    st.metric("Unique tracks", unique_tracks)

with col4:
    st.metric("Days of listening", f"{days_of_listening}/{day_of_year}")


# ulubieni artysci/piosenki

# top artysci
top_artists = (
    df_current_year.groupby("artist_name")
    .agg(ms_sum=("ms_played", "sum"))
    .reset_index()
    .sort_values("ms_sum", ascending=False)
    .head(5)
)

# top piosenki
top_tracks = (
    df_current_year
    .groupby(["track_name", "artist_name"])
    .agg(plays=("ms_played", "count"))
    .reset_index()
    .sort_values("plays", ascending=False)
    .head(5)
)

# najczesciej sluchani artysci/utwory

top_artist = top_artists.iloc[0]
top_track = top_tracks.iloc[0]

top_artist_name = top_artist["artist_name"]
top_artist_minutes = int(top_artist["ms_sum"] / 60_000)

top_track_name = top_track["track_name"]
top_track_plays = int(top_track["plays"])

metric_col1, metric_col2 = st.columns(2)

with metric_col1:
    st.metric(
        label="Your top artist",
        value=top_artist_name,
        delta=f"{top_artist_minutes} minutes",
        delta_color="off"
    )

with metric_col2:
    st.metric(
        label="Your top track",
        value=top_track_name,
        delta=f"{top_track['plays']} plays",
        delta_color="off"
    )


col1, col2 = st.columns(2)

with col1:
    st.subheader("Favourite artists")
    for i, row in enumerate(top_artists.itertuples(), start=1):
        st.markdown(
            f"<p><strong>{i}</strong> &nbsp;&nbsp; {row.artist_name}</p>",
            unsafe_allow_html=True
        )

with col2:
    st.subheader("Favourite tracks")
    for i, row in enumerate(top_tracks.itertuples(), start=1):
        st.markdown(
            f"<p><strong>{i}</strong> &nbsp;&nbsp; {row.track_name}</p>",
            unsafe_allow_html=True
        )