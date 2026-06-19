from etl.parser import extract_streaming_history
from etl.transform import to_dataframe, add_skip_column
from etl.load import load_dataframe
from db.session import SessionLocal

zip_path = "test_data_spotify.zip"

events = extract_streaming_history(zip_path)
df = to_dataframe(events)
df = add_skip_column(df)

session = SessionLocal()
upload_id = load_dataframe(session, df, filename="test_upload.zip")
session.close()

print(f"Zapisano upload_id: {upload_id}")