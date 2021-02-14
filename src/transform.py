import pandas as pd 
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans


class TransformDataFrame:

    """A class to transform all the extracted data from DataExtractor
    and return a Data Frame ready to be plotted.

    ...

    Attributes
    ----------
    df_tracks : dataframe
        Pandas Data Frame with all the info of the user tracks
    df_audio_ft : dataframe
        Pandas Data frame with all the audio features of the user tracks
    
    Methods
    .......

    concat_data():
        Concat tracks data frame and audio features data frame.
    scale_features():
        Scale thhe features of the data frame in preparation for clustering.
    get_cluster_number():
        Defines the number of clusters that K-means will user.
    clustering():
        Apply K-means clustering to the tracks.
    normalization():
        Mapping of some classes of a column to proper viz.
    get_cluster_stats():
        Create a new Data Frame with stats of each cluster for viz.

    """

    def __init__(self, df_tracks, df_audio_ft):
        self.df_tracks = df_tracks
        self.df_audio_ft = df_audio_ft
        self.concat_df = self.concat_data()
        self.n_clusters = self.get_cluster_number()
        self.audio_ft = ['danceability', 'energy', 'loudness', 'speechiness','acousticness','instrumentalness','liveness','valence','tempo']
        self.fit_features = ['danceability','energy','tempo','valence']
        self.concat_df[self.audio_ft] = self.scale_features()
        self.final_df = self.clustering()
        self.final_df['key'], self.final_df['mode'] = self.normalization()
        self.cluster_stats = self.get_cluster_stats()
        self.n_tracks = self.final_df.shape[0]

        

    def concat_data(self):
        """

        Concat tracks data frame and audio features data frame.

        """

        self.df_tracks.reset_index(drop=True, inplace=True)
        self.df_audio_ft.reset_index(drop=True, inplace=True)

        df_join = pd.concat([self.df_tracks, self.df_audio_ft], axis=1)

        df_join['song_name'] = df_join['name'] + ' - ' + df_join['artist']


        df_join.to_csv('output.csv')

        return df_join

    def scale_features(self):
        """

        Scale thhe features of the data frame in preparation for clustering.

        """

        scaler = MinMaxScaler()

        return scaler.fit_transform(self.concat_df[self.audio_ft])

    

    def get_cluster_number(self):

        """

        Defines the number of clusters that K-means will user.

        """

        ### WIP WIP WIP

        return 4

    
    def clustering(self):

        """

        Apply K-means clustering to the tracks.

        """

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

        """

        Mapping of some classes of a column to proper viz.

        """

        self.final_df['key'] = self.final_df['key'].map({0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F', 6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'})

        self.final_df['mode'] = self.final_df['mode'].map({1: 'Major', 0: 'Minor'})


        return self.final_df['key'], self.final_df['mode']

    def get_cluster_stats(self):

        """

        Create a new Data Frame with stats of each cluster for viz.
        
        """

        cluster_stats = pd.DataFrame(columns=self.audio_ft)


        for n in self.final_df['cluster'].value_counts().index.to_list():
            cluster_stats = cluster_stats.append(self.final_df[self.final_df['cluster'] == n][self.audio_ft].mean(), ignore_index=True)

        return cluster_stats












