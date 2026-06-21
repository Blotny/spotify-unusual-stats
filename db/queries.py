from db.models import Upload, Event
import streamlit as st
import pandas as pd
from db.session import SessionLocal


def find_upload_by_hash(session, file_hash):
    return session.query(Upload).filter(Upload.file_hash == file_hash).first()


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
            "spotify_is_skip": e.spotify_is_skip,
            "conn_country": e.conn_country,
        }
        for e in events
    ]
    return pd.DataFrame(data)