import pandas as pd
import requests
import numpy as np
import base64
from utils.code_tools import transform_to_64, split_list
import json


class Authenticator:

    """
    A class for authenticating with the Spotify API and obtaining an access token.

    This class provides a mechanism for obtaining an access token from Spotify by exchanging an authorization code.

    Attributes:
    - client_id (str): The Spotify client ID.
    - client_secret (str): The Spotify client secret.
    - redirect_uri (str): The redirect URI for the OAuth flow.
    - auth_code (str): The authorization code obtained from the OAuth flow.
    - auth_token (str): The access token obtained from Spotify.

    Methods:
    - get_auth_token(): Retrieve an access token from Spotify using the provided authorization code.
    """

    def __init__(self, client_id, client_secret, redirect_uri, auth_code):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_code = auth_code
        self.auth_token = self.get_auth_token()

    def get_auth_token(self):
        """
        Retrieve an access token from Spotify using the provided authorization code.

        This method sends a POST request to the Spotify API to exchange the authorization code for an access token.

        :return: The access token obtained from Spotify.
        :rtype: str

        :raises requests.exceptions.RequestException: If there's an issue with the API request.
        :raises KeyError: If the response JSON does not contain the expected 'access_token' field.
        """
        headers = {
            "Authorization": f"Basic {transform_to_64(self.client_id+':'+self.client_secret)}"
        }

        body = {
            "grant_type": "authorization_code",
            "code": self.auth_code,
            "redirect_uri": self.redirect_uri,
        }

        response = requests.post(
            "https://accounts.spotify.com/api/token", headers=headers, data=body
        ).json()

        return response["access_token"]
