import pandas as pd
import numpy as np
import plotly.graph_objects as go 
import json
from plotly.utils import PlotlyJSONEncoder
import plotly.io as io
import plotly.express as px



class Plot3D:
    def __init__(self,audio_df,n_clusters, cluster_stats):
        self.df = audio_df
        self.df['size'] = 3
        self.n_clusters = n_clusters
        self.cluster_stats = cluster_stats

    def scatter_3d(self, x_ax, y_ax, z_ax):

        fig = px.scatter_3d(self.df, x=x_ax, y=y_ax, z=z_ax, color='cluster', hover_data=['song_name'], width=800, height=800, size='size')

        self.df.to_csv('output.csv')

        return fig

    def radar_chart(self):

        categories = self.cluster_stats.loc[:,self.cluster_stats.columns != 'cluster'].columns

        fig = go.Figure()

        for i in range(0,self.n_clusters):

            fig.add_trace(go.Scatterpolar(
                r=[self.cluster_stats.loc[i]['danceability'], self.cluster_stats.loc[i]['energy'], self.cluster_stats.loc[i]['loudness'],
                self.cluster_stats.loc[i]['speechiness'], self.cluster_stats.loc[i]['acousticness'], self.cluster_stats.loc[i]['instrumentalness'],
                self.cluster_stats.loc[i]['liveness'], self.cluster_stats.loc[i]['valence'], self.cluster_stats.loc[i]['tempo']],
                theta=categories,
                fill='toself',
                name=f'Cluster {i}'
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0,1]
                )
            ),
            showlegend=True,
            width=600,
            height=600
        )

        return fig

    def bar_chart(self, data):

        fig = px.bar(x=data['x'], y=data['y'], orientation=data['orientation'], color=data['color'], width=data['width'], height=data['height'])

        fig.update_layout(title=data['layout']['title'],
                          xaxis=dict(title=data['layout']['title']),
                          yaxis=dict(title=data['layout']['title']))
        
        return fig

    def scatter_matrix(self, data:

        fig = px.scatter_matrix(data=self.df, dimensions=data['dimensions'], color=data['color'])

        return fig




        










