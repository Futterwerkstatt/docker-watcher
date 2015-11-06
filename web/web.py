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
    logging.info('/pods_info')
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


@app.route('/total_cluster_info')
def total_cluster_info():
    logging.info('total_cluster_info')
    url = 'http://' + settings_web.master + '/cluster_info'
    req = requests.get(url)
    req_list = yaml.safe_load(req.text)
    info = {'total_cpu': 0, 'total_memory': 0, 'total_disk': 0, 'total_used_cpu': 0,
            'total_used_memory': 0, 'total_used_disk': 0}
    for d in req_list:
        info['total_cpu'] += int(d['total_cpus'])
        info['total_memory'] += int(d['total_memory'])
        info['total_disk'] += int(d['total_disk'])
        info['total_used_cpu'] += int(d['used_cpus'])
        info['total_used_memory'] += int(d['used_memory'])
        info['total_used_disk'] += int(d['used_disk'])
    return json.dumps(info)


@app.route('/containers_info')
def containers_info():
    logging.info('containers_info')
    url = 'http://' + settings_web.master + '/containers_info'
    req = requests.get(url)
    res = yaml2json(req.text)
    return res


if __name__ == '__main__':
    logging.warning('===starting web===')
    app.run(port=settings_web.listen_port, host=settings_web.listen_host, debug=True)
