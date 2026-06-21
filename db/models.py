from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    file_hash = Column(String(64), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    events = relationship("Event", back_populates="upload")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"))
    ts = Column(DateTime)
    platform = Column(String)
    ms_played = Column(Integer)
    conn_country = Column(String)
    track_name = Column(String)
    artist_name = Column(String)
    album_name = Column(String)
    track_uri = Column(String)
    reason_start = Column(String)
    reason_end = Column(String)
    shuffle = Column(Boolean)
    spotify_is_skip = Column(Boolean)
    offline = Column(Boolean)
    incognito_mode = Column(Boolean)

    upload = relationship("Upload", back_populates="events")
