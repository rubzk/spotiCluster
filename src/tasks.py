import json
import configparser

from src.auth import Authenticator
from src.extract import DataExtractor
from src.transform import TransformDataFrame
from src.clustering import Clustering
from src.plot import Plot


import pandas as pd
from celery import shared_task, chord


@shared_task(bind=True, name="Get tracks", propagate=False)
def get_tracks(self, auth_token, playlist):

    data_extractor = DataExtractor(auth_token)

    user_id = data_extractor.get_user_id()

    tracks = data_extractor.get_all_tracks_v2(playlist)

    tracks_audio_ft = data_extractor.get_all_audio_features_v2(tracks)

    transform = TransformDataFrame(tracks, tracks_audio_ft)

    result = transform.concat_data()

    result = result.dropna(axis=0, how="any")

    result['spotify_user_id'] = user_id

    result['created'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S.%f')

    result = transform.rename_and_reindex_columns(result)

    result.to_csv('output2.csv')

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

    df_cluster.to_csv('clusters.csv')


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

@shared_task(bind=True, name="SAVE CLUSTER DATA IN POSTGRES")
def save_data_in_postgres(self,cluster_data):
    pass


