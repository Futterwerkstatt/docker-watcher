#!/usr/bin/env python

import argparse
import urllib
import yaml

import requests


def yaml_reader(filename):
    with  open(filename) as f:
        datamap = yaml.safe_load(f)
    return datamap


def run(server, config):
    print yaml_reader(config)
    url = urllib.urlencode()
    #req = requests.get('http://' + server + '/run/' +)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-s', '--server', help='master server url to connect')
    arg_parser.add_argument('-a', '--action', help='run, stop, or info')
    arg_parser.add_argument('-p', '--pods', help='pods file to run')
    arg_parser.add_argument('-k', '--kill', help='container id to kill')
    args = vars(arg_parser.parse_args())
    if args['action'] == 'run':
        run(args['server'], args['pods'])
