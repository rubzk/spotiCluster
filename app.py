import json
import os
from flask import Flask, render_template, redirect, url_for, request, jsonify, session
import requests
import configparser
from utils.flask_celery import make_celery
from src.tasks import concatenate_all_tracks
from src.extract import DataExtractor
from src.auth import Authenticator
from urllib.parse import urlencode, quote_plus


app = Flask(__name__)
app.config["CELERY_BROKER_URL"] = os.environ["CELERY_BROKER_URL"]
app.config["CELERY_BACKEND"] = os.environ["CELERY_BACKEND"]

celery = make_celery(app)

config = configparser.RawConfigParser()
config.read(r"config.cfg")


@app.route("/")
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


@app.route("/auth_ok/")
def auth():
    auth_code = request.args.get("code")
    # app.logger.info(f"auth_code: {auth_code}")

    auth = Authenticator(
        client_id=config.get("spotify-api", "client_id"),
        client_secret=config.get("spotify-api", "client_secret"),
        redirect_uri=config.get("spotify-api", "redirect_uri"),
        auth_code=auth_code,
    )

    task = concatenate_all_tracks.apply_async(args=(auth.auth_token,))

    return (
        render_template("plot.html", task_id=task.id),
        202,
        {"Location": url_for("taskstatus", task_id=task.id)},
    )


@app.route("/status/<task_id>", methods=["GET"])
def taskstatus(task_id):
    task = celery.AsyncResult(task_id)
    if task.state == "PENDING":
        response = {
            "state": task.state,
            "current": 0,
            "total": 1,
            "status": "Pending...",
        }
    elif task.state != "FAILURE":
        response = {
            "state": task.state,
            "current": task.info.get("current", 0),
            "total": task.info.get("total", 1),
            "status": task.info.get("status", ""),
        }
        if "plots" in task.info:
            response["plots"] = task.info["plots"]
    else:
        response = {
            "state": task.state,
            "current": 1,
            "total": 1,
            "status": str(task.info),
        }
    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
