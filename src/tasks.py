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
def get_tracks_celery(self, auth_token, playlist):

    data_extractor = DataExtractor(auth_token)

    tracks = data_extractor.get_all_tracks_v2(playlist)

    tracks_audio_ft = data_extractor.get_all_audio_features_v2(tracks)

    transform = TransformDataFrame(tracks, tracks_audio_ft)

    return transform.concat_data()


@shared_task(bind=True, name="Process all the tracks")
def concatenate_all_tracks(self, auth_token):

    # chain(process_all_tracks.s(auth_token) | append_results.s()).apply_async()

    extractor = DataExtractor(auth_token)

    playlists = extractor.get_all_playlists()

    total_tracks = [get_tracks_celery.s(auth_token, playlist) for playlist in playlists]

    chord(total_tracks)(append_results.s())


@shared_task(bind=True, name="Append all the results")
def append_results(self, results):
    result = pd.DataFrame()

    for tracks in results:
        result = result.append(tracks[1])

    return result


@shared_task(bind=True, name="ETL Data")
def celery_etl(self, auth_code, client_id, client_secret, redirect_uri):
    self.update_state(
        state="PROGRESS", meta={"current": 0, "total": 100, "status": "Getting Auth"}
    )

    print("Antes de autenticar")
    auth = Authenticator(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        auth_code=auth_code,
    )

    self.update_state(
        state="PROGRESS",
        meta={"current": 25, "total": 100, "status": "Start Extraction"},
    )

    extractor = DataExtractor(auth.auth_token)

    concatenate_all_tracks.apply_async(args=(auth.auth_token,))

    """total_tracks = [
        get_tracks_celery.delay(auth_token=auth.auth_token, playlist=playlist)
        for playlist in playlists
    ]"""

    # results = [async_item.wait() for async_item in asyncs]

    """transform = TransformDataFrame(extractor.df_tracks_info, extractor.df_audio_ft)
    self.update_state(
        state="PROGRESS",
        meta={"current": 66, "total": 100, "status": "Generating the plots"},
    )
    plotter = Plot3D(transform.final_df, transform.n_clusters, transform.cluster_stats)

    form_data = {
        "polar": plotter.radar_chart(),
        "scatter3d": {
            1: plotter.scatter_3d("danceability", "valence", "energy"),
            2: plotter.scatter_3d("loudness", "tempo", "acousticness"),
            3: plotter.scatter_3d("speechiness", "acousticness", "instrumentalness"),
            4: plotter.scatter_3d("tempo", "energy", "loudness"),
        },
        "keys_bar": plotter.bar_chart(
            {
                "x": plotter.df["key"].value_counts().values,
                "y": plotter.df["key"].value_counts().index.to_list(),
                "color": plotter.df["key"].value_counts().index.to_list(),
                "orientation": "h",
                "width": 450,
                "height": 450,
                "layout": {
                    "title": "Key Appearence",
                    "xaxis": "Number of keys",
                    "yaxis": "Keys",
                },
            }
        ),
        "mode_bar": plotter.bar_chart(
            {
                "x": plotter.df["mode"].value_counts().index.to_list(),
                "y": plotter.df["mode"].value_counts().values,
                "color": plotter.df["mode"].value_counts().index.to_list(),
                "orientation": "v",
                "width": 450,
                "height": 450,
                "layout": {
                    "title": "Mode of songs",
                    "xaxis": "Mode type ",
                    "yaxis": "Count",
                },
            }
        ),
        "cluster_bar": plotter.bar_chart(
            {
                "x": plotter.df["cluster_name"].value_counts().values,
                "y": plotter.df["cluster_name"].value_counts().index.to_list(),
                "color": plotter.df["cluster_name"].value_counts().index.to_list(),
                "orientation": "h",
                "width": 450,
                "height": 450,
                "layout": {
                    "title": "Cluster Classes",
                    "xaxis": "Count",
                    "yaxis": "Cluster number",
                },
            }
        ),
        "user_data": [plotter.n_clusters, transform.n_tracks],
        "scatter_matrix": plotter.scatter_matrix(
            {
                "dimensions": ["danceability", "valence", "tempo", "energy"],
                "color": "cluster",
            }
        ),
    }

    form_data = json.dumps(form_data, cls=PlotlyJSONEncoder)

    return {"current": 100, "total": 100, "status": "DONE!", "plots": form_data}
"""
    return {"current": 100, "total": 100, "status": "DONE!"}
