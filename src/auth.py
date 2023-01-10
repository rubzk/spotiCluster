import pandas as pd
import requests
import numpy as np
import base64
from utils.code_tools import transform_to_64, split_list
import requests
import json


class Authenticator:
    def __init__(self, client_id, client_secret, redirect_uri, auth_code):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_code = auth_code
        self.auth_token = self.get_auth_token()

    def get_auth_token(self):

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
