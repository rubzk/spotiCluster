import json
import configparser

from src.auth import Authenticator
from src.extract import DataExtractor
from src.transform import TransformDataFrame
from src.clustering import Clustering
from src.plot import Plot

from utils.postgres import df_to_db, PostgresDB


import pandas as pd
from celery import shared_task, chord


@shared_task(
    bind=True, name="Get tracks", propagate=False, max_retries=3, default_retry_delay=10
)
def get_tracks(self, auth_token, playlist):
    data_extractor = DataExtractor(auth_token)

    user_id = data_extractor.get_user_id()

    tracks = data_extractor.get_all_tracks_v2(playlist)

    tracks_audio_ft = data_extractor.get_all_audio_features_v2(tracks)

    transform = TransformDataFrame(tracks, tracks_audio_ft)

    result = transform.concat_data()

    result = result.dropna(axis=0, how="any")

    result["spotify_user_id"] = user_id

    result["created"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    result = transform.rename_and_reindex_columns(result)

    return json.dumps(result.to_dict("list"))


@shared_task(bind=True, name="Append all the results")
def append_results(self, results):
    result = pd.DataFrame()

    for tracks in results:
        result = result.append(pd.read_json(tracks))

    result = result.dropna(axis=0, how="any", subset=["song_id"])

    result = result.drop_duplicates(subset=["song_id"])

    return json.dumps(result.to_dict("list"))


@shared_task(bind=True, name="Cluster all the results")
def cluster_results(self, result):
    result = pd.read_json(result)

    clustering = Clustering(result)

    scaled_df = clustering.scale_features(clustering.df_all_tracks)

    df_cluster = clustering.k_means_clustering(scaled_df)

    df_cluster_stats = clustering.get_cluster_stats(df_cluster)

    return {
        "clusters": df_cluster.to_dict("list"),
        "cluster_stats": df_cluster_stats.to_dict("list"),
    }


@shared_task(bind=True, name="Create the plots")
def create_plots(self, clusters_info):
    clusters_stats = pd.read_json(json.dumps(clusters_info["cluster_stats"]))
    clusters = pd.read_json(json.dumps(clusters_info["clusters"]))

    plot = Plot(
        audio_df=[
            "danceability",
            "energy",
            "tempo",
            "instrumentalness",
            "valence",
            "loudness",
        ]
    )

    radar_chart = plot.radar_chart(clusters_stats)

    radar_chart_test = plot.radar_chart_test(clusters_stats)

    pie_chart = plot.pie_chart(clusters)

    top_3_artist = plot.top_3_artist(clusters)

    return {
        "plots": {
            "radar_chart": radar_chart,
            "radar_chart_test" : radar_chart_test,
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
        }
    }


@shared_task(bind=True, name="SAVE CLUSTER DATA IN POSTGRES")
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
    }
