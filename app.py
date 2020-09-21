import json
from flask import Flask, render_template, redirect, url_for, request, jsonify
import requests 
from utils.extract import DataExtractor
import credentials
from utils.transform import TransformDataFrame
from src.plot import Plot3D
from plotly.utils import PlotlyJSONEncoder



app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', auth_url=credentials.auth_url)


@app.route('/auth_ok/', methods=['GET', 'POST'])
def auth_ok():

    extractor = DataExtractor(credentials.client_id, credentials.client_secret, credentials.redirect_uri, 50)

    transform = TransformDataFrame(extractor.df_tracks_info, extractor.df_audio_ft)

    plotter = Plot3D(transform.final_df, transform.n_clusters, transform.cluster_stats)


    form_data = {'polar': plotter.radar_chart(),
                 'scatter3d': {
                     1: plotter.scatter_3d('danceability', 'valence', 'energy'),
                     2: plotter.scatter_3d('loudness', 'tempo', 'acousticness'),
                     3: plotter.scatter_3d('speechiness', 'acousticness', 'instrumentalness'),
                     4: plotter.scatter_3d('tempo', 'energy', 'loudness')
                 },
                 'keys_bar': plotter.bar_chart({'x':plotter.df['key'].value_counts().values ,
                                                'y': plotter.df['key'].value_counts().index.to_list(),
                                                'color': plotter.df['key'].value_counts().index.to_list(),
                                                'orientation': 'h',
                                                'width': 450,
                                                'height': 450,
                                                'layout': {
                                                    'title': 'Key Appearence',
                                                    'xaxis': 'Number of keys',
                                                    'yaxis': 'Keys'
                                                }}),
                 'mode_bar': plotter.bar_chart({'x':plotter.df['mode'].value_counts().index.to_list() ,
                                                'y': plotter.df['mode'].value_counts().values,
                                                'color': plotter.df['mode'].value_counts().index.to_list(),
                                                'orientation': 'v',
                                                'width': 450,
                                                'height': 450,
                                                'layout': {
                                                    'title': 'Mode of songs',
                                                    'xaxis': 'Mode type ',
                                                    'yaxis': 'Count'
                                                }}),
                 'cluster_bar': plotter.bar_chart({'x':plotter.df['cluster_name'].value_counts().values ,
                                                'y': plotter.df['cluster_name'].value_counts().index.to_list(),
                                                'color': plotter.df['cluster_name'].value_counts().index.to_list(),
                                                'orientation': 'h',
                                                'width': 450,
                                                'height': 450,
                                                'layout': {
                                                    'title': 'Cluster Classes',
                                                    'xaxis': 'Count',
                                                    'yaxis': 'Cluster number'
                                                }})}

    return render_template('plot.html', form=json.dumps(form_data, cls=PlotlyJSONEncoder))

if __name__ == '__main__':
    app.run(debug=True)



