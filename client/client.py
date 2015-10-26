#!/usr/bin/env python

import argparse

import yaml
import requests
import subprocess
import os

def add_pod(server, pod):
    url = 'http://' + server + '/add_pod'
    with  open(pod) as f:
        data = str(yaml.safe_load(f))
    req = requests.post(url, data=data)
    print req.status_code


def add_slave(server, slaveaddr):
    url = 'http://' + server + '/add_slave'
    req = requests.post(url, data=slaveaddr)
    print req.status_code


def run_pod(server, podname):
    url = 'http://' + server + '/run_pod'
    req = requests.post(url, data=podname)
    print req.text


def slave_info(server, slavename):
    url = 'http://' + server + '/slave_info'
    req = requests.post(url, data=slavename)
    print req.text

def upload_slave(slave, filename):
    slave_host = slave.split(':')[0]
    ssh_host = 'ssh root@' + slave_host + ' '
    cmds = []
    cmds.append(ssh_host + 'mkdir /opt/docker-watcher')
    cmds.append('scp ' + filename + ' root@' + slave_host + '/opt/docker-watcher/')
    cmds.append(ssh_host + '"wget -qO- https://get.docker.com/ | sh"')
    cmds.append(ssh_host + 'apt-get install python python-pip')
    cmds.append(ssh_host + 'pip install tornado docker-py psutil')
    for cmd in cmds:
        print '=== ' + cmd + ' ==='
        print subprocess.Popen(cmd, shell=True,
                               stdout=subprocess.PIPE).stdout.read()

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-s', '--server', help='master server url to connect')
    arg_parser.add_argument('-a', '--action', help='run, stop, add_slave or info')
    arg_parser.add_argument('-p', '--pod', help='pods file to set')
    arg_parser.add_argument('-r', '--run', help='pod to run')
    arg_parser.add_argument('-k', '--kill', help='container id to kill')
    arg_parser.add_argument('-l', '--slave', help='slave address')
    arg_parser.add_argument('-f', '--file', help='slave file to upload')
    args = vars(arg_parser.parse_args())
    action = args['action']
    server = args['server']
    if action == 'run_pod':
        run_pod(server, args['run'])
    elif action == 'upload_slave':
        upload_slave(args['slave'], args['file'])
    elif action == 'add_pod':
        add_pod(server, args['pod'])
    elif action == 'add_slave':
        add_slave(server, args['slave'])
    elif action == 'slave_info':
        slave_info(server, args['slave'])
