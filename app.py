import json
import os
from flask import Flask, render_template, redirect, url_for, request, jsonify, session
import requests 
from src.extract import DataExtractor
import credentials
from src.transform import TransformDataFrame
from src.plot import Plot3D
from plotly.utils import PlotlyJSONEncoder
from utils.flask_celery import make_celery
from src.tasks import tarea

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = os.environ['CELERY_BROKER_URL']
app.config['CELERY_BACKEND'] = os.environ['CELERY_BACKEND']

celery = make_celery(app)


@app.route('/')
def index():
    return render_template('index.html', auth_url=credentials.auth_url)


@app.route('/auth_ok/')
def auth():
    auth_code = request.args.get('code')
    app.logger.info(f'auth_code: {auth_code}')
    task = tarea.delay(auth_code)

    return render_template('plot.html', task_id=task.id), 202, {'Location': url_for('taskstatus', task_id=task.id)}


@app.route('/status/<task_id>', methods=['GET','POST'])
def taskstatus(task_id):
    task = celery.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'plots' in task.info:
            response['plots'] = task.info['plots']
    else:
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),
        }
    return jsonify(response)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


