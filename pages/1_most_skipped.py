from db.session import SessionLocal
from db.models import Event
import streamlit as st
import pandas as pd

if "upload_id" not in st.session_state:
    st.warning("Load file on main page.")
    st.stop()

upload_id = st.session_state["upload_id"]

session = SessionLocal()
events = session.query(Event).filter(Event.upload_id == upload_id).all()
session.close()

st.write(len(events))


data = [
    {"ts":e.ts, "track_name": e.track_name, "artist_name": e.artist_name, "is_skip": e.is_skip}
    for e in events
]

df = pd.DataFrame(data)

df["year"] = df["ts"].dt.year
avaible_years = sorted(df["year"].unique())

if "selected_years" not in st.session_state:
    st.session_state["selected_years"] = avaible_years


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
    ["Skip rate", "Count of skips"]
)

if sort_mode == "Skip rate":
    grouped = grouped.sort_values(["skip_rate", "skips"], ascending=False)
else:
    grouped = grouped.sort_values("skips", ascending=False)



st.dataframe(grouped.head(20), width="stretch", hide_index=True)