import pandas as pd
import numpy as np
import json

from pydantic import BaseModel, Field, root_validator
from typing import List, Optional, Any, Dict
from .models import UserData


class Plot(BaseModel):
    data: Dict


class Plots(BaseModel):
    number_of_tracks: int
    number_of_clusters: int
    radar_chart: Optional[Plot]
    pie_chart: Optional[Plot]
    scatter_chart: Optional[Plot]
    top_3_artist: Optional[Plot]
    saved_tracks_timeline: Optional[Plot]
    user_model: UserData


def generate_radar_chart(user_data):
    _df = pd.DataFrame([track.model_dump() for track in user_data.clustered_tracks])

    _plot = {}

    for c in _df.columns:
        _plot[c] = _df[c].to_list()

    return Plot(data=_plot)


def generate_pie_chart(user_data):
    _df = pd.DataFrame([track.model_dump() for track in user_data.clustered_tracks])

    _df_gb = (
        _df.groupby("cluster_name")[["track_id"]]
        .count()
        .reset_index()
        .rename(columns={"track_id": "number_of_tracks"})
    )

    return Plot(data=_df_gb.to_dict("list"))


def generate_top_3_artist(user_data):
    def get_top_artists(group):
        return group["artist_name"].value_counts().nlargest(3)

    _tracks_clustered = pd.DataFrame(
        [track.model_dump() for track in user_data.clustered_tracks]
    )

    _data = []

    for playlist in user_data.playlists:
        if playlist.tracks:
            for track in playlist.tracks:
                for artist in track.artists:
                    _data.append([track.id, artist.name])

    _artist_tracks = pd.DataFrame(_data, columns=["track_id", "artist_name"])

    _artist_tracks = _artist_tracks.merge(_tracks_clustered, how="left", on="track_id")

    top_artists_per_cluster = (
        _artist_tracks.groupby("cluster_name").apply(get_top_artists).reset_index()
    )

    top_artists_per_cluster.columns = ["cluster_name", "artist_name", "count"]

    top_artists_per_cluster = top_artists_per_cluster.to_dict("list")

    return Plot(data=top_artists_per_cluster)


def generate_saved_tracks_timeline(user_data):
    features = [
        "danceability",
        "energy",
        "loudness",
        "speechiness",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
        "tempo",
    ]

    _df = pd.DataFrame([track.model_dump() for track in user_data.saved_tracks.tracks])

    _df = pd.concat([_df, pd.json_normalize(_df["features"])], axis=1)

    _df["added_at"] = _df["added_at"].apply(lambda x: pd.Timestamp(x))

    _df["yyyy-mm"] = _df["added_at"].dt.strftime("%Y-%m")

    _timeline = _df.groupby(["yyyy-mm"])[features].mean().reset_index()

    _timeline = _timeline.to_dict("list")

    return Plot(data=_timeline)


def generate_scatter_chart(user_data):
    _df = pd.DataFrame([track.model_dump() for track in user_data.clustered_tracks])

    _scatter_dict = {}

    for cluster in _df["cluster_name"].unique():
        _scatter_dict.update(
            {cluster: _df[_df.cluster_name == cluster].to_dict("list")}
        )

    return Plot(data=_scatter_dict)
