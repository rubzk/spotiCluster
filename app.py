import os
from flask import Flask

import configparser
from utils.flask_celery import make_celery

from src.db_models import create_db_and_tables, create_engine

from blueprints.index_blueprints.index_blueprint import index_bp
from blueprints.celery_blueprints.celery_blueprint import celery_bp


from sqlmodel import Session, create_engine


app = Flask(__name__)
app.register_blueprint(index_bp)
app.register_blueprint(celery_bp)
app.config["CELERY_BROKER_URL"] = os.environ["CELERY_BROKER_URL"]
app.config["CELERY_BACKEND"] = os.environ["CELERY_BACKEND"]

celery = make_celery(app)

app.celery = celery

if __name__ == "__main__":
    create_db_and_tables()
    app.run(host="0.0.0.0", port=5000, debug=True)
    
