#!flask/bin/python
# -*- coding: utf-8 -*-
from flask import Flask
from flask import render_template
from flask import request
from flask import send_from_directory

import pandas as pd
import csv
#from sklearn.linear_model import Ridge
import joblib
#import dash
#import dash_core_components as dcc
#import dash_html_components as html

app = Flask(__name__, static_url_path='/static')

import os

def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))

root = root_dir() + '/'

@app.route('/data/<path:path>')
def send_data(path):
    return send_from_directory('data', path)

def predict(data):

    debug = ''

    data = pd.DataFrame(data=data)

    # load your model
    r_clf = joblib.load(root+'ridge.pkl')
    result = r_clf.predict(data).round().astype(int)
    return result

@app.route('/predict', methods=['POST'])
def send_predict():
    result = ''
    try:
        q = request.form
        data = {
            'Освещенность': [q['lighting'] if 'lighting' in q else '100'],
            'Влажность почвы': [q['moisture'] if 'moisture' in q else '70'],
            'Температура': [q['temperature'] if 'temperature' in q else '0'],
            'Кислотность почвы': [q['acidity'] if 'acidity' in q else '7'],
            }

        #amount, size, taste = predict(data)
        result = predict(data)[0]
        print(result)

        #result = dict(amount=amount, size=size, taste=taste)
    except Exception as e:
        #result = dict(amount=0, size=0, taste=0)
        result = 10

    #return 'static/' + str(result)+ ".jpg"
    return str(result)


def pack_data(x):

    data = {
        'Освещенность': [x['Освещенность']],
        'Влажность почвы': [x['Влажность почвы']],
        'Температура': [x['Температура']],
        'Кислотность почвы': [x['Кислотность почвы']], }

    return data


@app.route('/upload', methods=['POST'])
def send_upload():

    result = request.form["text"]
    if not result:
        try:
            f = request.files["file"]
            if f.filename:
                result = f.read().decode('utf-8')
        except:
            result = 'error reading file'

    try:
        reader = csv.DictReader(result.splitlines())
        out = []
        i = 1
        for x in reader:
            perc, debug = predict(pack_data(x))
            out.append('%.2f%%' % (perc))
            i += 1
        result = '\n'.join(out)

    except Exception as e:
        result = str(e)


    return result


@app.route('/', methods=['GET', 'POST'])
def index():
    data = {
        'lighting': ['5','10','15','20','25','30','35','40','45','50','55'],
        'moisture': ['50', '55','60','65','70','75','80','85','90'],
        'temperature': ['0','5','10','15','20','25','30', '35', '40'],
        'acidity': ['5.5','6.0', '6.5','7.0', '7.5','8.0','8.5'],

    }

    return render_template('info.html', title='Home', data=data)

if __name__ == '__main__':
    app.run(debug=True)
