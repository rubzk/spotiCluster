import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans


class Clustering:
    def __init__(self, all_tracks):
        self.audio_ft = [
            "danceability",
            "energy",
            "loudness",
            "speechiness",
            "acousticness",
            "instrumentalness",
            "liveness",
            "valence",
            "tempo",
        ]
        self.fit_features = ["danceability", "energy", "instrumentalness", "valence"]
        # self.n_clusters = 4
        self.df_all_tracks = all_tracks

    def _json_to_df(self):
        return pd.read_json(self.all_data)

    def scale_features(self, all_tracks):
        scaler = MinMaxScaler()

        all_tracks[self.audio_ft] = scaler.fit_transform(all_tracks[self.audio_ft])

        return all_tracks

    def k_means_clustering(self, scaled_df, n_clusters):
        fit_features_df = pd.DataFrame(scaled_df)

        fit_features_df = scaled_df[self.fit_features]

        # kmeans = KMeans(n_clusters=self.n_clusters).fit(fit_features_df)

        kmeans = KMeans(n_clusters=n_clusters).fit(fit_features_df)

        y_kmeans = kmeans.predict(fit_features_df)

        scaled_df["songs_cluster"] = y_kmeans

        scaled_df["songs_cluster"] = scaled_df["songs_cluster"].astype("str")

        cluster_names = {}

        for cluster in range(0, n_clusters):
            cluster_names.update({str(cluster): f"Cluster {cluster}"})

        scaled_df["cluster_name"] = scaled_df["songs_cluster"].map(cluster_names)

        return scaled_df

    def get_cluster_stats(self, df_cluster):
        cluster_stats = (
            df_cluster.groupby("cluster_name")[self.audio_ft].mean().reset_index()
        )

        return cluster_stats

    def determine_optimal_k(self, scaled_df, max_k):
        # Initialize a list to store the inertias for each value of k
        inertias = []

        # Loop through different values of k
        for k in range(1, max_k + 1):
            # Fit a K-means model with the current value of k
            model = KMeans(n_clusters=k)
            model.fit(scaled_df[self.fit_features])

            # Append the inertia for the current model to the list
            inertias.append(model.inertia_)

        # Return the value of k that has the smallest inertia

        if inertias.index(min(inertias)) < 4:
            return 4
        else:
            return inertias.index(min(inertias)) + 1
