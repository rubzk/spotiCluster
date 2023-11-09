import json

from src.extract import DataExtractor
from src.clustering import k_means_clustering, prepare_df_tracks_
from src.plot import (
    Plots,
    generate_radar_chart,
    generate_pie_chart,
    generate_scatter_chart,
    generate_saved_tracks_timeline,
    generate_top_3_artist,
)

from utils.postgres import df_to_db, PostgresDB

import logging

import pandas as pd
from celery import shared_task
from .models import Playlist, UserData, TracksClustered

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

    log.warning(saved_tracks.dict())

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

    for r in results:
        if "playlist_model" in r:
            user_data.playlists.append(Playlist.parse_obj(r["playlist_model"]))
        else:
            # saved_tracks = SavedTracks.parse_obj(r)
            user_data.saved_tracks = r

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
        fit_features=["danceability", "energy", "instrumentalness", "valence"],
    )

    clustered_dict_ = clustered_df.to_dict(orient="records")

    user_data.clustered_tracks = [
        TracksClustered(**record) for record in clustered_dict_
    ]

    # with open("./output/final_user_data_v1.json", "w") as file:
    #     json.dump(jsonable_encoder(user_data), file)

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

    number_of_tracks = len(user_data.clustered_tracks)

    number_of_clusters = len(
        set([track.cluster_name for track in user_data.clustered_tracks])
    )

    plots = Plots(
        number_of_tracks=number_of_tracks,
        number_of_clusters=number_of_clusters,
        radar_chart=radar_chart,
        pie_chart=pie_chart,
        scatter_chart=scatter_chart,
        top_3_artist=top_3_artist,
        saved_tracks_timeline=saved_tracks_timeline,
        user_model=user_data,
    )

    with open("./output/final_plots_data.json", "w") as json_file:
        json.dump(jsonable_encoder(plots), json_file)

    return jsonable_encoder(plots)


@shared_task(
    bind=True,
    name="SAVE CLUSTER DATA IN POSTGRES",
    max_retries=3,
    default_retry_delay=10,
)
def save_data_in_postgres(self, result):
    cluster_data = pd.read_json(json.dumps(result["clusters"]))
    cluster_stats = pd.read_json(json.dumps(result["cluster_stats"]))

    db = PostgresDB()
    df_to_db(
        df=cluster_data,
        table_name="user_clusters",
    )

    return {
        "clusters": cluster_data.to_dict("list"),
        "cluster_stats": cluster_stats.to_dict("list"),
        "saved_tracks": result["saved_tracks"],
    }
