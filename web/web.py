#!/usr/bin/env python

import settings_web
import logging
import sys
from flask import Flask, render_template
import requests
import yaml
import json

logging.basicConfig(filename=settings_web.log, level=30,
                    format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', )
ch = logging.StreamHandler(sys.stdout)
app = Flask(__name__)


def yaml2json(yaml_str):
    return json.dumps(yaml.safe_load(yaml_str))


@app.route('/')
def index():
    logging.warning('/')
    return render_template('index.html')


@app.route('/pods_info')
def pods_info():
    logging.warning('/pods_info')
    url = 'http://' + settings_web.master + '/pods_info'
    req = requests.get(url)
    res = yaml2json(req.text)
    return res


@app.route('/cluster_info')
def cluster_info():
    logging.info('cluster_info')
    url = 'http://' + settings_web.master + '/cluster_info'
    req = requests.get(url)
    res = yaml2json(req.text)
    return res


if __name__ == '__main__':
    logging.warning('===starting web===')
    app.run(port=settings_web.listen_port, host=settings_web.listen_host, debug=True)
