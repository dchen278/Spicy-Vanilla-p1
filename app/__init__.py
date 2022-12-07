# Spicy Vanilla: David Chen, Jing Feng, Jeremy Kwok, and Matthew Yee
# SoftDev

from flask import Flask  # facilitate flask webserving
from flask import render_template  # facilitate jinja templating
from flask import request  # facilitate form submission
import requests
import json

app = Flask(__name__)  # create Flask object


@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        data = request.form
        print(data)
        return render_template('index.html')


if __name__ == "__main__":  # false if this file imported as module
    # enable debugging, auto-restarting of server when this file is modified
    app.debug = True
    app.run()
