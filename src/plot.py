import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
from plotly.utils import PlotlyJSONEncoder
import plotly.io as io
import plotly.express as px


class Plot:
    def __init__(self, audio_df):
        self.audio_ft = audio_df
        # self.df["size"] = 3
        # self.n_clusters = n_clusters
        # self.cluster_stats = cluster_stats

    def scatter_3d(self, x_ax, y_ax, z_ax):
        fig = px.scatter_3d(
            self.df,
            x=x_ax,
            y=y_ax,
            z=z_ax,
            color="cluster",
            hover_data=["song_name"],
            width=600,
            height=600,
            size="size",
        )

        self.df.to_csv("output.csv")

        return fig

    def radar_chart(self, cluster_stats):
        plot = {}

        cluster_stats = cluster_stats[["cluster_name"] + self.audio_ft]

        for cluster in range(cluster_stats.shape[0]):
            plot[cluster_stats.iloc[cluster]["cluster_name"]] = cluster_stats.iloc[
                cluster, cluster_stats.columns != "cluster_name"
            ].to_list()

        plot["categories"] = self.audio_ft

        return plot

    def bar_chart(self, data):
        fig = px.bar(
            x=data["x"],
            y=data["y"],
            orientation=data["orientation"],
            color=data["color"],
            width=data["width"],
            height=data["height"],
        )

        fig.update_layout(
            title=data["layout"]["title"],
            xaxis=dict(title=data["layout"]["title"]),
            yaxis=dict(title=data["layout"]["title"]),
        )

        return fig

    def scatter_matrix(self, form):
        fig = px.scatter_matrix(
            self.df,
            dimensions=form["dimensions"],
            color=form["color"],
            width=1400,
            height=800,
        )

        return fig
