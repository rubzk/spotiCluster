import pandas as pd
import numpy as np
import base64
from utils.code_tools import transform_to_64, split_list
import requests
import json


class DataExtractor:
    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.limit = 50
        self.headers = headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}",
        }
        self.test = self.get_all_saved_tracks()

    def get_user_id(self):
        return requests.get(
            "https://api.spotify.com/v1/me", headers=self.headers
        ).json()["id"]

    def get_all_playlists(self, offset=0):
        playlists = requests.get(
            "https://api.spotify.com/v1/me/playlists?"
            + "limit={}".format(self.limit)
            + "&offset={}".format(offset),
            headers=self.headers,
        ).json()["items"]

        playlists_id = [playlist["id"] for playlist in playlists]

        return playlists_id

    def get_all_tracks(self, playlist):
        response = requests.get(
            f"https://api.spotify.com/v1/playlists/{playlist}/tracks?fields=total%2Climit&limit={self.limit}",
            headers=self.headers,
        ).json()

        repeat = 1

        tracks_info = pd.DataFrame([], columns=["id", "name", "artist"])

        if response["total"] > self.limit:
            repeat = (response["total"] // self.limit) + 1

        for r in range(repeat):
            d = requests.get(
                f"https://api.spotify.com/v1/playlists/{playlist}/tracks?fields=items(track(id,name,artists))&limit={self.limit}&offset={r * self.limit}",
                headers=self.headers,
            ).json()
            for track in d["items"]:
                d_tracks = {
                    "id": track["track"]["id"],
                    "name": track["track"]["name"],
                    "artist": track["track"]["artists"][0]["name"],
                }
                tracks_info = pd.concat(
                    [tracks_info, pd.DataFrame([d_tracks])], ignore_index=True
                )

        tracks_info = tracks_info.dropna(how="any", subset=["id"])

        tracks_info = tracks_info.drop_duplicates(subset=["id"], keep="first")

        return tracks_info

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

        return saved_tracks_info

    def get_all_audio_features(self, tracks):
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
                headers=self.headers,
            ).json()["audio_features"]

            tracks_audio_ft = pd.concat(
                [tracks_audio_ft, pd.DataFrame(response)], ignore_index=True
            )

        return tracks_audio_ft
