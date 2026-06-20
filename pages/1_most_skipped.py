from db.session import SessionLocal
from db.models import Event
import streamlit as st
import pandas as pd

if "upload_id" not in st.session_state:
    st.warning("Load file on main page.")
    st.stop()

upload_id = st.session_state["upload_id"]


@st.cache_data
def load_events_df(upload_id):
    session = SessionLocal()
    events = session.query(Event).filter(Event.upload_id == upload_id).all()
    session.close()

    data = [
        {
            "ts": e.ts,
            "track_name": e.track_name,
            "artist_name": e.artist_name,
            "ms_played": e.ms_played,
            "reason_end": e.reason_end,
            "spotify_is_skip": e.spotify_is_skip
        }
        for e in events
    ]
    return pd.DataFrame(data)


df = load_events_df(upload_id)

df["year"] = df["ts"].dt.year
avaible_years = sorted(df["year"].unique())

if "pills_years" not in st.session_state:
    st.session_state["pills_years"] = avaible_years

# button all
if st.button("All"):
    st.session_state["pills_years"] = avaible_years

# buttony dla lat
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
use_raw_skips = st.checkbox("Show all Spotify-flagged skips (ignore duration)")


# warunek z reason_end jest spowodowany nie zaliczaniem przez spotify
# wielu skipów w latach 2018-2022 gdzie reason end było forward lub
# back button ale skipped False

if use_raw_skips:
    df["is_skip"] = (df["spotify_is_skip"] |df["reason_end"].isin(["fwdbtn", "backbtn"]))
else:
    max_skip_seconds = st.slider("Max seconds to count as skip:", 1, 60, 30)
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


grouped["skip_rate"] = grouped["skips"] / grouped["plays"]

# odrzucenie utworow odtworzonych mniej niz 3 razy
grouped = grouped[grouped["plays"] >= 3]

# wybor opcji sortowania
sort_mode = st.radio(
    "Sort by:",
    ["Count of skips", "Skip rate"]
)

if sort_mode == "Skip rate":
    grouped = grouped.sort_values(["skip_rate", "skips"], ascending=False)
else:
    grouped = grouped.sort_values("skips", ascending=False)


st.dataframe(grouped.head(50), width="stretch", hide_index=True)
