import pandas as pd
import numpy as np
import json

from pydantic import BaseModel, Field, root_validator
from typing import List, Optional, Dict
from models import UserData


class Plot(BaseModel):
    data: Field[Dict]


class Plots(BaseModel):
    number_of_tracks: int
    number_of_clusters: int
    radar_chart: Plot
    pie_chart: Plot
    top_artist: Plot
    saved_tracks_timeline: Plot
    scatter_chart: Plot
    user_model: UserData


class Plot:
    def __init__(self, audio_df):
        self.audio_ft = audio_df

    def radar_chart(self, user_data):
        _df = pd.DataFrame([track.model_dump() for track in user_data.clustered_tracks])

        _plot = {}

        for c in _df.columns:
            _plot[c] = _df[c].to_list()

        return _plot

    def pie_chart(self, clusters):
        df_pie_chart = (
            clusters.groupby("cluster_name")[["spotify_user_id"]]
            .count()
            .reset_index()
            .rename(columns={"spotify_user_id": "number_of_songs"})
        )

        return df_pie_chart.to_dict("list")

    def top_3_artist(self, clusters):
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

    def saved_tracks_timeline(self, saved_tracks):
        saved_tracks["added_at"] = saved_tracks["added_at"].apply(
            lambda x: pd.Timestamp(x)
        )

        saved_tracks["yyyy-mm"] = saved_tracks["added_at"].dt.strftime("%Y-%m")

        timeline = saved_tracks.groupby(["yyyy-mm"])[self.audio_ft].mean().reset_index()

        return timeline.to_dict("list")

    def scatter_chart(self, tracks):
        scatter_dict = {}

        for cluster in list(tracks["cluster_name"].unique()):
            scatter_dict.update(
                {
                    cluster: tracks[tracks.cluster_name == cluster][
                        self.audio_ft + ["title"]
                    ].to_dict("list")
                }
            )

        return scatter_dict
