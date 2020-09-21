import pandas as pd 
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans


class TransformDataFrame:

    def __init__(self, df_tracks, df_audio_ft):
        self.df_tracks = df_tracks
        self.df_audio_ft = df_audio_ft
        self.concat_df = self.concat_data()
        self.concat_df['key'] = self.key_normalization()
        self.n_clusters = self.get_cluster_number()
        self.audio_ft = ['danceability', 'energy', 'loudness', 'speechiness','acousticness','instrumentalness','liveness','valence','tempo']
        self.fit_features = ['danceability','energy','tempo','valence']
        self.concat_df[self.audio_ft] = self.scale_features()
        self.final_df = self.clustering()
        self.cluster_stats = self.get_cluster_stats()
        self.n_tracks = self.final_df.shape[0]

        

    def concat_data(self):

        self.df_tracks.reset_index(drop=True, inplace=True)
        self.df_audio_ft.reset_index(drop=True, inplace=True)

        df_join = pd.concat([self.df_tracks, self.df_audio_ft], axis=1)

        df_join['song_name'] = df_join['name'] + ' - ' + df_join['artist']


        df_join.to_csv('output.csv')

        return df_join

    def scale_features(self):

        scaler = MinMaxScaler()

        return scaler.fit_transform(self.concat_df[self.audio_ft])

    

    def get_cluster_number(self):

        ### WIP WIP WIP

        return 4

    def key_normalization(self):

        self.concat_df['key'] = self.concat_df['key'].map({0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F', 6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'})

        return self.concat_df['key']

    def mode_normalization(self):

        self.concat_df['mode'] = self.concat_df['mode'].map({1: 'Major', 0: 'Minor'})

        return self.concat_df['mode']


    
    def clustering(self):

        kmeans = KMeans(n_clusters=self.n_clusters).fit(self.concat_df[self.fit_features])

        y_kmeans = kmeans.predict(self.concat_df[self.fit_features])

        self.concat_df['cluster'] = y_kmeans

        self.concat_df['cluster'] = self.concat_df['cluster'].astype('str')

        return self.concat_df

    def get_cluster_stats(self):

        cluster_stats = pd.DataFrame(columns=self.audio_ft)

        for n in self.final_df['cluster'].value_counts().index.to_list():
            cluster_stats = cluster_stats.append(self.final_df[self.final_df['cluster'] == n][self.audio_ft].mean(), ignore_index=True)

        return cluster_stats












