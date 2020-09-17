import pandas as pd
import numpy as np
import plotly.graph_objects as go 
import json
from plotly.utils import PlotlyJSONEncoder


class Plot3D:
    def __init__(self,audio_df,n_clusters, cluster_stats):
        self.df = audio_df
        self.n_clusters = n_clusters
        self.cluster_stats = cluster_stats

    def scatter3d(self, x_ax,y_ax,z_ax):

        data = [go.Scatter3d(x=self.df[x_ax], y=self.df[y_ax], z=self.df[z_ax],
                             mode='markers',
                             customdata=self.df['song_name'],
                             hovertemplate= "{x_ax}: %{x} <br> {y_ax}: %{y} </br> {z_ax}: %{z} <br> song: %{customdata}",
                             marker=dict(
                                 size=12,
                                 color=self.df['cluster'],
                                 colorscale='Viridis'
                             ))]

        layout = {'scene': {'xaxis' : {'title': x_ax},
            'yaxis' : {'title': y_ax},
            'zaxis' : {'title' :z_ax}},
            'widht': 700,
            'height': 700}

        plot_3d = json.dumps(data, cls=PlotlyJSONEncoder)

        layout = json.dumps(layout)

        return plot_3d, layout

    def radar_subplot(self):

        categories = self.cluster_stats.loc[:, self.cluster_stats.columns != 'cluster'].columns

        data = []

        for i in range(0,self.n_clusters):
            trace = [go.Scatterpolar(
                r=[self.cluster_stats.loc[i]['danceability'], self.cluster_stats.loc[i]['energy'], self.cluster_stats.loc[i]['loudness'],
                self.cluster_stats.loc[i]['speechiness'], self.cluster_stats.loc[i]['acousticness'], self.cluster_stats.loc[i]['instrumentalness'],
                self.cluster_stats.loc[i]['liveness'], self.cluster_stats.loc[i]['valence'], self.cluster_stats.loc[i]['tempo']],
                theta=categories,
                fill='toself',
                name=f'Cluster {i}'
            )]
            data.append(json.dumps(trace, cls=PlotlyJSONEncoder))

        layout = {
            'grid': {'rows': 1, 'columns': 4, 'pattern': 'independent'}
        }

        data = json.dumps(data)


        return data[0],data[1],data[2],data[3]
        










