from db.models import Upload


def find_upload_by_hash(session, file_hash):
    return session.query(Upload).filter(Upload.file_hash == file_hash).first()