import pandas as pd 
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans


class TransformDataFrame:

    def __init__(self, df_tracks, df_audio_ft):
        self.df_tracks = df_tracks
        self.df_audio_ft = df_audio_ft
        self.concat_df = self.concat_data()
        self.audio_ft = ['danceability', 'energy', 'loudness', 'speechiness','acousticness','instrumentalness','liveness','valence','tempo']
        self.fit_features = ['danceability','energy','tempo']
        self.concat_df[self.audio_ft] = self.scale_features()
        self.n_clusters = self.determine_optimal_k(max_k=35)
        self.final_df = self.clustering()
        self.final_df['key'], self.final_df['mode'] = self.normalization()
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

    def determine_optimal_k(self, max_k):
        # Initialize a list to store the inertias for each value of k
        inertias = []

        # Loop through different values of k
        for k in range(1, max_k+1):
            # Fit a K-means model with the current value of k
            model = KMeans(n_clusters=k)
            model.fit(self.concat_df[self.fit_features])

            # Append the inertia for the current model to the list
            inertias.append(model.inertia_)

        # Return the value of k that has the smallest inertia
        return inertias.index(min(inertias)) + 1 

    def get_cluster_number(self):

        ### WIP WIP WIP

        return 4

    
    def clustering(self):

        kmeans = KMeans(n_clusters=self.n_clusters).fit(self.concat_df[self.fit_features])

        y_kmeans = kmeans.predict(self.concat_df[self.fit_features])

        self.concat_df['cluster'] = y_kmeans

        self.concat_df['cluster'] = self.concat_df['cluster'].astype('str')
        
        cluster_names = {}

        for cluster in range(0,self.n_clusters):
            cluster_names.update({str(cluster): f'Cluster {cluster}'})

        self.concat_df['cluster_name'] = self.concat_df['cluster'].map(cluster_names)

        return self.concat_df

    
    def normalization(self):

        self.final_df['key'] = self.final_df['key'].map({0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F', 6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'})

        self.final_df['mode'] = self.final_df['mode'].map({1: 'Major', 0: 'Minor'})


        return self.final_df['key'], self.final_df['mode']

    def get_cluster_stats(self):

        cluster_stats = pd.DataFrame(columns=self.audio_ft)


        for n in self.final_df['cluster'].value_counts().index.to_list():
            cluster_stats = cluster_stats.append(self.final_df[self.final_df['cluster'] == n][self.audio_ft].mean(), ignore_index=True)

        return cluster_stats












