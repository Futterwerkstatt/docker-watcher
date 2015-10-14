#!/usr/bin/env python

import tornado.ioloop
import tornado.web
import tornado.httputil
import etcd
import yaml

import psutil

import docker

import settings_slave


class EtcdClient:
    def __init__(self, host='localhost', port=4001):
        self.etcd_client = etcd.client.Client(host=host, port=port)

    def set(self, key, value):
        key_str = '/docker-watcher/' + key
        self.etcd_client.set(key_str, value)

    def get(self, key):
        key_str = '/docker-watcher/' + key
        return self.etcd_client.get(key_str).value


class DockerClient:
    def __init__(self, url='unix://var/run/docker.sock'):
        self.client = docker.Client(base_url=url)

class HostInfo:

    def __init__(self):
        self.used_cpus = 0
        self.used_memory = 0
        self.used_disk = 0

    def use_disk(self, disk):
        self.used_disk += disk

    def use_cpus(self, cpus):
        self.used_cpus += cpus

    def use_memory(self, memory):
        self.used_memory += memory

    def get_used_memory(self):

class DockerWatcherSlave:
    def __init__(self):
        self.etcd_client = EtcdClient(host=settings_slave.etcd_host,
                                      port=settings_slave.etcd_port)


    class InfoHandler(tornado.web.RequestHandler):
        def return_mb(self, value):
            return int(value / float(2 ** 20))

        def get(self):
            print '/info'
            info_dict = {}
            info_dict['total_cpus'] = psutil.cpu_count()
            info_dict['used_cpus'] = DockerWatcherSlave.used_cpus
            info_dict['total_memory'] = self.return_mb(psutil.virtual_memory().total)
            info_dict['used_memory'] = DockerWatcherSlave.used_memory
            info_dict['total_disk'] =
            self.write(yaml.dump(info_dict))

    class StopHandler(tornado.web.RequestHandler):
        def get(self):
            print '/stop'
            tornado.ioloop.IOLoop.instance().stop()

    def run(self):
        self.tornadoapp = tornado.web.Application([
            (r'/info', DockerWatcherSlave.InfoHandler),
            (r'/stop', DockerWatcherSlave.StopHandler)])
        self.tornadoapp.listen(settings_slave.listen_port,
                               settings_slave.listen_host)
        tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    print 'starting'
    docker_watcher = DockerWatcherSlave()
    docker_watcher.run()
    print 'exiting'
