import pandas
import requests
import numpy
import base64

def transform_to_64(code):
    return base64.urlsafe_b64encode(bytes(code, 'utf-8')).decode('utf-8')

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

    
    tracks = []

    for playlist in playlists:
        ## Request to get limit 

        response = requests.get('https://api.spotify.com/v1/playlists/{}/tracks?fields=total%2Climit&limit={}'.format(playlist, limit), headers=headers).json()


        repeat = 1

        if response['total'] > limit:
            repeat = (response['total'] // limit ) + 1

        for r in range(repeat):
            d = requests.get('https://api.spotify.com/v1/playlists/{}/tracks?fields=items(track(id))&limit={}&offset={}'.format(playlist,limit,r*limit), headers=headers).json()
            for track in d['items']:
                tracks.append(track['track']['id'])

    return tracks


    
    


    

