import os
from flask import Flask

import configparser
from utils.flask_celery import make_celery

from blueprints.index_blueprints.index_blueprint import index_bp
from blueprints.celery_blueprints.celery_blueprint import celery_bp


app = Flask(__name__)
app.register_blueprint(index_bp)
app.register_blueprint(celery_bp)
app.config["CELERY_BROKER_URL"] = os.environ["CELERY_BROKER_URL"]
app.config["CELERY_BACKEND"] = os.environ["CELERY_BACKEND"]

celery = make_celery(app)

app.celery = celery

config = configparser.RawConfigParser()
config.read(r"config.cfg")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
