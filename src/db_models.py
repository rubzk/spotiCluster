from sqlmodel import SQLModel, Field, create_engine, Session
from typing import List, Optional
from datetime import datetime
import os 


def create_db_and_tables(sql_url):
    print(sql_url)
    engine = create_engine(sql_url,echo=True)
    SQLModel.metadata.create_all(engine)

class UserResults(SQLModel, table=True):
    __tablename__ = "user_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: str
    created: datetime


