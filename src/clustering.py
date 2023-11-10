import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler


def determine_optimal_k(self, scaled_df, max_k):
    """
    Determine the optimal number of clusters (k) using the K-means algorithm.

    This function calculates the optimal number of clusters for K-means clustering by evaluating different values
    of k and choosing the value that minimizes the inertia.

    :param scaled_df: The scaled DataFrame containing the data for clustering.
    :type scaled_df: pandas.DataFrame

    :param max_k: The maximum number of clusters to consider.
    :type max_k: int

    :return: The optimal number of clusters (k) based on inertia.
    :rtype: int

    :raises ValueError: If no suitable number of clusters is found.
    """
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
    """
    Prepare a DataFrame for clustering from user data.

    This function extracts and formats data from user playlists and tracks to create a DataFrame suitable for clustering.

    :param user_data: The user's data containing playlists and tracks.
    :type user_data: UserData

    :return: A DataFrame with features for clustering.
    :rtype: pandas.DataFrame
    """

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


def k_means_clustering(_df, fit_features, n_clusters=5):
    """
    Perform K-means clustering on a DataFrame.

    This function applies K-means clustering to the provided DataFrame and returns the results, including cluster labels and names.

    :param scaled_df: The scaled DataFrame for clustering.
    :type scaled_df: pandas.DataFrame

    :param fit_features: The features used for clustering.
    :type fit_features: list

    :param n_clusters: The number of clusters to create (default is 5).
    :type n_clusters: int

    :return: The DataFrame with added cluster labels and cluster names.
    :rtype: pandas.DataFrame
    """

    scaler = MinMaxScaler()

    scaled_df = scaler.fit_transform(_df[fit_features])

    kmeans = KMeans(n_clusters=n_clusters, random_state=42).fit(scaled_df)

    y_kmeans = kmeans.predict(scaled_df)

    _df["track_cluster"] = y_kmeans

    _df["track_cluster"] = _df["track_cluster"].astype("str")

    cluster_names = {}

    for cluster in range(0, n_clusters):
        cluster_names.update({str(cluster): f"Cluster {cluster + 1 }"})

    _df["cluster_name"] = _df["track_cluster"].map(cluster_names)

    return _df
