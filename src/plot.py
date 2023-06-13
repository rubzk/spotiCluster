import pandas as pd
import numpy as np
import json


class Plot:
    def __init__(self, audio_df):
        self.audio_ft = audio_df

    def radar_chart(self, cluster_stats):
        plot = {}

        for c in cluster_stats.columns:
            plot[c] = cluster_stats[c].to_list()

        return plot

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
                        self.audio_ft
                    ].to_dict("list")
                }
            )

        return scatter_dict
