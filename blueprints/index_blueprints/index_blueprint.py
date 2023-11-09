from flask import Blueprint, jsonify, render_template
from urllib.parse import urlencode, quote_plus
import configparser

config = configparser.RawConfigParser()
config.read(r"config.cfg")
index_bp = Blueprint("index_bp", __name__)


@index_bp.route("/")
def index():
    payload = {
        "client_id": config.get("spotify-api", "client_id"),
        "response_type": "code",
        "redirect_uri": config.get("spotify-api", "redirect_uri"),
        "scope": config.get("spotify-api", "scope"),
        "show_dialog": "true",
    }

    query_parameters = urlencode(payload, quote_via=quote_plus)

    return render_template(
        "index.html", auth_url=config.get("spotify-api", "url") + query_parameters
    )
