from flask import Flask
from random import randint
from os import urandom
app = Flask(name)

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
def catch_all(path):
    randomdata = urandom(randint(10, 110))
    randomdata = randomdata.decode('utf-8', errors='ignore')

    return randomdata, randint(100, 999)

