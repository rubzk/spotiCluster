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
    try:
        data_extractor = DataExtractor(auth_token)

        user_id = data_extractor.get_user_id()

        tracks = data_extractor.get_all_tracks(playlist)

        tracks_audio_ft = data_extractor.get_all_audio_features(tracks)

        transform = TransformDataFrame(tracks, tracks_audio_ft)

        tracks = transform.concat_data()

        tracks = tracks.dropna(axis=0, how="any")

        tracks["spotify_user_id"] = user_id

        tracks["created"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        tracks = transform.rename_and_reindex_columns(tracks)

        return {"tracks": tracks.to_dict("list")}
    except KeyError as e:
        raise self.retry(exc=e)


@shared_task(
    bind=True, name="Append all the results", max_retries=3, default_retry_delay=10
)
def append_results(self, results):
    result = pd.DataFrame()

    saved_tracks_result = pd.DataFrame()

    for r in results:
        if list(r.keys()) == ["tracks"]:
            result = pd.concat(
                [result, pd.read_json(json.dumps(r["tracks"]))], ignore_index=True
            )

        else:
            saved_tracks_result = pd.read_json(json.dumps(r["saved_tracks"]))

    result = result.dropna(axis=0, how="any", subset=["song_id"])

    result = result.drop_duplicates(subset=["song_id"])

    saved_tracks_result.to_csv("appended_saved_tracks.csv")

    return {
        "saved_tracks": saved_tracks_result.to_dict("list"),
        "tracks": json.dumps(result.to_dict("list")),
    }


@shared_task(
    bind=True, name="Cluster all the results", max_retries=3, default_retry_delay=10
)
def cluster_results(self, result):
    tracks = pd.read_json(result["tracks"])

    clustering = Clustering(tracks)

    scaled_df = clustering.scale_features(clustering.df_all_tracks)

    df_cluster = clustering.k_means_clustering(scaled_df)

    df_cluster_stats = clustering.get_cluster_stats(df_cluster)

    return {
        "clusters": df_cluster.to_dict("list"),
        "cluster_stats": df_cluster_stats.to_dict("list"),
        "saved_tracks": result["saved_tracks"],
    }


@shared_task(bind=True, name="Create the plots", max_retries=3, default_retry_delay=10)
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

    # radar_chart_test = plot.radar_chart_test(clusters_stats)

    pie_chart = plot.pie_chart(clusters)

    # with open("saved_tracks.json", "w") as f:
    #     f.write(clusters_info["saved_tracks"])

    # saved_test =

    timeline = plot.saved_tracks_timeline(
        pd.read_json(json.dumps(clusters_info["saved_tracks"], default=str))
    )

    top_3_artist = plot.top_3_artist(clusters)

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


@shared_task(
    bind=True,
    name="GET LIKED TRACKS AND AUDIO FEATURES",
    max_retries=3,
    default_retry_delay=10,
)
def get_saved_tracks(self, auth_token):
    data_extractor = DataExtractor(auth_token)

    saved_tracks = data_extractor.get_all_saved_tracks()

    saved_tracks_audio_ft = data_extractor.get_all_audio_features(tracks=saved_tracks)

    saved_tracks = pd.concat([saved_tracks, saved_tracks_audio_ft], axis=1)

    saved_tracks["added_at"] = saved_tracks["added_at"].astype("str")

    return {"saved_tracks": saved_tracks.to_dict("list")}
