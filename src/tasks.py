import json
import configparser

from src.auth import Authenticator
from src.extract import DataExtractor
from src.transform import TransformDataFrame
from src.clustering import Clustering
from src.plot import Plot


import pandas as pd
from celery import shared_task, chord, chain, group, current_app


@shared_task(bind=True, name="Get tracks", propagate=False)
def get_tracks(self, auth_token, playlist):

    data_extractor = DataExtractor(auth_token)

    tracks = data_extractor.get_all_tracks_v2(playlist)

    tracks_audio_ft = data_extractor.get_all_audio_features_v2(tracks)

    transform = TransformDataFrame(tracks, tracks_audio_ft)

    result = transform.concat_data()

    result = result.dropna(axis=0, how="any")

    return json.dumps(result.to_dict("list"))


@shared_task(bind=True, name="Process all the tracks", propagate=False)
def concatenate_all_tracks(self, auth_token):

    self.update_state(
        state="PROGRESS",
        meta={"current": 35, "total": 100, "status": "Processing All the tracks"},
    )

    extractor = DataExtractor(auth_token)

    playlists = extractor.get_all_playlists()

    total_tracks = [get_tracks.s(auth_token, playlist) for playlist in playlists]

    res = chord(total_tracks)(append_results.s())


    return {
        "current": 50,
        "total": 100,
        "status": "Finish Processing  all the tracks",
        "plot": res.id,
    }


@shared_task(bind=True, name="Append all the results")
def append_results(self, results):

    result = pd.DataFrame()

    for tracks in results:
        result = result.append(pd.read_json(tracks))

    result = result.dropna(axis=0, how="any", subset=["id"])

    result = result.drop(axis=1, columns="0")

    clustering = Clustering(result)

    scaled_df = clustering.scale_features(clustering.df_all_tracks)

    df_cluster = clustering.k_means_clustering(scaled_df)

    return {
        "plots" : df_cluster.to_dict("list")
    }