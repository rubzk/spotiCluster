from sqlmodel import SQLModel, Field, Column, BigInteger, JSON
from typing import List, Optional, Dict
from datetime import datetime
import os 
from uuid import UUID

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
    task_id: UUID
    plot_id: int
    result: dict = Field(sa_column=Column(JSON))
    created: datetime

    

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


class PlotTypes(SQLModel, table=True):
    __tablename__ = "plot_types"
    id: int = Field(primary_key=True)
    name: str


    
