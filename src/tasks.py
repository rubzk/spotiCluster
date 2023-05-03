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


@shared_task(bind=True, name="Append all the results")
def append_results(self, results):

    result = pd.DataFrame()

    for tracks in results:
        result = result.append(pd.read_json(tracks))

    result = result.dropna(axis=0, how="any", subset=["id"])

    result = result.drop(axis=1, columns="0")

    
    return json.dumps(result.to_dict("list"))

@shared_task(bind=True, name="Cluster all the results")
def cluster_results(self,result):

    result = pd.read_json(result)

    clustering = Clustering(result)

    scaled_df = clustering.scale_features(clustering.df_all_tracks)

    df_cluster = clustering.k_means_clustering(scaled_df)


    df_cluster_stats = clustering.get_cluster_stats(df_cluster)


    return {"clusters" : df_cluster.to_dict("list"),
            "cluster_stats" : df_cluster_stats.to_dict("list") }



@shared_task(bind=True, name="Create the plots")
def create_plots(self,clusters_info):
 
    clusters_stats = pd.read_json(json.dumps(clusters_info['cluster_stats']))


    plot = Plot(audio_df=["danceability", "energy", "tempo","instrumentalness","valence"])

    radar_chart = plot.radar_chart(clusters_stats)


    return {
        "plots" : {"radar_chart" : radar_chart}
    }



