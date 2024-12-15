# create_database.py

from sqlalchemy import create_engine
from database.models_v3 import Base  # Ensure models_v3.py is in the same directory or adjust the import path accordingly

def create_database():
    engine = create_engine("sqlite:///brew_and_bitev3.db")
    Base.metadata.create_all(engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    create_database()
