import pandas as pd
import numpy as np
from sklearn.cluster import KMeans


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


def prepare_df_tracks_(user_data):
    data = []

    for playlist in user_data.playlists:
        if playlist.tracks:
            for track in playlist.tracks:
                if track.features:
                    data.append([track.features.model_dump()])

    df_ = pd.DataFrame(data, columns=["data"])

    df = pd.json_normalize(df_["data"])

    df.drop_duplicates(subset=["track_id"], keep="first", inplace=True)

    return df


def k_means_clustering(scaled_df, fit_features, n_clusters=5):
    fit_features_df = scaled_df[fit_features]

    kmeans = KMeans(n_clusters=n_clusters).fit(fit_features_df)

    y_kmeans = kmeans.predict(fit_features_df)

    scaled_df["track_cluster"] = y_kmeans

    scaled_df["track_cluster"] = scaled_df["track_cluster"].astype("str")

    cluster_names = {}

    for cluster in range(0, n_clusters):
        cluster_names.update({str(cluster): f"Cluster {cluster + 1 }"})

    scaled_df["cluster_name"] = scaled_df["track_cluster"].map(cluster_names)

    return scaled_df
