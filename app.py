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


    plot3d_one = plotter.scatter_3d('danceability', 'valence', 'energy')

    plot3d_two = plotter.scatter_3d('loudness', 'tempo', 'acousticness')

    plot3d_three = plotter.scatter_3d('speechiness', 'acousticness', 'instrumentalness')

    plot3d_four = plotter.scatter_3d('tempo', 'energy', 'loudness')


    polar= plotter.radar_chart()

    return render_template('plot.html', plot1=plot3d_one, plot2=plot3d_two,plot3=plot3d_three, plot4=plot3d_four, radar=polar)

if __name__ == '__main__':
    app.run(debug=True)



