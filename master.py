#!/usr/bin/env python

import time
import logging
import sys

import etcd
import yaml
import tornado.ioloop
import tornado.web
import tornado.httputil
import tornado.escape

import settings_master

logging.basicConfig(filename=settings_master.log, level=4)
ch = logging.StreamHandler(sys.stdout)
logging.debug('starting server')


class EtcdClient:
    def __init__(self, host='localhost', port=4001):
        self.etcd_client = etcd.client.Client(host=host, port=port)

    def set(self, key, value):
        key_str = '/docker-watcher/' + key
        self.etcd_client.set(key_str, value)

    def get(self, key):
        key_str = '/docker-watcher/' + key
        logging.debug(key_str)
        return self.etcd_client.get(key_str).value

    def lock(self, key):
        key_str = '/docker-watcher/' + key
        i = 0
        lock = self.etcd_client.get_lock(key_str, ttl=60)
        while (i < 60):
            lock.acquire()
            if (lock.is_locked()):
                logging.debug(key_str + ' locked')
                return lock
            else:
                time.sleep(1)
        logging.debug('unable to get lock on ' + key_str)
        return 1

    def unlock(self, lock):
        logging.debug('unlock ' + lock)
        lock.release()
        return 0

    def ls(self, key):
        ret = []
        key_str = '/docker-watcher/' + key
        r = self.etcd_client.read(key_str, recursive=True, sorted=True)
        for d in r.children:
            ret.append(d.key)
        logging.debug('ls ' + key_str)
        return ret


etcd_client = EtcdClient(settings_master.etcd_host, settings_master.etcd_port)


class DockerWatcherMaster:
    class RunHandler(tornado.web.RequestHandler):
        def post(self):
            req = self.request.body
            args = yaml.safe_load(req)
            # lock = etcd_client.lock('pods')
            if args['name'] in etcd_client.ls('pods'):
                self.write('container already exists')
                logging.debug('container already exists')
                self.set_status(404)
                return 1
            etcd_client.set('pods/' + args['name'], str(args))
            # etcd_client.unlock(lock)
            self.set_status(200)

    class AddSlaveHandler(tornado.web.RequestHandler):
        def post(self):
            logging.debug('add slave')
            slavename = self.request.body
            slaves = yaml.safe_load(etcd_client.get('slaves'))
            if slaves != None:
                if slavename in slaves:
                    logging.debug('slave ' + slavename + ' already exists')
                    self.set_status(500)
                else:
                    slaves.append(slavename)
                    etcd_client.set('slaves', str(yaml.safe_load(slaves)))
                    logging.debug('append slave ' + slavename)
                    self.set_status(200)
            else:
                print slavename
                print yaml.safe_load(list(slavename))
                etcd_client.set('slaves', str(yaml.safe_load(list(slavename))))
                logging.debug('slave ' + slavename)
                self.set_status(200)

    # class KillHandler(tornado.web.RequestHandler):
    #    def get(self):

    def run(self):
        self.tornadoapp = tornado.web.Application([
            # (r'/info', DockerWatcherMaster.InfoHandler),
            (r'/run', DockerWatcherMaster.RunHandler),
            (r'/add_slave', DockerWatcherMaster.AddSlaveHandler),
            # (r'/kill/(.*)', DockerWatcherMaster.KillHandler)
        ])
        self.tornadoapp.listen(settings_master.listen_port,
                               settings_master.listen_ip)
        tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    docker_watcher = DockerWatcherMaster()
    docker_watcher.run()
