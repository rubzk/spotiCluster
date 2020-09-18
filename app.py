import json
from flask import Flask, render_template, redirect, url_for, request
import requests 
from utils.extract import DataExtractor
import credentials
from utils.transform import TransformDataFrame
from src.plot import Plot3D


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', auth_url=credentials.auth_url)


@app.route('/auth_ok/', methods=['GET', 'POST'])
def auth_ok():

    extractor = DataExtractor(credentials.client_id, credentials.client_secret, credentials.redirect_uri, 50)

    transform = TransformDataFrame(extractor.df_tracks_info, extractor.df_audio_ft)

    plotter = Plot3D(transform.final_df, transform.n_clusters, transform.cluster_stats)


    new = plotter.scatter_3d('danceability', 'valence', 'energy')

    polar= plotter.radar_chart()

    return render_template('plot.html', plot=new , radar=polar)

if __name__ == '__main__':
    app.run(debug=True)



