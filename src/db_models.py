from sqlmodel import SQLModel, Field, create_engine, Session
from typing import List, Optional
from datetime import datetime
import os 


def create_db_engine():
    try:
        db_url  = f'postgresql://{os.environ["POSTGRES_USER"]}:{os.environ["POSTGRES_PASSWORD"]}@{os.environ["POSTGRES_HOST"]}/{os.environ["POSTGRES_DB"]}'
        engine = create_engine(db_url, echo=True)
        return engine
    except Exception as e: 
        print(f"Couldn't create the connection: {e}")

def create_db_and_tables():
    engine = create_db_engine()
    SQLModel.metadata.create_all(engine)

def commit_results(results):

    engine = create_db_engine()

    with Session(engine) as session:
        for r in results:
            session.add(r)
        session.commit()


class UserResults(SQLModel, table=True):
    __tablename__ = "user_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: str
    created: datetime

