from event_api.db.postgres import engine
from event_api.db.models import Base


def create_tables():
    """
    Create all PostgreSQL tables
    """
    Base.metadata.create_all(bind=engine)
    print("PostgreSQL tables created successfully.")

def drop_tables():
    """
    Drop all PostgreSQL tables
    """
    Base.metadata.drop_all(bind=engine)
    print("PostgreSQL tables dropped successfully.")