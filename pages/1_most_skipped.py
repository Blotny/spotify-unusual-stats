import streamlit as st
import pandas as pd
from db.queries import load_events_df
from ui_helpers import require_data


st.set_page_config(
    page_title="Most skipped",
    page_icon="🎵",
    layout="wide",
)

if "upload_id" not in st.session_state:
    require_data()

upload_id = st.session_state["upload_id"]

df = load_events_df(upload_id)

df["year"] = df["ts"].dt.year
avaible_years = sorted(df["year"].unique())

if "pills_years" not in st.session_state:
    st.session_state["pills_years"] = avaible_years

# tytul i opis
st.title("Who you skipped the most")
st.markdown(
    """
    Find out which tracks and artists you skip the most. 
    Adjust the skip threshold, filter by year, and sort by skip count, 
    skip rate, or dislike score to see what you really can't stand.
    """
)

with st.expander("Filters & sorting", expanded=True):

    col1, col2 = st.columns([5, 1])

    with col2:
        st.write("")
        if st.button("Select all"):
            st.session_state["pills_years"] = avaible_years

    with col1:
        selected = st.pills(
            "Choose years:",
            options=avaible_years,
            selection_mode="multi",
            key="pills_years"
        )

    # zeby nie zostalo zero wybranych
    if not selected:
        st.warning("You must choose at least one year.")
        selected = st.session_state["pills_years"]

    # slider dla skipa
    use_raw_skips = st.checkbox("Show all Spotify-flagged skips (ignore duration)",
                                help="Spotify had some anomalies in 2018-2022 in skipped collumn so every " \
                                "reason_end that is forward button or back button count as skip")


    # warunek z reason_end jest spowodowany nie zaliczaniem przez spotify
    # wielu skipów w latach 2015-2022 gdzie reason end było forward lub
    # back button ale skipped False

    if use_raw_skips:
        df["is_skip"] = (df["spotify_is_skip"] |df["reason_end"].isin(["fwdbtn", "backbtn"]))
    else:
        max_skip_seconds = st.slider("Max seconds to count as skip:", 1, 60, 15)
        df["is_skip"] = (
            (df["spotify_is_skip"] | df["reason_end"].isin(["fwdbtn", "backbtn"]))
            & (df["ms_played"] < max_skip_seconds * 1000)
        )

    # filtrowanie dla wybranych lat
    df_filtered = df[df["year"].isin(selected)]

    # wybor opcji sortowania
    sort_mode = st.radio(
        "Sort by:",
        ["Dislike score", "Count of skips", "Skip rate"],
        horizontal=True,
        help="Dislike score = skips³ / plays² — combines skip count, skip frequency and total plays. "
         "Penalizes tracks with high play counts but low skip rate more aggressively than the basic skip count."
    )

    
# skladanie dataframe
grouped_tracks = df_filtered.groupby(["track_name", "artist_name"]).agg(
    plays=("is_skip", "count"),
    skips=("is_skip", "sum")
).reset_index()

grouped_artists = df_filtered.groupby("artist_name").agg(
    plays=("is_skip", "count"),
    skips=("is_skip", "sum")
).reset_index()


# metryki
for grouped in [grouped_tracks, grouped_artists]:
    grouped["skip_rate"] = grouped["skips"] / grouped["plays"]
    grouped["dislike_score"] = (grouped["skips"] ** 2) / grouped["plays"] * grouped["skip_rate"]

# odrzucenie utworów odtworzonych mniej niż 3 razy
grouped_tracks = grouped_tracks[grouped_tracks["plays"] >= 3]
grouped_artists = grouped_artists[grouped_artists["plays"] >= 3]


# sortowanie
if sort_mode == "Skip rate":
    grouped_tracks = grouped_tracks.sort_values(["skip_rate", "skips"], ascending=False)
    grouped_artists = grouped_artists.sort_values(["skip_rate", "skips"], ascending=False)
elif sort_mode == "Dislike score":
    grouped_tracks = grouped_tracks.sort_values("dislike_score", ascending=False)
    grouped_artists = grouped_artists.sort_values("dislike_score", ascending=False)
else:
    grouped_tracks = grouped_tracks.sort_values("skips", ascending=False)
    grouped_artists = grouped_artists.sort_values("skips", ascending=False)


# zakładki
tab_tracks, tab_artists = st.tabs(["Tracks", "Artists"])

# 20 rekordów podstawowo
if "n_tracks" not in st.session_state:
    st.session_state["n_tracks"] = 20

if "n_artists" not in st.session_state:
    st.session_state["n_artists"] = 20

with tab_tracks:
    n = st.session_state["n_tracks"]
    total = len(grouped_tracks)

    st.dataframe(
        grouped_tracks.head(n),
        width="stretch",
        hide_index=True,
        height=(len(grouped_tracks.head(n)) + 1) * 35 + 3,
        column_config={
            "track_name": st.column_config.TextColumn("Track name"),
            "artist_name": st.column_config.TextColumn("Artist"),
            "plays": st.column_config.NumberColumn("Plays"),
            "skips": st.column_config.NumberColumn("Skips"),
            "skip_rate": st.column_config.NumberColumn("Skip rate", format="percent",
                help="Percentage of plays that were skipped."),
            "dislike_score": st.column_config.NumberColumn("Dislike score",
                help="skips³ / plays²"),
        }
    )

    if n < total:
        _, center, _ = st.columns([2, 1, 2])
        with center:
            if st.button(f"See more (showing {n} of {total})", key="btn_tracks"):
                st.session_state["n_tracks"] += 20
                st.rerun()

with tab_artists:
    n = st.session_state["n_artists"]
    total = len(grouped_artists)

    st.dataframe(
        grouped_artists.head(n),
        width="stretch",
        hide_index=True,
        height=(len(grouped_artists.head(n)) + 1) * 35 + 3,
        column_config={
            "artist_name": st.column_config.TextColumn("Artist"),
            "plays": st.column_config.NumberColumn("Plays"),
            "skips": st.column_config.NumberColumn("Skips"),
            "skip_rate": st.column_config.NumberColumn("Skip rate", format="percent",
                help="Percentage of plays that were skipped."),
            "dislike_score": st.column_config.NumberColumn("Dislike score",
                help="skips³ / plays²"),
        }
    )

    if n < total:
        _, center, _ = st.columns([2, 1, 2])
        with center:
            if st.button(f"See more (showing {n} of {total})", key="btn_artists"):
                st.session_state["n_artists"] += 20
                st.rerun()