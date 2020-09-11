import json
from flask import Flask, render_template, redirect, url_for, request
import requests 
from utils.extract import authenticate, transform_to_64
import credentials

app = Flask(__name__)

"""client_id = 'dc0ae7e239524e8e9c42ebaaec57d5fc'
client_secret = '56ad76b0390e482e8c0327945ba4ac0b'
redirect_uri = 'http://localhost:5000/auth_ok'
"""

#auth_url = 'https://accounts.spotify.com/authorize?'+'client_id='+credentials.client_id+'&response_type=code'+'&redirect_uri='+credentials.redirect_uri+'&scope=user-read-private'


@app.route('/')
def index():
    return render_template('index.html', auth_url =credentials.auth_url)


@app.route('/auth_ok/', methods=['GET', 'POST'])
def auth_ok():
    auth_code = request.args.get('code')
    auth_token, user_id = authenticate(auth_code, credentials.client_id, credentials.client_secret,credentials.redirect_uri)
    return '{} ,{}'.format(auth_token, user_id)



if __name__ == '__main__':
    app.run(debug=True)

