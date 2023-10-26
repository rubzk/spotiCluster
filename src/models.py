from pydantic import BaseModel, Field, root_validator
from typing import List, Optional
from datetime import datetime

from sklearn.preprocessing import MinMaxScaler


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
    artists: List[Artist]
    features: Optional[AudioFeatures] = Field(default_factory=dict)

    def scale_features(self):
        scaler = MinMaxScaler()

        scaled_audio_ft = AudioFeatures()

        return Track(
            id=self.id, name=self.name, artists=self.artists, features=scaled_audio_ft
        )


class SavedTrack(BaseModel):
    added_at: datetime
    artists: List[Artist]
    id: str
    name: str
    popularity: int
    features: Optional[AudioFeatures] = Field(default_factory=dict)


class Playlist(BaseModel):
    id: str
    type: str
    public: bool
    tracks: List[Track]


class SavedTracks(BaseModel):
    tracks: List[SavedTrack]


class UserData(BaseModel):
    id: int
    playlists: List[Playlist]
    saved_tracks: Optional[SavedTracks] = Field(default=None)
