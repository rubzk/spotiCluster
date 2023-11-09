from flask import (
    Blueprint,
    jsonify,
    make_response,
    request,
    redirect,
    url_for,
    render_template,
    current_app,
)
from src.auth import Authenticator
import configparser
from src.tasks import (
    get_tracks,
    append_results,
    cluster_results,
    create_plots,
    save_data_in_postgres,
    get_saved_tracks,
)
from celery import chord
from src.extract import DataExtractor

config = configparser.RawConfigParser()
config.read(r"config.cfg")

celery_bp = Blueprint("celery_bp", __name__)


@celery_bp.route("/auth_ok/")
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

    total_tracks = [get_saved_tracks.s(auth.auth_token)] + [
        get_tracks.s(auth.auth_token, playlist.dict())
        for playlist in user_data.playlists
    ]

    # task = chord(total_tracks[:5])(
    #     append_results.s(user=user_data.dict())
    #     | cluster_results.s()
    #     | save_data_in_postgres.s()
    #     | create_plots.s()
    # )

    task = chord(total_tracks)(
        append_results.s(user=user_data.dict()) | cluster_results.s() | create_plots.s()
    )

    return redirect(url_for("celery_bp.taskstatus", celery_task_id=task.id))


@celery_bp.route("/status/<celery_task_id>", methods=["GET"])
def taskstatus(celery_task_id):
    task = current_app.celery.AsyncResult(celery_task_id)

    # app.logger.info(f"status: {task.state}")

    if "application/json" in request.headers.get("Content-Type", ""):
        if task.state == "SUCCESS":
            # with open("./output/task_info.json", "w") as json_file:
            #     json.dump(task.info, json_file)

            return {"plots": task.info}

        # app.logger.info(task.info)

        return {
            "status": task.state
        }  ### Here One idea I have is to return the status of the task and Update front end with it

    return render_template("plot.html", task_id=celery_task_id)