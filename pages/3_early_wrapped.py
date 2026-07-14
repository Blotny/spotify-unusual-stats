import streamlit as st
import pandas as pd
from db.queries import load_events_df
from datetime import datetime
import plotly.express as px


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

# zapobieganie Latexowi w markdownach
df_current_year["track_name"] = df_current_year["track_name"].str.replace("$", r"\$", regex=False)
df_current_year["artist_name"] = df_current_year["artist_name"].str.replace("$", r"\$", regex=False)

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
    st.metric("Minutes listened", 
              total_minutes,
              delta=f"{total_days}d {remaining_hours}h {remaining_minutes}m",
              delta_color="off")

with col2:
    st.metric("Unique artists", unique_artists)

with col3:
    st.metric("Unique tracks", unique_tracks)

with col4:
    st.metric("Days of listening", f"{days_of_listening}/{day_of_year}")

st.divider()

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

col1, col2 = st.columns(2)

with col1:
    st.caption("Your top artist")
    st.markdown(f"## {top_artist_name}")
    st.markdown(f"**{top_artist_minutes} minutes**")

with col2:
    st.caption("Your top song")
    st.markdown(f"## {top_track_name}")
    st.markdown(f"**{top_track_plays} plays**")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Your top artists")
    for i, row in enumerate(top_artists.itertuples(), start=1):
        st.markdown(f"**{i}** &nbsp;&nbsp; {row.artist_name}")

with col2:
    st.subheader("Your top songs")
    for i, row in enumerate(top_tracks.itertuples(), start=1):
        st.markdown(f"**{i}** &nbsp;&nbsp; {row.track_name}")

st.divider()

# biggest listening day
biggest_day = (
    df_current_year.groupby(df_current_year["ts"].dt.date)
    .agg(minutes=("ms_played", "sum"))
    .reset_index()
    .sort_values("minutes", ascending=False)
    .iloc[0]
)

biggest_day_date = biggest_day["ts"].strftime("%#d %B")
biggest_day_minutes = int(biggest_day["minutes"] / 60_000)

st.markdown(
    f"""
    <div style="text-align: center; padding: 20px 0;">
        <p style="font-size: 16px; color: #888888; margin-bottom: 8px;">Your biggest listening day was on</p>
        <p style="font-size: 48px; font-weight: bold; margin: 0;">{biggest_day_date}</p>
        <p style="font-size: 24px; color: #1DB954; margin-top: 8px;">{biggest_day_minutes} minutes</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

col1, col2 = st.columns(2)

# bar plot z miesiącami
all_months = pd.DataFrame({
    "month_num": range(1, 13),
    "month": [datetime(current_year, m, 1).strftime("%B") for m in range(1, 13)]
})

monthly = (
    df_current_year.groupby(df_current_year["ts"].dt.month)
    .agg(minutes=("ms_played", "sum"))
    .reset_index()
    .rename(columns={"ts": "month_num"})
)

monthly["minutes"] = (monthly["minutes"] / 60_000).round(0).astype(int)

monthly = all_months.merge(monthly, on="month_num", how="left").fillna(0)
monthly["minutes"] = monthly["minutes"].astype(int)

fig_monthly = px.bar(
    monthly,
    x="month",
    y="minutes",
    color_discrete_sequence=["#1DB954"],
)

fig_monthly.update_layout(
    xaxis_title=None,
    yaxis_title="Minutes",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    margin=dict(l=0, r=0, t=20, b=0),
)

fig_monthly.update_traces(
    hovertemplate="<b>%{x}</b><br>%{y} minutes<extra></extra>"
)

# bar plot z dniami tygodnia
weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

weekly = (
    df_current_year.groupby(df_current_year["ts"].dt.day_name())
    .agg(minutes=("ms_played", "sum"))
    .reset_index()
    .rename(columns={"ts": "weekday"})
)

weekly["minutes"] = (weekly["minutes"] / 60_000).round(0).astype(int)

# zachowujemy kolejnosc dni tygodnia
weekly["weekday"] = pd.Categorical(weekly["weekday"], categories=weekday_order, ordered=True)
weekly = weekly.sort_values("weekday")

fig_weekly = px.bar(
    weekly,
    x="weekday",
    y="minutes",
    color_discrete_sequence=["#1DB954"],
)

fig_weekly.update_layout(
    xaxis_title=None,
    yaxis_title="Minutes",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    margin=dict(l=0, r=0, t=20, b=0),
)

fig_weekly.update_traces(
    hovertemplate="<b>%{x}</b><br>%{y} minutes<extra></extra>"
)

# bar ploty na stronie

with col1:
    st.subheader("Listening by month")
    st.plotly_chart(fig_monthly, use_container_width=True)


with col2:
    st.subheader("Listening by day of week")
    st.plotly_chart(fig_weekly, use_container_width=True)