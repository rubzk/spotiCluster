import json
from src.extract import DataExtractor
import configparser
from src.transform import TransformDataFrame
from src.plot import Plot3D
import pandas as pd
from src.auth import Authenticator
from plotly.utils import PlotlyJSONEncoder
from celery import shared_task, group, chain, chord


@shared_task(bind=True, name="Get tracks", propagate=False)
def get_tracks(self, auth_token, playlist):

    data_extractor = DataExtractor(auth_token)

    tracks = data_extractor.get_all_tracks_v2(playlist)

    tracks_audio_ft = data_extractor.get_all_audio_features_v2(tracks)

    transform = TransformDataFrame(tracks, tracks_audio_ft)

    result = transform.concat_data()

    result = result.dropna(axis=0,how='any')

    return json.dumps(result.to_dict('list'))


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

    self.update_state(
        state="PROGRESS",
        meta={
            "current": 50,
            "total": 100,
            "status": "Finish Processing  all the tracks",
            "result_id": res.id,
        },
    )

    return {
        "current": 50,
        "total": 100,
        "status": "Finish Processing  all the tracks",
        "result_id": res.id,
    }


@shared_task(bind=True, name="Append all the results")
def append_results(self, results):

    self.update_state(
        state="PROGRESS",
        meta={
            "current": 75,
            "total": 100,
            "status": "Concatenating Tasks",
        },
    )

    result = pd.DataFrame()

    for tracks in results:
        result = result.append(pd.read_json(tracks))


    result = result.dropna(axis=0,how='any',subset=['id'])

    result = result.drop(axis=1,columns="0")

    return {
        "current": 100,
        "total": 100,
        "status": "DONE!",
        "plots": result.to_dict('list'),
    }
