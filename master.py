#!/usr/bin/env python

import commands

import settings_master
import etcd

import tornado.ioloop
import tornado.web
import tornado.httputil
import tornado.escape

class EtcdClient:
    def __init__(self, host='localhost', port=4001):
        self.etcd_client = etcd.client.Client(host=host, port=port)

    def set(self, key, value):
        key_str = '/docker-watcher/' + key
        self.etcd_client.set(key_str, value)

    def get(self, key):
        key_str = '/docker-watcher/' + key
        return self.etcd_client.get(key_str).value



class DockerWatcherMaster:
    def __init__(self, settings):
        self.settings = settings
        self.etcd_client = EtcdClient(settings_master.etcd_host, settings_master.etcd_port)
        self.pods_map = yaml_reader(settings_master.pods_file)

    class InfoHandler(tornado.web.RequestHandler):
        def get(self):



    def get_total_memory(self):
        output = commands.getoutput(free - m)
        return output

    def run(self):
        self.tornadoapp = tornado.web.Application([
            (r'/info', DockerWatcherMaster.InfoHandler),
            (r'/run/(.*)', DockerWatcherSlave.RunHandler),
            (r'/kill/(.*)', DockerWatcherSlave.KillHandler)
        ])
        self.tornadoapp.listen(settings_slave.listen_port,
                               settings_slave.listen_host)
        tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    docker_watcher = DockerWatcherMaster(settings_master)
    docker_watcher.run()
