import pandas as pd 
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.graph_objects as go 
import json
from plotly.utils import PlotlyJSONEncoder
from plotly.subplots import make_subplots

def concat_data(df_info_tracks, df_audio_ft):

    df_info_tracks.reset_index(drop=True, inplace=True)
    df_audio_ft.reset_index(drop=True, inplace=True)

    df_join = pd.concat([df_info_tracks, df_audio_ft], axis =1)

    df_join['song_name'] = df_join['name'] + ' - ' + df_join['artist']

    #df_join.to_csv('output.csv')

    return df_join



def get_cluster_number(df_scaled):
    
    df = pd.DataFrame([], columns=['SSD', 'n_clusters'])

    for n  in range(1,15):
        kmeans = KMeans(n_clusters=n)
        kmeans.fit(X=df_scaled)
        df = df.append({'SSD': kmeans.inertia_, 'n_clusters': n}, ignore_index=True)

    return 4


def clustering(df_scaled, clusters, features):

    kmeans = KMeans(n_clusters=clusters).fit(df_scaled[features])

    y_kmeans = kmeans.predict(df_scaled[features])

    df_scaled['cluster'] = y_kmeans

    return df_scaled









