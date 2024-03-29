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
import uuid
from datetime import datetime
from src.tasks import (
    get_tracks,
    append_results,
    cluster_results,
    create_plots,
    get_saved_tracks,
)
from celery import chord
from src.extract import DataExtractor
from src.models import Task
from src.db import select_user_runs, select_results

import logging

log = logging.getLogger(__name__)

config = configparser.RawConfigParser()
config.read(r"config.cfg")

celery_bp = Blueprint("celery_bp", __name__)


@celery_bp.route("/auth_ok/")
def auth():
    auth_code = request.args.get("code")

    auth = Authenticator(
        client_id=config.get("spotify-api", "client_id"),
        client_secret=config.get("spotify-api", "client_secret"),
        redirect_uri=config.get("spotify-api", "redirect_uri"),
        auth_code=auth_code,
    )

    extractor = DataExtractor(auth.auth_token)

    

    user_data = extractor.get_user_id()

    db_task_id = select_user_runs(user_data.id)

    log.warning(f"db task_id:{db_task_id}")

    if db_task_id:
        # return "Redirect with results"
        
        return redirect(url_for("celery_bp.get_results", task_id=db_task_id))
    # return redirect(url_for("celery_bp.get_results_user", auth_code=auth_code))
    else:
        print("start task and redirect to plot loading")
        task_ = Task(id=uuid.uuid4(),started_at=datetime.today())
        user_data = extractor.get_all_playlists(user_data)

    
        user_data.task = task_

        total_tracks = [get_saved_tracks.s(auth.auth_token)] + [
            get_tracks.s(auth.auth_token, playlist.dict())
            for playlist in user_data.playlists
        ]

        task = chord(total_tracks)(
            append_results.s(user=user_data.dict()) | cluster_results.s() | create_plots.s()
        )
    
        return redirect(url_for("celery_bp.get_results", task_id=task.id))


@celery_bp.route("/results/<task_id>", methods=["GET"])
def get_results(task_id):
    return render_template("plot.html", task_id=task_id)




@celery_bp.route("/status/<celery_task_id>", methods=["GET"])
def get_task_status(celery_task_id):

    task = current_app.celery.AsyncResult(celery_task_id)

    ## In the future  I would love to have an status bar 

    if "application/json" in request.headers.get("Content-Type", ""):

        if task.state == "SUCCESS":
            return {"plots": task.info}


        return {
            "status": task.state
        }  


@celery_bp.route("/get_old_result/<task_id>", methods=["GET"])
def get_old_results(task_id):

    try:
        uuid.UUID(task_id)
    except ValueError:
        return {"plots" : None}

    data = select_results(task_id)

    return data