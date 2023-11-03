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

    def model_post_init(self, __context) -> None:
        scaler = MinMaxScaler()

        # Define the fields to scale
        fields_to_scale = ["danceability", "energy", "instrumentalness", "valence"]

        # Create a list of values for scaling
        values_to_scale = [getattr(self, field) for field in fields_to_scale]

        # Perform scaling
        scaled_values = scaler.fit_transform(np.array([values_to_scale]).T)

        # Update the corresponding fields with scaled values
        for field, scaled_value in zip(fields_to_scale, scaled_values):
            setattr(self, field, scaled_value[0])


class Track(BaseModel):
    id: str
    name: str
    artists: List[Artist]
    features: Optional[AudioFeatures] = Field(default_factory=dict)

    def scale_features(self):
        scaler = MinMaxScaler()

        scaled_values = scaler.fit_transform(
            [[self.features.danceability, self.features.energy, self.features.valence]]
        )

        scaled_audio_ft = AudioFeatures(
            track_id=self.features.track_id,
            danceability=scaled_values[0],
            energy=scaled_values[1],
            valence=scaled_values[2],
            key=self.features.key,
            loudness=self.features.loudness,
            mode=self.features.mode,
            speechiness=self.features.speechiness,
            acousticness=self.features.acousticness,
            instrumentalness=self.features.instrumentalness,
            liveness=self.features.liveness,
            tempo=self.features.tempo,
            duration_ms=self.features.duration_ms,
            time_signature=self.features.time_signature,
        )

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


class TracksClustered(BaseModel):
    id: int
    features: AudioFeatures
    cluster_id: int
    cluster_label: str
