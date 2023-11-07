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


def top_3_artist(clusters):
    gb = (
        clusters.groupby("cluster_name")["artist"]
        .value_counts()
        .groupby(level=0)
        .head(3)
        .sort_values(ascending=False)
        .to_frame("counts")
        .reset_index()
    )

    return gb.sort_values(by="cluster_name", ascending=False).to_dict("list")


def saved_tracks_timeline(saved_tracks):
    saved_tracks["added_at"] = saved_tracks["added_at"].apply(lambda x: pd.Timestamp(x))

    saved_tracks["yyyy-mm"] = saved_tracks["added_at"].dt.strftime("%Y-%m")

    timeline = saved_tracks.groupby(["yyyy-mm"])[self.audio_ft].mean().reset_index()

    return timeline.to_dict("list")


def generate_scatter_chart(user_data):
    _df = pd.DataFrame([track.model_dump() for track in user_data.clustered_tracks])

    _scatter_dict = {}

    for cluster in _df["cluster_name"].unique():
        _scatter_dict.update(
            {cluster: _df[_df.cluster_name == cluster].to_dict("list")}
        )

    return Plot(data=_scatter_dict)
