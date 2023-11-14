import pandas as pd
import numpy as np
import json

from pydantic import BaseModel, Field, root_validator
from typing import List, Optional, Any, Dict
from .models import UserData


class Plot(BaseModel):
    """
    Data model for a plot.

    This class represents a plot data model that contains a dictionary of data.

    :param data: A dictionary of data for the plot.
    :type data: Dict
    """

    data: Dict


class Plots(BaseModel):
    """
    Data model for multiple plots.

    This class represents a data model for multiple plots, including radar charts, pie charts, scatter charts, and more.

    :param number_of_tracks: The number of tracks in the user's data.
    :type number_of_tracks: int

    :param number_of_clusters: The number of clusters in the user's data.
    :type number_of_clusters: int

    :param radar_chart: Radar chart data.
    :type radar_chart: Optional[Plot]

    :param pie_chart: Pie chart data.
    :type pie_chart: Optional[Plot]

    :param scatter_chart: Scatter chart data.
    :type scatter_chart: Optional[Plot]

    :param top_3_artist: Data for the top 3 artists in each cluster.
    :type top_3_artist: Optional[Plot]

    :param saved_tracks_timeline: Timeline data for saved tracks.
    :type saved_tracks_timeline: Optional[Plot]

    :param user_model: The user data model.
    :type user_model: UserData
    """

    number_of_tracks: int
    number_of_clusters: int
    radar_chart: Optional[Plot]
    pie_chart: Optional[Plot]
    scatter_chart: Optional[Plot]
    top_3_artist: Optional[Plot]
    saved_tracks_timeline: Optional[Plot]
    table_tracks: Optional[Plot]
    user_model: UserData


def generate_radar_chart(user_data):
    """
    Generate radar chart data based on user data.

    This function calculates cluster statistics and generates radar chart data.

    :param user_data: The user's data model.
    :type user_data: UserData

    :return: Radar chart data.
    :rtype: Plot
    """

    _df = pd.DataFrame([track.model_dump() for track in user_data.clustered_tracks])

    cluster_stats = _df.groupby("cluster_name").mean().reset_index()

    _plot = {}

    for c in cluster_stats.columns:
        _plot[c] = cluster_stats[c].to_list()

    return Plot(data=_plot)


def generate_pie_chart(user_data):
    """
    Generate pie chart data based on user data.

    This function calculates the number of tracks in each cluster and generates pie chart data.

    :param user_data: The user's data model.
    :type user_data: UserData

    :return: Pie chart data.
    :rtype: Plot
    """

    _df = pd.DataFrame([track.model_dump() for track in user_data.clustered_tracks])

    _df_gb = (
        _df.groupby("cluster_name")[["track_id"]]
        .count()
        .reset_index()
        .rename(columns={"track_id": "number_of_tracks"})
    )

    return Plot(data=_df_gb.to_dict("list"))


def generate_top_3_artist(user_data):
    """
    Generate data for the top 3 artists in each cluster.

    This function identifies the top 3 artists in each cluster based on user data.

    :param user_data: The user's data model.
    :type user_data: UserData

    :return: Data for the top 3 artists in each cluster.
    :rtype: Plot
    """

    def get_top_artists(group):
        return group["artist_name"].value_counts().nlargest(3)

    _tracks_clustered = pd.DataFrame(
        [track.model_dump() for track in user_data.clustered_tracks]
    )

    _data = []

    for playlist in user_data.playlists:
        if playlist.tracks:
            for track in playlist.tracks:
                for artist in track.artists:
                    _data.append([track.id, artist.name])

    _artist_tracks = pd.DataFrame(_data, columns=["track_id", "artist_name"])

    _artist_tracks = _artist_tracks.merge(_tracks_clustered, how="left", on="track_id")

    top_artists_per_cluster = (
        _artist_tracks.groupby("cluster_name").apply(get_top_artists).reset_index()
    )

    top_artists_per_cluster.columns = ["cluster_name", "artist_name", "count"]

    top_artists_per_cluster = top_artists_per_cluster.to_dict("list")

    return Plot(data=top_artists_per_cluster)


def generate_saved_tracks_timeline(user_data):
    """
    Generate a timeline of audio features for saved tracks.

    This function creates a timeline of audio features for saved tracks in user data.

    :param user_data: The user's data model.
    :type user_data: UserData

    :return: Timeline data for saved tracks.
    :rtype: Plot
    """

    features = [
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

    _df = pd.DataFrame([track.model_dump() for track in user_data.saved_tracks.tracks])

    _df = pd.concat([_df, pd.json_normalize(_df["features"])], axis=1)

    _df["added_at"] = _df["added_at"].apply(lambda x: pd.Timestamp(x))

    _df["yyyy-mm"] = _df["added_at"].dt.strftime("%Y-%m")

    _timeline = _df.groupby(["yyyy-mm"])[features].mean().reset_index()

    _timeline = _timeline.to_dict("list")

    return Plot(data=_timeline)


def generate_scatter_chart(user_data):
    """
    Generate scatter chart data based on user data.

    This function generates scatter chart data for selected audio features in each cluster.

    :param user_data: The user's data model.
    :type user_data: UserData

    :return: Scatter chart data.
    :rtype: Plot
    """

    _df = pd.DataFrame([track.model_dump() for track in user_data.clustered_tracks])

    _data = []

    for playlist in user_data.playlists:
        if playlist.tracks:
            for track in playlist.tracks:
                _data.append([track.id, track.name, track.artists[0].name])

    _artist_tracks = pd.DataFrame(
        _data, columns=["track_id", "track_name", "first_artist"]
    )

    _artist_tracks["track_title"] = (
        _artist_tracks["track_name"] + " - " + _artist_tracks["first_artist"]
    )

    _df = _df.merge(_artist_tracks, on="track_id", how="left").drop_duplicates(
        subset=["track_id"]
    )

    features = ["danceability", "energy", "instrumentalness", "valence", "track_title"]

    _scatter_dict = {}

    for cluster in _df["cluster_name"].unique():
        _scatter_dict.update(
            {cluster: _df[_df.cluster_name == cluster][features].to_dict("list")}
        )

    return Plot(data=_scatter_dict)


def generate_data_for_table(user_data):
    """
    Generate dataframe with data for plotting a table

    """

    _df_clustered = pd.DataFrame(
        [track.model_dump() for track in user_data.clustered_tracks]
    )

    _data = []

    for playlist in user_data.playlists:
        if playlist.tracks:
            for track in playlist.tracks:
                _data.append([track.id, track.name, track.artists[0].name])

    _artist_tracks = pd.DataFrame(
        _data, columns=["track_id", "track_name", "first_artist"]
    )

    _artist_tracks["track_title"] = (
        _artist_tracks["track_name"] + " - " + _artist_tracks["first_artist"]
    )

    _df_clustered = _df_clustered.merge(
        _artist_tracks, on="track_id", how="left"
    ).drop_duplicates(subset=["track_id"])

    _df_clustered = _df_clustered.to_dict("list")

    return Plot(data=_df_clustered)
