import pandas as pd
import requests
import numpy as np
import base64
from utils.code_tools import transform_to_64, split_list
from flask import request
import requests
import json


class DataExtractor:
    """A class to extract data from the Spotify-API

    ...

    Attributes
    ----------
    client_id : str
        API requirement to make requests.
    client_secret : str
        API secret requirement to make requests.
    redirect_uri : str
        The redirect URI after the auth process.
    limit : int
        The limit number of results delivered by the request.
    auth_code : str
        Code retrieved by the auth process.

    Methods
    -------
    get_auth_token():
        Gets the auth token necessary to get data from the user.
    get_user_id():
        Gets the user id with the auth token.
    get_all_playlists(, offset=0):
        Gets all the playlist ids from the users.
    get_all_tracks():
        Gets all the tracks from the playlists.
    get_all_audio_features():
        Gets all the audio features from the tracks.

    """

    def __init__(self, client_id, client_secret,
                 redirect_uri, limit, auth_code):
        
        
        self.limit = limit
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__redirect_uri = redirect_uri
        self.__auth_code = auth_code
        self.__auth_token = self.get_auth_token()
        self.user_id = self.get_user_id()
        self.playlists_id = self.get_all_playlists()
        self.df_tracks_info = self.get_all_tracks()
        self.df_audio_ft = self.get_all_audio_features()


    def get_auth_token(self):
        """
        
        Gets the auth token necessary to get data from the user.

        """

        headers = {"Authorization" : f"Basic {transform_to_64(self.__client_id+':'+self.__client_secret)}"}

        body = {"grant_type": "authorization_code", "code": self.__auth_code, "redirect_uri": self.__redirect_uri}

        return requests.post('https://accounts.spotify.com/api/token', headers=headers, data=body).json()['access_token']
    
    def get_user_id(self):
        """ 

        Gets the user id with the auth token.

        """

        headers = {'Authorization': f"Bearer {self.__auth_token}"}

        return requests.get('https://api.spotify.com/v1/me', headers=headers).json()['id']

    def get_all_playlists(self, offset=0):

        """

        Gets all the playlist ids from the users.

        Parameters
        ----------
            offset : int
                The index of the first playlist to return. Default: 0
        """

        headers = {'Accept': 'application/json',
               'Content-Type': 'application/json',
               'Authorization': f'Bearer {self.__auth_token}'}

        playlists = requests.get('https://api.spotify.com/v1/me/playlists?'+'limit={}'.format(self.limit)+'&offset={}'.format(offset), headers=headers).json()['items']

        playlists_id = [playlist['id'] for playlist in playlists]

        return playlists_id

    def get_all_tracks(self):

        """

        Gets all the tracks from the playlists.

        """

        headers = {'Accept': 'application/json',
               'Content-Type': 'application/json',
               'Authorization': f'Bearer {self.__auth_token}'}

        
        tracks_info = pd.DataFrame([], columns=['id','name','artist'])

        tracks = []

        for playlist in self.playlists_id:

            response = requests.get(f'https://api.spotify.com/v1/playlists/{playlist}/tracks?fields=total%2Climit&limit={self.limit}', headers=headers).json()

            repeat = 1

            if response['total'] > self.limit:
                repeat = (response['total'] // self.limit) + 1

            for r in range(repeat):
                d = requests.get(f'https://api.spotify.com/v1/playlists/{playlist}/tracks?fields=items(track(id,name,artists))&limit={self.limit}&offset={r * self.limit}', headers=headers).json()
                for track in d['items']:
                    d_tracks = {'id': track['track']['id'], 'name': track['track']['name'], 'artist': track['track']['artists'][0]['name']}
                    tracks_info = tracks_info.append(d_tracks, ignore_index=True)
        
        tracks_info = tracks_info.dropna(how='any', subset=['id'])

        tracks_info = tracks_info.drop_duplicates(subset=['id'], keep='first')

        return tracks_info

    
    def get_all_audio_features(self):

        """

        Gets all the audio features from the tracks and return a data frame


        """

        df_audio_ft = pd.DataFrame([], columns=['danceability','energy','key','loudness','mode','speechiness','acousticness','instrumentalness','liveness',
                                   'valence','tempo','type','id','uri','track_href','analysis_url','duration_ms','time_signature'])
        
        headers = {'Authorization': f"Bearer {self.__auth_token}"}

        tracks_ids = self.df_tracks_info['id'].to_list()

        if len(tracks_ids) > 100:
            list_of_ids = split_list(tracks_ids, round(len(tracks_ids)/100)+1)
        else:
            list_of_ids = split_list(tracks_ids,1)
        
        for tracks in list_of_ids:

            response = requests.get('https://api.spotify.com/v1/audio-features?ids={}'.format(str(tracks)[1:-1].replace("'","").replace(", ",",")), headers=headers).json()['audio_features']
            df_audio_ft = df_audio_ft.append(response, ignore_index=True)
        
        return df_audio_ft






    

