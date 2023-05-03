import json
import os
from flask import Flask, render_template, redirect, url_for, request, jsonify, session
import requests
import configparser
from utils.flask_celery import make_celery
from src.tasks import concatenate_all_tracks,get_tracks,append_results
from src.extract import DataExtractor
from src.auth import Authenticator
from urllib.parse import urlencode, quote_plus
from celery import current_app, chord
#from flask_assets import Environment, Bundle


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

    extractor = DataExtractor(auth.auth_token)

    playlists = extractor.get_all_playlists()

    total_tracks = [get_tracks.s(auth.auth_token, playlist) for playlist in playlists]

    task = chord(total_tracks)(append_results.s())
    #task = concatenate_all_tracks.apply_async(args=(auth.auth_token,))

    return (
        render_template("plot.html", task_id=task.id),
        202,
        {"Location": url_for("taskstatus", task_id=task.id)},
    )


@app.route("/status/<task_id>", methods=["GET"])
def taskstatus(task_id):

    task = celery.AsyncResult(task_id)

    app.logger.info(f"status: {task.state}")

    if task.state == 'SUCCESS':
        return {"status" : task.state,
                "plots" :task.info["plots"]}

    #app.logger.info(task.info)

    return {"status" : task.state}

    # try:

    #     if task.state != 'SUCCESS':

    #         app.logger.info("Entrando al if")

    #         task = celery.AsyncResult(task.info["plot"])

    #         return task.info
    #     else:
    #         return "Not available yet"

    # except TypeError as e:


    #     return "Not available yet"

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.exception(f"Unhandled exception: {e}")
    return "Internal server error", 500

@app.route("/tasks/", methods=["GET"])
def get_tasks_celery():

    current_app.loader.import_default_modules()

    tasks = list(
        sorted(name for name in current_app.tasks if not name.startswith("celery."))
    )

    return jsonify(tasks)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
