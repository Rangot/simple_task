import os
import requests
import random
import urllib.parse

from flask import Flask, redirect, url_for, render_template, request, session
from functools import wraps
from time import time

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.debug = True

API_HOST = "https://apiproxy.telphin.ru"
APP_ID = "ca171d22eb2440338a3a5ea8b86182bf"
APP_SECRET = "f38d0e46e90949d38bbaab41f0ae8b66"
REDIRECT_URI = "http://localhost:5055/login/authorized"

headers = {'Content-type': 'application/json'}

body = {
    'redirect_uri': REDIRECT_URI,
    'client_id': APP_ID,
    'client_secret': APP_SECRET,
}


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = headers.get("Authorization")
        if not data:
            return authorize()
        else:
            token = session.get('token')
            if time() > float(token.get('expires_at')):
                return login()
        return f(*args, **kwargs)
    return decorated


@app.route('/authorize', methods=['GET'])
def authorize():
    request_url = "{host}/oauth/authorize".format(host=API_HOST)
    query = {
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'client_id': APP_ID,
        'scope': 'all'
    }
    enc_query = urllib.parse.urlencode(query)
    url = request_url + '?' + enc_query
    return redirect(url)


@app.route('/login/authorized', methods=['GET'])
def login():
    request_url = "{host}/oauth/token".format(host=API_HOST)
    token = session.get('token')
    # new token
    if not token:
        code = request.args.get('code')
        body.update({'grant_type': 'authorization_code', 'code': code})
    # refresh token
    else:
        body.update({'grant_type': 'refresh_token', 'refresh_token': token.get('refresh_token')})
    response = requests.post(request_url, data=body)
    if response.status_code == 200:
        session['token'] = {
            'access_token': response.json()['access_token'],
            'refresh_token': response.json()['refresh_token'],
            'expires_at': response.json()['expires_in'] + time()
        }
        token = session.get('token')
        headers.update({'Authorization': 'Bearer {access_token}'.format(access_token=token.get('access_token'))})
    elif response.status_code == 401:
        raise requests.HTTPError('Ошибка авторизации')
    else:
        raise requests.HTTPError('Неизвестная ошибка')
    return redirect(url_for('main'))


@app.route('/', methods=['GET'])
@requires_auth
def main():
    return render_template('main.html')


@app.route('/extlist/', methods=['GET'])
@requires_auth
def extlist():
    request_url = "{host}/api/ver1.0/client/@me/extension/".format(host=API_HOST)
    response = requests.get(request_url, headers=headers)
    extension_list = response.json()
    return render_template('main.html', extension_list=extension_list)


@app.route('/randomext/', methods=['GET'])
@requires_auth
def randomext():
    request_url = "{host}/api/ver1.0/client/@me/extension/".format(host=API_HOST)
    response = requests.get(request_url, headers=headers)
    extension_list = response.json()
    random_ext = random.choice(extension_list)
    return render_template('main.html', random_ext=random_ext)


if __name__ == '__main__':
    app.run(port='5055')
