import pandas as pd
import numpy as np
import base64
from utils.code_tools import transform_to_64, split_list
import requests
import json
import logging

from .models import UserData, Playlist, Artist, Track, AudioFeatures

log = logging.getLogger(__name__)


class DataExtractor:
    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.limit = 50
        self.headers = headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}",
        }
        # self.test = self.get_all_saved_tracks()

    def get_user_id(self):
        log.warning(
            requests.get("https://api.spotify.com/v1/me", headers=self.headers).json()
        )

        response = requests.get(
            "https://api.spotify.com/v1/me", headers=self.headers
        ).json()

        user_data = UserData(id=response["id"], playlists=[])

        return user_data

    def get_all_playlists(self, user_data, offset=0):
        response = requests.get(
            "https://api.spotify.com/v1/me/playlists?"
            + "limit={}".format(self.limit)
            + "&offset={}".format(offset),
            headers=self.headers,
        ).json()["items"]

        for p in response:
            user_data.playlists.append(
                Playlist(id=p["id"], type=p["type"], public=p["public"], tracks=[])
            )

        # playlists_id = [playlist["id"] for playlist in response]

        log.warning(user_data)

        return user_data

    def get_all_tracks(self, playlist):
        response = requests.get(
            f"https://api.spotify.com/v1/playlists/{playlist.id}/tracks?fields=total%2Climit&limit={self.limit}",
            headers=self.headers,
        ).json()

        log.warning(response)

        repeat = 1

        tracks_info = pd.DataFrame([], columns=["id", "name", "artist"])

        if response["total"] > self.limit:
            repeat = (response["total"] // self.limit) + 1

        for r in range(repeat):
            response = requests.get(
                f"https://api.spotify.com/v1/playlists/{playlist.id}/tracks?fields=items(track(id,name,artists))&limit={self.limit}&offset={r * self.limit}",
                headers=self.headers,
            ).json()

            for t in response["items"]:
                track_name = t["track"]["name"]
                track_id = t["track"]["id"]
                log.warning(t)
                track = Track(id=track_id, name=track_name, artists=[])

                for artist in t["track"]["artists"]:
                    artist_id = artist["id"]
                    artist_name = artist["name"]
                    artist_type = artist["type"]
                    track.artists.append(
                        Artist(id=artist_id, name=artist_name, type=artist_type)
                    )

                playlist.tracks.append(track)

        return playlist

    def get_all_saved_tracks(self):
        response = requests.get(
            "https://api.spotify.com/v1/me/tracks?", headers=self.headers
        ).json()

        if response["total"] > self.limit:
            repeat = (response["total"] // self.limit) + 1

        saved_tracks_info = pd.DataFrame(
            [], columns=["id", "name", "added_at", "artist", "preview_url"]
        )

        for r in range(repeat):
            d = requests.get(
                f"https://api.spotify.com/v1/me/tracks?limit{self.limit}&offset={r * self.limit}",
                headers=self.headers,
            ).json()

            with open("all_saved_response.json", "w") as json_file:
                json.dump(d, json_file)

            if d != None:
                for track in d["items"]:
                    d_tracks = {
                        "id": track["track"]["id"],
                        "name": track["track"]["name"],
                        "added_at": track["added_at"],
                        "artist": track["track"]["artists"][0]["name"],
                        "preview_url": track["track"]["preview_url"],
                    }
                    saved_tracks_info = pd.concat(
                        [saved_tracks_info, pd.DataFrame([d_tracks])], ignore_index=True
                    )
            else:
                continue

        return saved_tracks_info

    def get_all_audio_features(self, playlist):
        if len(playlist.tracks) > 100:
            splitted_list = split_list(
                playlist.tracks, round(len(playlist.tracks) / 100) + 1
            )
        else:
            splitted_list = split_list(playlist.tracks, 1)

        for track_list in splitted_list:
            track_ids = [track.id for track in track_list]
            response = requests.get(
                "https://api.spotify.com/v1/audio-features?ids={}".format(
                    str(track_ids)[1:-1].replace("'", "").replace(", ", ",")
                ),
                headers=self.headers,
            ).json()["audio_features"]

            for track, audio_feature in zip(track_list, response):
                ft_dict = {
                    "danceability": audio_feature["danceability"],
                    "energy": audio_feature["energy"],
                    "key": audio_feature["key"],
                    "loudness": audio_feature["loudness"],
                    "mode": audio_feature["mode"],
                    "speechiness": audio_feature["speechiness"],
                    "acousticness": audio_feature["acousticness"],
                    "instrumentalness": audio_feature["instrumentalness"],
                    "liveness": audio_feature["liveness"],
                    "valence": audio_feature["valence"],
                    "tempo": audio_feature["tempo"],
                    "track_id": audio_feature["id"],
                    "duration_ms": audio_feature["duration_ms"],
                    "time_signature": audio_feature["time_signature"],
                }

                audio_features = AudioFeatures(**ft_dict)
                track.features = audio_features

        tracks = [item for sublist in splitted_list for item in sublist]

        playlist.tracks = tracks

        return playlist
