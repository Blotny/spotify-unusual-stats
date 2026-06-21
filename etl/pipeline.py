from etl.load import load_dataframe
from etl.parser import extract_streaming_history, compute_file_hash
from etl.transform import to_dataframe
from db.session import SessionLocal
from db.queries import find_upload_by_hash


def pipeline(zip_file):
    file_hash = compute_file_hash(zip_file)
    session = SessionLocal()
    upload = find_upload_by_hash(session, file_hash)

    if upload:
        session.close()
        return upload.id

    events = extract_streaming_history(zip_file)
    df = to_dataframe(events)
    filename = getattr(zip_file, "name", zip_file)
    upload_id = load_dataframe(session, df, filename, file_hash)
    session.close()

    return upload_id
