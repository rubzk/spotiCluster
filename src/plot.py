import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import plotly.graph_objects as go 
import json
from plotly.utils import PlotlyJSONEncoder


class Plot3D:
    def __init__(self,audio_df,n_clusters):
        self.df = audio_df
        self.n_clusters = n_clusters
        self.features = ['danceability', 'energy', 'loudness', 'speechiness','acousticness','instrumentalness','liveness','valence','tempo']
        self.df['full_name'] = self.df['name'] + ' - ' + self.df['artist']
        self.df[self.features] = self.scale_features()

    def scale_features(self):

        scaler = MinMaxScaler()
        return scaler.fit_transform(self.df[self.features])

    def scatter3d(self, x_ax,y_ax,z_ax):

        data = [go.Scatter3d(x=self.df[x_ax], y=self.df[y_ax], z=self.df[z_ax],
                             mode='markers',
                             customdata=self.df['full_name'],
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
            'height': 1000}

        plot_3d = json.dumps(data, cls=PlotlyJSONEncoder)

        layout = json.dumps(layout)

        return plot_3d, layout







