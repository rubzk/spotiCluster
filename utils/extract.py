import pandas as pd
import requests
import numpy as np
import base64
from utils.code_tools import transform_to_64, split_list


def authenticate(auth_code, client_id, client_secret, redirect_uri):

    headers = {"Authorization" : "Basic {}".format(transform_to_64(client_id+':'+client_secret))}
    body = {"grant_type": "authorization_code", "code": auth_code, "redirect_uri": redirect_uri}

    auth_token = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=body).json()['access_token']

    headers = {'Authorization': "Bearer {}".format(auth_token)}

    user_id = requests.get('https://api.spotify.com/v1/me', headers=headers).json()['id']

    return auth_token, user_id


def extract_all_playlist(auth_token, limit=20, offset=0):


    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json',
               'Authorization': 'Bearer {}'.format(auth_token)}

    
    playlists = requests.get('https://api.spotify.com/v1/me/playlists?'+'limit={}'.format(limit)+'&offset={}'.format(offset), headers=headers).json()['items']

    playlists_id = [playlist['id'] for playlist in playlists]

    return playlists_id


def extract_all_tracks(auth_token, playlists):

    limit = 100

    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json',
               'Authorization': 'Bearer {}'.format(auth_token)}

    tracks_info = pd.DataFrame([], columns=['id','name','artist'])

    
    tracks = []

    for playlist in playlists:
        ## Request to get limit 

        response = requests.get('https://api.spotify.com/v1/playlists/{}/tracks?fields=total%2Climit&limit={}'.format(playlist, limit), headers=headers).json()


        repeat = 1

        if response['total'] > limit:
            repeat = (response['total'] // limit ) + 1

        for r in range(repeat):
            d = requests.get('https://api.spotify.com/v1/playlists/{}/tracks?fields=items(track(id,name,artists))&limit={}&offset={}'.format(playlist,limit,r*limit), headers=headers).json()
            for track in d['items']:
                d_tracks = {'id': track['track']['id'], 'name': track['track']['name'], 'artist': track['track']['artists'][0]['name']}
                tracks_info = tracks_info.append(d_tracks, ignore_index=True)

    tracks_info = tracks_info.dropna(how='any', subset=['id'])

    return tracks_info


def get_audio_features(auth_token, df_tracks):

    df_audio_ft = pd.DataFrame([], columns=['danceability','energy','key','loudness','mode','speechiness','acousticness','instrumentalness','liveness',
                                   'valence','tempo','type','id','uri','track_href','analysis_url','duration_ms','time_signature'])

    headers = {'Authorization': "Bearer {}".format(auth_token)}

    tracks_ids = df_tracks['id'].to_list()

    if len(tracks_ids) > 100:
        list_of_ids = split_list(tracks_ids, round(len(tracks_ids)/100)+1)
    else:
        list_of_ids = split_list(tracks_ids,1)

    for tracks in list_of_ids:

        response = requests.get('https://api.spotify.com/v1/audio-features?ids={}'.format(str(tracks)[1:-1].replace("'","").replace(", ",",")), headers=headers).json()['audio_features']
        df_audio_ft = df_audio_ft.append(response, ignore_index=True)
    
    return df_audio_ft





    

