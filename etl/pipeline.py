from etl.load import load_dataframe
from etl.parser import extract_streaming_history
from etl.transform import to_dataframe, add_skip_column
from db.session import SessionLocal

def pipeline(zip_file):
    events = extract_streaming_history(zip_file)
    df = to_dataframe(events)
    df = add_skip_column(df)

    session = SessionLocal()
    filename = getattr(zip_file, "name", zip_file)
    upload_id = load_dataframe(session, df, filename)
    session.close()

    return upload_id