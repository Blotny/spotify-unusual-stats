from db.models import Base
from db.session import engine

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)