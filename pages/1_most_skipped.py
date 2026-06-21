from db.session import SessionLocal
from db.models import Event
import streamlit as st
import pandas as pd
from db.queries import load_events_df


st.set_page_config(layout="wide")

if "upload_id" not in st.session_state:
    st.warning("Load file on main page.")
    st.stop()

upload_id = st.session_state["upload_id"]

df = load_events_df(upload_id)

df["year"] = df["ts"].dt.year
avaible_years = sorted(df["year"].unique())

if "pills_years" not in st.session_state:
    st.session_state["pills_years"] = avaible_years

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
    # wielu skipów w latach 2018-2022 gdzie reason end było forward lub
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

    # agregacja
    grouped = df_filtered.groupby(["track_name", "artist_name"]).agg(
        plays=("is_skip", "count"),
        skips=("is_skip", "sum")
    ).reset_index()

    # metryki
    grouped["skip_rate"] = grouped["skips"] / grouped["plays"]
    grouped["dislike_score"] = (grouped["skips"] ** 2) / grouped["plays"]

    # odrzucenie utworow odtworzonych mniej niz 3 razy
    grouped = grouped[grouped["plays"] >= 3]

    # wybor opcji sortowania
    sort_mode = st.radio(
        "Sort by:",
        ["Count of skips", "Skip rate", "Dislike score"],
        horizontal=True,
        help="Dislike score = skips² / plays — combines how often you skip with how many real skips happened, weighting against tracks with few plays."
    )

    if sort_mode == "Skip rate":
        grouped = grouped.sort_values(["skip_rate", "skips"], ascending=False)
    elif sort_mode == "Dislike score":
        grouped = grouped.sort_values("dislike_score", ascending=False)
    else:
        grouped = grouped.sort_values("skips", ascending=False)

# skladanie dataframe

n_rows = len(grouped.head(50))
table_height = (n_rows + 1) * 35 + 3

st.dataframe(grouped.head(50), 
             width="stretch", 
             hide_index=True,
             height=table_height,
             column_config={
                 "track_name": st.column_config.TextColumn("Track name"),
                 "artist_name": st.column_config.TextColumn("Artist"),
                 "plays": st.column_config.NumberColumn("Plays"),
                 "skips": st.column_config.NumberColumn("Skips"),
                 "skip_rate": st.column_config.NumberColumn(
                     "Skip rate", 
                     format="percent", 
                     help="Percentage of plays that were skipped (skips / plays). Tracks with very few plays can show misleadingly extreme values (e.g. 1 play + 1 skip = 100%)."
                     ),
                 "dislike_score": st.column_config.NumberColumn(
                    "Dislike score",
                    help="skips² / plays — combines skip frequency with total skip count, naturally de-weighting low-sample tracks."
                    )
             })

