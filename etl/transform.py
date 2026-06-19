import pandas as pd

def to_dataframe(events: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(events)

    # odrzucenie podcastow
    if "episode_name" in df.columns:
        df = df[df["episode_name"].isna()].copy()
    
    # wyrzucenie zbednych kolumn
    df = df.drop(columns=["ip_addr", "user_agent_decrypted", "episode_name", "episode_show_name", "spotify_episode_uri", "audiobook_title", "audiobook_uri", "audiobook_chapter_uri", "audiobook_chapter_title", "offline_timestamp"], errors="ignore")
    
    # zmienie nazw
    df = df.rename(columns={
        "master_metadata_track_name": "track_name",
        "master_metadata_album_artist_name": "artist_name",
        "master_metadata_album_album_name": "album_name",
        "spotify_track_uri": "track_uri",
        "skipped": "spotify_is_skip"
    })

    df["ts"] = pd.to_datetime(df["ts"])

    return df

'''
kolumna skipped (True lub False) jest niemiarodajna  w latach 2015-2022
(występują przypadki gdzie skipped nie zwracała True) wprowadzamy własną kolumnę
'''

def add_skip_column(df: pd.DataFrame) -> pd.DataFrame:
    df["is_skip"] = (
        (df["spotify_is_skip"] == True)
        | ((df["reason_end"].isin(["fwdbtn", "backbtn"])) & (df["ms_played"] < 30_000))
    )

    return df