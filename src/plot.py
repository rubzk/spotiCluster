import pandas as pd
import numpy as np
import plotly.graph_objects as go 
import json
from plotly.utils import PlotlyJSONEncoder
import plotly.io as io
import plotly.express as px



class Plot3D:
    """A class to plot all the insights of the user's data

    ...

    Attributes
    ----------
    audio_df : dataframe
        Pandas Data Frame containing all the tracks and the audio features.
    n_clusters : int
        Number of clusters 
    clusters_stats : dataframe
        Pandas Data Frame with the stats of each cluster
    
    Methods
    -------
    scatter_3d(x_ax, 
               y_ax, z_ax,):
        Plot a Scatter3d Plot and return a plotly fig.
    radar_chart():
        Plot a RadarChar and return a plotly fig.
    bar_chart(data):
        Plot a BarChart and return a plotly fig.
    scatter_matrix(form):
        Plot Scatter Matrix and return a plotly fig.
    

    """
    def __init__(self,audio_df,n_clusters, cluster_stats):
        self.df = audio_df
        self.df['size'] = 3
        self.n_clusters = n_clusters
        self.cluster_stats = cluster_stats

    def scatter_3d(self, x_ax, y_ax, z_ax):

        """

        Plot a Scatter3d Plot and return a plotly fig.

        Parameters
        ----------
            x_ax : str
                The name of the column we want in the x axis.
            y_ax : str
                The name of the column we want in the y axis.
            z_ax : str
                The name of the column we want in the z axis.

        """

        fig = px.scatter_3d(self.df, x=x_ax, y=y_ax, z=z_ax, color='cluster', hover_data=['song_name'], width=600, height=600, size='size')

        self.df.to_csv('output.csv')

        return fig

    def radar_chart(self):

        """

        Plot a RadarChar and return a plotly fig.


        """

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
            height=600,
        )

        return fig

    def bar_chart(self, data):

        """

        Plot a BarChart and return a plotly fig.

        Parameters
        ----------
            data : dict
                Dictonary with settings for the plot such as x_axis, y_axis, orientation, etc.

    
        """

        fig = px.bar(x=data['x'], y=data['y'], orientation=data['orientation'], color=data['color'], width=data['width'], height=data['height'])

        fig.update_layout(title=data['layout']['title'],
                          xaxis=dict(title=data['layout']['title']),
                          yaxis=dict(title=data['layout']['title']))
        
        return fig

    def scatter_matrix(self, form):

        """

        Plot Scatter Matrix and return a plotly fig.

        Parameters
        ----------
            form : dict
                Dictonary with settings for the plot such as dimensions, color, widht and height.
        
        
        """

        fig = px.scatter_matrix(self.df, dimensions=form['dimensions'], color=form['color'], width=1400, height=800)

        return fig




        










