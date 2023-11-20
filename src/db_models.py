from sqlmodel import SQLModel, Field, create_engine, Session, Column, BigInteger, JSON
from typing import List, Optional, Dict
from datetime import datetime
import os 
from uuid import UUID
from src.plot import Plots

class TaskRuns(SQLModel, table=True):
    __tablename__ = "task_runs"
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: UUID
    user_id: int = Field(sa_column=Column(BigInteger()))
    number_of_tracks: Optional[int] = Field(default=None)
    started_at: datetime
    finished_at: datetime

class TaskResults(SQLModel, table=True):
    __tablename__ = "task_results"
    id: Optional[int] = Field(default=None, primary_key=True)
    taks_id: UUID
    results: Optional[int] = Field(default=None)
    number_of_tracks: int
    number_of_clusters: int

class UserPlaylists(SQLModel, table=True):
    __tablename__ = "user_playlists"
    id: int = Field(primary_key=True)
    user_id: int
    public: bool

class UserTracks(SQLModel, table=True):
    __tablename__ = "user_tracks"
    id: int = Field(primary_key=True)
    playlist_id: int
    name: str
    first_artist_id: int 
    second_artist_id: int
    features_id: int 
    cluster_name: str
    cluster_id: int 
    
class Features(SQLModel, table=True):
    __tablename__ = "audio_features"
    track_id: int = Field(primary_key=True)
    danceability: float
    energy: float
    key: int
    loudness: float
    mode: int
    speechiness: float
    acousticness: float
    instrumentalness: float
    liveness: float
    valence: float
    tempo: float
    duration_ms: int
    time_signature: int
    key_mapped: Optional[str] = None

class Artists(SQLModel, table=True):
    __tablename__ = "artists"
    artist_id: int = Field(primary_key=True)
    name: str
    type: str


class PlotResults(SQLModel, table=True):
    __tablename__ = "plot_results"
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: UUID
    plot_id: int
    result: Dict = Field(default={}, sa_column=Column(JSON))

class PlotTypes(SQLModel, table=True):
    __tablename__ = "plot_types"
    id: int = Field(primary_key=True)
    name: str

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

    
