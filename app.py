import json
from flask import Flask, render_template, redirect, url_for, request
import requests 
from utils.extract import authenticate, extract_all_playlist, extract_all_tracks, get_audio_features
import credentials

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', auth_url =credentials.auth_url)


@app.route('/auth_ok/', methods=['GET', 'POST'])
def auth_ok():
    auth_code = request.args.get('code')
    auth_token, user_id = authenticate(auth_code, credentials.client_id, credentials.client_secret,credentials.redirect_uri)


    playlists = extract_all_playlist(auth_token, limit=50, offset=0)

    tracks = extract_all_tracks(auth_token, playlists)

    audio_ft = get_audio_features(auth_token, tracks)

    return '{}'.format(audio_ft)


if __name__ == '__main__':
    app.run(debug=True)

