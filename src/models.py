from pydantic import BaseModel, Field, root_validator
from typing import List, Optional
from datetime import datetime
import numpy as np
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
    track_href: str
    key_mapped: Optional[str] = None

    def model_post_init(self, __context) -> None:
        """
        Initialize audio features object and perform scaling on selected fields.

        :param __context: A context object.
        :type __context: Any
        """

        key_mapping = {
            0: "C",
            1: "C#",
            2: "D",
            3: "D#",
            4: "E",
            5: "F",
            6: "F#",
            7: "G",
            8: "G#",
            9: "A",
            10: "A#",
            11: "B",
        }

        setattr(self, "key_mapped", key_mapping.get(getattr(self, "key")))

        # scaler = MinMaxScaler()

        # # Define the fields to scale
        # fields_to_scale = [
        #     "danceability",
        #     "energy",
        #     "acousticness",
        #     "instrumentalness",
        #     "valence",
        # ]

        # # Create a list of values for scaling
        # values_to_scale = [getattr(self, field) for field in fields_to_scale]

        # # Perform scaling
        # scaled_values = scaler.fit_transform(np.array([values_to_scale]).T)

        # # Update the corresponding fields with scaled values
        # for field, scaled_value in zip(fields_to_scale, scaled_values):
        #     setattr(self, field, scaled_value[0])


class Track(BaseModel):
    id: str
    name: str
    artists: List[Artist]
    features: Optional[AudioFeatures] = Field(default_factory=dict)


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


class TracksClustered(AudioFeatures):
    track_cluster: int
    cluster_name: str


class UserData(BaseModel):
    id: int
    playlists: List[Playlist]
    saved_tracks: Optional[SavedTracks] = Field(default=None)
    clustered_tracks: Optional[List[TracksClustered]] = Field(default=None)
