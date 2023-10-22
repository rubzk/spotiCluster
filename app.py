import json
import os
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    jsonify,
    session,
    make_response,
)
import requests
import configparser
from utils.flask_celery import make_celery
from src.tasks import (
    get_tracks,
    append_results,
    cluster_results,
    create_plots,
    save_data_in_postgres,
    get_saved_tracks,
)
from src.extract import DataExtractor
from src.auth import Authenticator
from urllib.parse import urlencode, quote_plus
from celery import current_app, chord


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

    res = make_response()

    res.headers["my-header"] = "Test Header"

    extractor = DataExtractor(auth.auth_token)

    user_data = extractor.get_user_id()

    res.set_cookie(
        "username",
        # value=user_id,
        value="carlos",
        expires=None,
        path="/",
    )

    user_data = extractor.get_all_playlists(user_data)

    # total_tracks = [get_saved_tracks.s(auth.auth_token)] + [
    #     get_tracks.s(auth.auth_token, playlist) for playlist in user_data.playlists
    # ]

    total_tracks = [
        get_tracks.s(auth.auth_token, playlist.dict())
        for playlist in user_data.playlists
    ]

    task = chord(total_tracks[:5])(
        append_results.s()
        | cluster_results.s()
        | save_data_in_postgres.s()
        | create_plots.s()
    )

    return redirect(url_for("taskstatus", celery_task_id=task.id))


@app.route("/status/<celery_task_id>", methods=["GET"])
def taskstatus(celery_task_id):
    task = celery.AsyncResult(celery_task_id)

    app.logger.info(f"status: {task.state}")

    if "application/json" in request.headers.get("Content-Type", ""):
        if task.state == "SUCCESS":
            return {"status": task.state, "plots": task.info["plots"]}

        app.logger.info(task.info)

        return {
            "status": task.state
        }  ### Here One idea I have is to return the status of the task and Update front end with it

    return render_template("plot.html", task_id=celery_task_id)


@app.route("/tasks/", methods=["GET"])
def get_tasks_celery():
    current_app.loader.import_default_modules()

    tasks = list(
        sorted(name for name in current_app.tasks if not name.startswith("celery."))
    )

    return jsonify(tasks)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
