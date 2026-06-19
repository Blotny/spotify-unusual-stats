from sqlalchemy.orm import sessionmaker
from db.models import Upload, Event
from db.session import engine


Session = sessionmaker(bind=engine)
session = Session()


def load_dataframe(session, df, filename):
    upload = Upload(filename=filename)

    session.add(upload)
    session.flush()
    
    dicts = df.to_dict(orient="records")

    for event in dicts:
        event["upload_id"] = upload.id
    
    session.bulk_insert_mappings(Event, dicts)
    session.commit()

    return upload.id
        


    

    