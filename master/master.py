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
import requests

import settings_master

logging.basicConfig(filename=settings_master.log, level=4)
ch = logging.StreamHandler(sys.stdout)
logging.debug('starting master')


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
            ret.append(str(d.key).split('/')[-1])
        return ret


etcd_client = EtcdClient(settings_master.etcd_host, settings_master.etcd_port)


class DockerWatcherMaster:
    class AddPodHandler(tornado.web.RequestHandler):
        def post(self):
            logging.debug('add pod')
            req = self.request.body
            args = yaml.safe_load(req)
            # lock = etcd_client.lock('pods')
            if args['name'] in etcd_client.ls('pods'):
                self.write('pod already exists')
                logging.debug('pod already exists')
                self.set_status(500)
            else:
                etcd_client.set('pods/' + args['name'], str(args))
                # etcd_client.unlock(lock)
                self.set_status(200)

    class AddSlaveHandler(tornado.web.RequestHandler):
        def post(self):
            logging.debug('add slave')
            slavename = self.request.body
            logging.debug(str(etcd_client.ls('slaves/')))
            url = 'http://' + slavename + '/info'
            req = requests.get(url)
            slave_info = str(req.text)
            slave_config = yaml.safe_load(slave_info)
            logging.debug(slave_config)
            slave_config['used_cpus'] = 0
            slave_config['used_memory'] = 0
            slave_config['used_disk'] = 0
            etcd_client.set('slaves/' + slavename, yaml.safe_dump(slave_config))
            self.set_status(200)

    # class KillHandler(tornado.web.RequestHandler):
    #    def get(self):
    class RunPodHandler(tornado.web.RequestHandler):
        def post(self):
            logging.debug('run pod')
            podname = self.request.body
            pod_config = yaml.safe_load(etcd_client.get('pods/' + podname))
            slaves_list = etcd_client.ls('slaves/')
            for slave in slaves_list:
                slave_config = yaml.safe_load(etcd_client.get('slaves/' + slave))
                free_cpus = int(slave_config['total_cpus']) - int(slave_config['used_cpus'])
                free_memory = int(slave_config['total_memory']) - int(slave_config['used_memory'])
                free_disk = int(slave_config['total_disk']) - int(slave_config['used_disk'])
                cpus = int(pod_config['cpus'])
                memory = int(pod_config['memory'])
                disk = int(pod_config['disk'])
                instances_count = pod_config['instances']
                if cpus <= free_cpus and memory <= free_memory and disk <= free_disk:
                    url = 'http://' + slave + '/run_pod'
                    body = str(yaml.safe_dump({'image': pod_config['image'],
                                               'command': pod_config['command'],
                                               'name': pod_config['name']}))
                    req = requests.post(url, data=body)
                    instances_count -= 1
                    if instances_count == 0:
                        break
                self.set_status(200)

    class SlaveInfoHandler(tornado.web.RequestHandler):
        def post(self):
            logging.debug('slave_info')
            slave_addr = self.request.body
            url = 'http://' + slave_addr + '/info'
            req = requests.get(url)
            info_data = str(req.text)
            self.write(info_data)

    def run(self):
        self.tornadoapp = tornado.web.Application([
            (r'/slave_info', DockerWatcherMaster.SlaveInfoHandler),
            (r'/add_pod', DockerWatcherMaster.AddPodHandler),
            (r'/add_slave', DockerWatcherMaster.AddSlaveHandler),
            (r'/run_pod', DockerWatcherMaster.RunPodHandler),
            # (r'/kill/(.*)', DockerWatcherMaster.KillHandler)
        ])
        self.tornadoapp.listen(settings_master.listen_port,
                               settings_master.listen_ip)
        tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    docker_watcher = DockerWatcherMaster()
    docker_watcher.run()
