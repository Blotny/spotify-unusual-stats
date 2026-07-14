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


