#!/usr/bin/env python

import argparse
import socket

import etcd
import docker

import settings
import yaml

class ArgParser:
    def __init__(self):
        self.arg_parser = argparse.ArgumentParser(description='Docker watcher')
        self.arg_parser.add_argument('--mode', help='Daemon mode: master or slave')
        self.args = self.arg_parser.parse_args()

    def mode(self):
        return self.args.mode


class SockerServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

    def listen(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((settings.listen_ip, settings.listen_port))
        self.socket.listen(1)

    def get(self):
        conn, addr = self.socket.accept()
        data = conn.recv(settings.socket_buffer_size)
        return str(data)

    def send(self, host, port, data):
        self.socket.connect((host, port))
        self.socket.send(data)


class EtcdClient:
    def __init__(self):
        self.etcd_client = etcd.Client(host=settings.etcd_host, port=settings.etcd_port)

    def set(self, key, value, ttl=0):
        set_str = '/docker-watcher/' + settings.nodename + '/' + key
        if ttl == 0:
            self.etcd_client.write(set_str, value)
        else:
            self.etcd_client.write(set_str, value, ttl)

    def get(self, key):
        key_str = '/docker-watcher/' + settings.nodename + '/' + key
        return self.etcd_client.read(key_str).value


class YamlReader:



class DockerClient:
    def __init__(self, url='unix://var/run/docker.sock'):
        self.client = docker.Client(base_url=url)


class DockerWatcher:
    def __init__(self):
        self.etcd_client = EtcdClient()


class DockerWatcherMaster(DockerWatcher):
    def run(self):


class DockerWatcherSlave(DockerWatcher):
    def run(self):


if __name__ == '__main__':
    args = ArgParser()
    mode = args.mode()
    if args == 'master':
        docker_watcher = DockerWatcherMaster()
    elif args == 'slave':
        docker_watcher = DockerWatcherSlave()
    else:
        print 'wrong mode, exiting...'
    docker_watcher.run()
    exit(0)
