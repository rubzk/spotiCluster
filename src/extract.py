import pandas as pd
import requests
import numpy as np
import base64
from utils.code_tools import transform_to_64, split_list
import requests
import json


class DataExtractor:
    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.limit = 50
        # self.user_id = self.get_user_id()
        # self.playlists_id = self.get_all_playlists()
        # self.df_tracks_info = self.get_all_tracks()
        # self.df_audio_ft = self.get_all_audio_features()

    def get_user_id(self):

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        return requests.get("https://api.spotify.com/v1/me", headers=headers).json()[
            "id"
        ]

    def get_all_playlists(self, offset=0):

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}",
        }

        playlists = requests.get(
            "https://api.spotify.com/v1/me/playlists?"
            + "limit={}".format(self.limit)
            + "&offset={}".format(offset),
            headers=headers,
        ).json()["items"]

        playlists_id = [playlist["id"] for playlist in playlists]

        return playlists_id

    def get_all_tracks_v2(self, playlist):

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}",
        }

        response = requests.get(
            f"https://api.spotify.com/v1/playlists/{playlist}/tracks?fields=total%2Climit&limit={self.limit}",
            headers=headers,
        ).json()

        repeat = 1

        tracks_info = pd.DataFrame([], columns=["id", "name", "artist"])

        if response["total"] > self.limit:
            repeat = (response["total"] // self.limit) + 1

        for r in range(repeat):
            d = requests.get(
                f"https://api.spotify.com/v1/playlists/{playlist}/tracks?fields=items(track(id,name,artists))&limit={self.limit}&offset={r * self.limit}",
                headers=headers,
            ).json()
            for track in d["items"]:
                d_tracks = {
                    "id": track["track"]["id"],
                    "name": track["track"]["name"],
                    "artist": track["track"]["artists"][0]["name"],
                }
                tracks_info = tracks_info.append(d_tracks, ignore_index=True)

        tracks_info = tracks_info.dropna(how="any", subset=["id"])

        tracks_info = tracks_info.drop_duplicates(subset=["id"], keep="first")

        return tracks_info

    def get_all_tracks(self):

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}",
        }

        tracks_info = pd.DataFrame([], columns=["id", "name", "artist"])

        tracks = []

        repeat = 1

        for playlist in self.playlists_id:

            response = requests.get(
                f"https://api.spotify.com/v1/playlists/{playlist}/tracks?fields=total%2Climit&limit={self.limit}",
                headers=headers,
            ).json()

            if response["total"] > self.limit:
                repeat = (response["total"] // self.limit) + 1

            for r in range(repeat):
                d = requests.get(
                    f"https://api.spotify.com/v1/playlists/{playlist}/tracks?fields=items(track(id,name,artists))&limit={self.limit}&offset={r * self.limit}",
                    headers=headers,
                ).json()
                for track in d["items"]:
                    d_tracks = {
                        "id": track["track"]["id"],
                        "name": track["track"]["name"],
                        "artist": track["track"]["artists"][0]["name"],
                    }
                    tracks_info = tracks_info.append(d_tracks, ignore_index=True)

        tracks_info = tracks_info.dropna(how="any", subset=["id"])

        tracks_info = tracks_info.drop_duplicates(subset=["id"], keep="first")

        return tracks_info

    def get_all_audio_features(self):

        df_audio_ft = pd.DataFrame(
            [],
            columns=[
                "danceability",
                "energy",
                "key",
                "loudness",
                "mode",
                "speechiness",
                "acousticness",
                "instrumentalness",
                "liveness",
                "valence",
                "tempo",
                "type",
                "id",
                "uri",
                "track_href",
                "analysis_url",
                "duration_ms",
                "time_signature",
            ],
        )

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        tracks_ids = self.df_tracks_info["id"].to_list()

        if len(tracks_ids) > 100:
            list_of_ids = split_list(tracks_ids, round(len(tracks_ids) / 100) + 1)
        else:
            list_of_ids = split_list(tracks_ids, 1)

        for tracks in list_of_ids:

            response = requests.get(
                "https://api.spotify.com/v1/audio-features?ids={}".format(
                    str(tracks)[1:-1].replace("'", "").replace(", ", ",")
                ),
                headers=headers,
            ).json()["audio_features"]
            df_audio_ft = df_audio_ft.append(response, ignore_index=True)

        return df_audio_ft

    def get_all_audio_features_v2(self, tracks):

        tracks_audio_ft = pd.DataFrame(
            [],
            columns=[
                "danceability",
                "energy",
                "key",
                "loudness",
                "mode",
                "speechiness",
                "acousticness",
                "instrumentalness",
                "liveness",
                "valence",
                "tempo",
                "type",
                "id",
                "uri",
                "track_href",
                "analysis_url",
                "duration_ms",
                "time_signature",
            ],
        )

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        tracks_ids = tracks["id"].to_list()

        if len(tracks_ids) > 100:
            list_of_ids = split_list(tracks_ids, round(len(tracks_ids) / 100) + 1)
        else:
            list_of_ids = split_list(tracks_ids, 1)

        for tracks in list_of_ids:

            response = requests.get(
                "https://api.spotify.com/v1/audio-features?ids={}".format(
                    str(tracks)[1:-1].replace("'", "").replace(", ", ",")
                ),
                headers=headers,
            ).json()["audio_features"]
            tracks_audio_ft = tracks_audio_ft.append(response, ignore_index=True)

        return tracks_audio_ft
