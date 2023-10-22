import json
import configparser

from src.auth import Authenticator
from src.extract import DataExtractor
from src.transform import TransformDataFrame
from src.clustering import Clustering
from src.plot import Plot

from utils.postgres import df_to_db, PostgresDB

import logging

import pandas as pd
from celery import shared_task, chord
from .models import Playlist, UserData, SavedTracks

log = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="GET TRACKS FROM API",
    propagate=False,
    max_retries=10,
    default_retry_delay=4,
)
def get_tracks(self, auth_token, playlist_dict):
    try:
        data_extractor = DataExtractor(auth_token)

        playlist = Playlist(**playlist_dict)

        playlist = data_extractor.get_all_tracks(playlist)

        playlist = data_extractor.get_all_audio_features(playlist)

        # transform = TransformDataFrame(tracks, tracks_audio_ft)

        # tracks = transform.concat_data()

        # tracks = tracks.dropna(axis=0, how="any")

        # tracks["spotify_user_id"] = user_id

        # tracks["created"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        # tracks = transform.rename_and_reindex_columns(tracks)

        with open("playlist_model.json", "w") as json_file:
            json.dump({"playlist_model": playlist.dict()}, json_file)

        return {"playlist_model": playlist.dict()}
    except (KeyError, AttributeError) as e:
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    name="GET LIKED TRACKS AND AUDIO FEATURES",
    max_retries=3,
    default_retry_delay=10,
)
def get_saved_tracks(self, auth_token):
    data_extractor = DataExtractor(auth_token)

    saved_tracks = data_extractor.get_all_saved_tracks()

    saved_tracks = data_extractor.get_all_audio_features(saved_tracks)

    log.warning(saved_tracks)

    return saved_tracks.json()


@shared_task(
    bind=True, name="TRANSFORM ALL THE RESULTS", max_retries=3, default_retry_delay=10
)
def append_results(self, results, user):
    user_data = UserData(**user)

    for r in results:
        if "saved_tracks_model" in r:
            with open("saved_tracks_model.json", "w") as json_file:
                json.dump(r, json_file)

            saved_tracks = SavedTracks.parse_obj(r["saved_tracks_model"])
            user_data.saved_tracks = saved_tracks
        elif "playlist_model" in r:
            user_data.playlists.append(Playlist.parse_obj(r["playlist_model"]))

    with open("final_user_model.json", "w") as json_file:
        json.dump(user_data.dict(), json_file)

    log.warning(user_data)

    return {None}


@shared_task(
    bind=True, name="CLUSTER THE RESULTS", max_retries=3, default_retry_delay=10
)
def cluster_results(self, result):
    tracks = pd.read_json(result["tracks"])

    clustering = Clustering(tracks)

    scaled_df = clustering.scale_features(clustering.df_all_tracks)

    n_clusters = clustering.determine_optimal_k(scaled_df=scaled_df, max_k=5)

    df_cluster = clustering.k_means_clustering(scaled_df, n_clusters=n_clusters)

    df_cluster_stats = clustering.get_cluster_stats(df_cluster)

    return {
        "clusters": df_cluster.to_dict("list"),
        "cluster_stats": df_cluster_stats.to_dict("list"),
        "saved_tracks": result["saved_tracks"],
    }


@shared_task(
    bind=True, name="CREATE JSON FOR PLOTS", max_retries=3, default_retry_delay=10
)
def create_plots(self, clusters_info):
    clusters_stats = pd.read_json(json.dumps(clusters_info["cluster_stats"]))
    clusters = pd.read_json(json.dumps(clusters_info["clusters"]))

    plot = Plot(
        audio_df=[
            "danceability",
            "energy",
            "instrumentalness",
            "valence",
        ]
    )

    radar_chart = plot.radar_chart(clusters_stats)

    pie_chart = plot.pie_chart(clusters)

    timeline = plot.saved_tracks_timeline(
        pd.read_json(json.dumps(clusters_info["saved_tracks"], default=str))
    )

    top_3_artist = plot.top_3_artist(clusters)

    scatter_dict = plot.scatter_chart(clusters)

    return {
        "plots": {
            "radar_chart": radar_chart,
            "pie_chart": pie_chart,
            "number_of_tracks": clusters.shape[0],
            "number_of_clusters": len(clusters.cluster_name.unique()),
            "top_3_artist": top_3_artist,
            "songs": clusters[
                [
                    "cluster_name",
                    "song_name",
                    "artist",
                    "title",
                    "danceability",
                    "energy",
                    "instrumentalness",
                    "valence",
                    "tempo",
                ]
            ].to_dict("list"),
            "saved_tracks": timeline,
            "scatter": scatter_dict,
        }
    }


@shared_task(
    bind=True,
    name="SAVE CLUSTER DATA IN POSTGRES",
    max_retries=3,
    default_retry_delay=10,
)
def save_data_in_postgres(self, result):
    cluster_data = pd.read_json(json.dumps(result["clusters"]))
    cluster_stats = pd.read_json(json.dumps(result["cluster_stats"]))

    db = PostgresDB()
    df_to_db(
        df=cluster_data,
        table_name="user_clusters",
    )

    return {
        "clusters": cluster_data.to_dict("list"),
        "cluster_stats": cluster_stats.to_dict("list"),
        "saved_tracks": result["saved_tracks"],
    }
