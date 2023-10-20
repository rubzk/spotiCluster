from pydantic import BaseModel, Field
from typing import List, Optional


class Artist(BaseModel):
    id: str
    name: str
    type: str


class AudioFeatures(BaseModel):
    track_id: str
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


class Track(BaseModel):
    id: str
    name: str
    artist: List[Artist]
    features: Optional[AudioFeatures] = Field(default_factory=dict)


class Playlist(BaseModel):
    id: str
    type: str
    public: bool
    tracks: List[Track]


class UserData(BaseModel):
    id: int
    playlists: List[Playlist]
