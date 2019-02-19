from flask import Flask, redirect, url_for, render_template

import requests
import random


app = Flask(__name__)
app.debug = True

API_HOST = "https://apiproxy.telphin.ru"
APP_ID = "ca171d22eb2440338a3a5ea8b86182bf"
APP_SECRET = "f38d0e46e90949d38bbaab41f0ae8b66"
REDIRECT_URI = "http://simplesapp:5055/login/authorized"

headers = {'Content-type': 'application/json',
           'Authorization': ''}

body = {
    'grant_type': 'client_credentials',
    'redirect_uri': REDIRECT_URI,
    'client_id': APP_ID,
    'client_secret': APP_SECRET,
}


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET'])
def login():
    request_url = "{host}/oauth/token".format(host=API_HOST)
    response = requests.post(request_url, data=body)
    if response.status_code == 200:
        access_token = response.json()['access_token']
    elif response.status_code == 401:
        raise requests.HTTPError('Ошибка авторизации: {error}'.format(error=response.json()['error']))
    else:
        raise requests.HTTPError('Неизвестная ошибка')
    headers.update({'Authorization': 'Bearer {access_token}'.format(access_token=access_token)})
    return redirect(url_for('main'))


@app.route('/main', methods=['GET'])
def main():
    return render_template('main.html')


@app.route('/extlist/', methods=['GET'])
def extlist():
    request_url = "{host}/api/ver1.0/client/@me/extension/".format(host=API_HOST)
    response = requests.get(request_url, headers=headers)
    extension_list = response.json()
    return render_template('main.html', extension_list=extension_list)


@app.route('/randomext/', methods=['GET'])
def randomext():
    request_url = "{host}/api/ver1.0/client/@me/extension/".format(host=API_HOST)
    response = requests.get(request_url, headers=headers)
    extension_list = response.json()
    random_ext = random.choice(extension_list)
    return render_template('main.html', random_ext=random_ext)


if __name__ == '__main__':
    app.run()
