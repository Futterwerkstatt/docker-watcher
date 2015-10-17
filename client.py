#!/usr/bin/env python

import argparse

import yaml

import requests


def yaml_reader(filename):
    return str(datamap)


def run(server, config):
    url = 'http://' + server + '/run'
    with  open(config) as f:
        data = str(yaml.safe_load(f))
    req = requests.post(url, data=data)
    print req.status_code


def add_slave(server, slaveaddr):
    url = 'http://' + server + '/add_slave'
    req = requests.post(url, data=slaveaddr)
    print req.status_code


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-s', '--server', help='master server url to connect')
    arg_parser.add_argument('-a', '--action', help='run, stop, add_slave or info')
    arg_parser.add_argument('-r', '--run', help='pods file to run')
    arg_parser.add_argument('-k', '--kill', help='container id to kill')
    arg_parser.add_argument('-l', '--slave', help='slave address to add')
    args = vars(arg_parser.parse_args())
    if args['action'] == 'run':
        run(args['server'], args['run'])
    elif args['action'] == 'add_slave':
        add_slave(args['server'], args['slave'])
