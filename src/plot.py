import pandas as pd
import numpy as np
import json



class Plot:
    def __init__(self, audio_df):
        self.audio_ft = audio_df


    def radar_chart(self,cluster_stats):

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
        gb = clusters.groupby('cluster_name')['artist'].value_counts().groupby(level=0).head(3).sort_values(ascending=False).to_frame('counts').reset_index()

        return gb.sort_values(by="cluster_name", ascending=False).to_dict("list")


