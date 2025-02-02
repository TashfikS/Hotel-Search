from sqlalchemy import create_engine, MetaData
from sqlalchemy.exc import SQLAlchemyError
from app.models import Base

DATABASE_URL = "postgresql://admin:admin@db:5432/hotel_db"

def apply_migration():
    engine = create_engine(DATABASE_URL)
    metadata = MetaData()

    try:
        Base.metadata.create_all(engine)
        print("Migration applied successfully.")
    except SQLAlchemyError as e:
        print(f"Error applying migration: {e}")

if __name__ == "__main__":
    apply_migration()