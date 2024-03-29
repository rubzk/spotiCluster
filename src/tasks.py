import json
import uuid 

from src.extract import DataExtractor
from src.clustering import k_means_clustering, prepare_df_tracks_
from src.plot import (
    Plots,
    generate_radar_chart,
    generate_pie_chart,
    generate_scatter_chart,
    generate_saved_tracks_timeline,
    generate_top_3_artist,
    generate_data_for_table,
)

#from utils.postgres import df_to_db, PostgresDB

import logging

import pandas as pd
from celery import shared_task
from .models import Playlist, UserData, TracksClustered
from .db import generate_and_commit_task_results_db, generate_and_commit_task_metadata_db


from fastapi.encoders import jsonable_encoder

log = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="GET TRACKS FROM API",
    propagate=False,
    max_retries=10,
    default_retry_delay=4,
)
def get_tracks(self, auth_token, playlist_dict):
    """
    Retrieve tracks and audio features for a playlist.

    This task fetches track data and audio features for a given playlist using the Spotify API.

    :param auth_token: The user's authentication token for Spotify.
    :type auth_token: str

    :param playlist_dict: A dictionary representing the playlist to fetch tracks for.
    :type playlist_dict: dict

    :return: A dictionary containing the playlist's model data.
    :rtype: dict

    :raises KeyError, AttributeError: If there are issues with data extraction.
    """
    try:
        data_extractor = DataExtractor(auth_token)

        playlist = Playlist(**playlist_dict)

        playlist = data_extractor.get_all_tracks(playlist)

        playlist = data_extractor.get_all_audio_features(playlist)

        return {"playlist_model": playlist.dict()}
    except (KeyError, AttributeError) as e:
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    name="GET LIKED TRACKS",
    max_retries=3,
    default_retry_delay=10,
)
def get_saved_tracks(self, auth_token):
    """
    Retrieve liked (saved) tracks and their audio features.

    This task fetches liked tracks and their audio features for a user using the Spotify API.

    :param auth_token: The user's authentication token for Spotify.
    :type auth_token: str

    :return: A dictionary containing liked tracks and their audio features.
    :rtype: dict
    """

    data_extractor = DataExtractor(auth_token)

    saved_tracks = data_extractor.get_all_saved_tracks()

    saved_tracks = data_extractor.get_all_audio_features(saved_tracks)

    return jsonable_encoder(saved_tracks)


@shared_task(
    bind=True, name="TRANSFORM ALL THE RESULTS", max_retries=3, default_retry_delay=10
)
def append_results(self, results, user):
    """
    Combine and transform results into a user data model.

    This task combines and transforms the results of fetching playlists and liked tracks into a user data model.

    :param results: A list of results, including playlist models and liked tracks.
    :type results: list

    :param user: A dictionary representing the user's data.
    :type user: dict

    :return: A JSON-serializable user data model.
    :rtype: dict
    """

    user_data = UserData(**user)


    playlists = []

    for r in results:
        if "playlist_model" in r:
            playlists.append(Playlist.parse_obj(r["playlist_model"]))
        else:
            user_data.saved_tracks = r
    
    user_data.playlists = playlists

    return jsonable_encoder(user_data)


@shared_task(
    bind=True, name="CLUSTER THE RESULTS", max_retries=3, default_retry_delay=10
)
def cluster_results(self, user_data):
    """
    Perform K-means clustering on user data.

    This task applies K-means clustering to the provided user data, generating cluster labels and cluster names.

    :param user_data: The user's data including playlists and liked tracks.
    :type user_data: dict

    :return: A JSON-serializable user data model with clustering results.
    :rtype: dict
    """

    user_data = UserData(**user_data)

    df_tracks_features = prepare_df_tracks_(user_data)

    clustered_df = k_means_clustering(
        df_tracks_features,
        fit_features=[
            "danceability",
            "energy",
            # "key",
            # "loudness",
            # "mode",
            "acousticness",
            "valence",
            "tempo",
            "instrumentalness",
        ],
    )

    clustered_dict_ = clustered_df.to_dict(orient="records")

    user_data.clustered_tracks = [
        TracksClustered(**record) for record in clustered_dict_
    ]

    return jsonable_encoder(user_data)


@shared_task(
    bind=True, name="CREATE JSON FOR PLOTS", max_retries=3, default_retry_delay=10
)
def create_plots(self, user_data):
    """
    Generate JSON data for various plots and charts.

    This task generates JSON data for radar charts, pie charts, scatter charts, and more, based on user data.

    :param user_data: The user's data model.
    :type user_data: dict

    :return: JSON data for various plots and charts.
    :rtype: dict
    """

    user_data = UserData(**user_data)

    radar_chart = generate_radar_chart(user_data)

    pie_chart = generate_pie_chart(user_data)

    scatter_chart = generate_scatter_chart(user_data)

    top_3_artist = generate_top_3_artist(user_data)

    saved_tracks_timeline = generate_saved_tracks_timeline(user_data)

    table_tracks = generate_data_for_table(user_data)

    number_of_tracks = len(user_data.clustered_tracks)

    number_of_clusters = len(
        set([track.cluster_name for track in user_data.clustered_tracks])
    )

    generate_and_commit_task_results_db(plots=[radar_chart,pie_chart,scatter_chart,top_3_artist,saved_tracks_timeline,table_tracks], task_id=user_data.task.id)

    generate_and_commit_task_metadata_db(user_data=user_data,number_of_tracks=number_of_tracks)
    

    plots = Plots(
        number_of_tracks=number_of_tracks,
        number_of_clusters=number_of_clusters,
        radar_chart=radar_chart,
        pie_chart=pie_chart,
        scatter_chart=scatter_chart,
        top_3_artist=top_3_artist,
        saved_tracks_timeline=saved_tracks_timeline,
        table_tracks=table_tracks,
        user_model=user_data,
    )

    return jsonable_encoder(plots)

