#!/usr/bin/env python

import logging
import sys
import os

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from common import EtcdClient
import yaml
import tornado.ioloop
import tornado.web
import tornado.httputil
import tornado.escape
import requests

import settings_master

logging.basicConfig(filename=settings_master.log, level=30,
                    format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', )
ch = logging.StreamHandler(sys.stdout)
logging.warning('starting master')

etcd_client = EtcdClient.EtcdClient(settings_master.etcd_host, settings_master.etcd_port, settings_master.etcd_timeout)


class DockerWatcherMaster:
    class AddPodHandler(tornado.web.RequestHandler):
        def post(self):
            '''add pod'''
            logging.warning('add pod')
            etcd_client.lock()
            pod = self.request.body
            args = yaml.safe_load(pod)
            podname = args['name']
            # lock = etcd_client.lock('pods')
            if podname in etcd_client.ls('pods'):
                self.write('pod already exists, replacing')
                logging.warning('pod already exists, replacing')
            args['enabled'] = 0
            args['containers'] = [{}]
            etcd_client.set('pods/' + podname, str(args))
            logging.warning('pod ' + podname + ' added')
            etcd_client.unlock()
            self.write('pod ' + podname + ' added')
            self.set_status(200)

    class AddSlaveHandler(tornado.web.RequestHandler):
        def post(self):
            '''add slave'''
            logging.warning('add slave')
            etcd_client.lock()
            slavename = self.request.body
            logging.warning(str(etcd_client.ls('slaves/')))
            url = 'http://' + slavename + '/info'
            req = requests.get(url)
            slave_info = str(req.text)
            slave_config = yaml.safe_load(slave_info)
            logging.warning(slave_config)
            slave_config['used_cpus'] = 0
            slave_config['used_memory'] = 0
            slave_config['used_disk'] = 0
            slave_config['name'] = slavename
            if slavename in etcd_client.ls('slaves'):
                self.write('slave already exists, replacing')
                logging.warning('slave already exists, replacing')
            etcd_client.set('slaves/' + slavename, yaml.safe_dump(slave_config))
            etcd_client.unlock()
            self.write('slave ' + slavename + ' added')
            self.set_status(200)

    # class KillHandler(tornado.web.RequestHandler):
    #    def get(self):
    class RunPodHandler(tornado.web.RequestHandler):
        def post(self):
            '''run pod'''
            logging.warning('run pod')
            etcd_client.lock()
            podname = self.request.body
            if podname not in etcd_client.ls('pods/'):
                logging.warning('pod ' + podname + ' not found')
                self.set_status(500)
                return 0
            pod = etcd_client.get('pods/' + podname)
            pod_dict = yaml.safe_load(pod)
            pod_dict['enabled'] = 1
            etcd_client.set('pods/' + podname, str(yaml.safe_dump(pod_dict)))
            logging.warning('pod ' + podname + ' queued to run')
            etcd_client.unlock()
            self.write('pod ' + podname + ' queued to run')
            self.set_status(200)

    class SlaveInfoHandler(tornado.web.RequestHandler):
        def post(self):
            '''slave info'''
            logging.warning('slave_info')
            etcd_client.lock()
            slavename = str(self.request.body)
            info = etcd_client.get('slaves/' + slavename)
            etcd_client.unlock()
            self.write(info)
            self.set_status(200)

    class ClusterInfoHandler(tornado.web.RequestHandler):
        def get(self):
            '''get cluster info'''
            logging.info('cluster_info')
            etcd_client.lock()
            slaves_list = etcd_client.ls('slaves/')
            info = []
            for slave in slaves_list:
                slave_config = yaml.safe_load(etcd_client.get('slaves/' + slave))
                info.append(slave_config)
            etcd_client.unlock()
            self.write(yaml.safe_dump(info))
            self.set_status(200)

    class StopMasterHandler(tornado.web.RequestHandler):
        def get(self):
            '''stop master'''
            logging.warning('/stop_master')
            self.write('stopping master\n')
            self.set_status(200)
            tornado.ioloop.IOLoop.instance().stop()

    class StopSlaveHandler(tornado.web.RequestHandler):
        def post(self):
            '''stop slave'''
            logging.warning('/stop_slave')
            slave = self.request.body
            url = 'http://' + slave + '/stop'
            req = requests.get(url)
            self.write(req.text)
            self.set_status(200)

    class ContainersInfoHandler(tornado.web.RequestHandler):
        def get(self):
            '''get containers info'''
            logging.info('/containers_info')
            etcd_client.lock()
            info = []
            slaves_list = etcd_client.ls('slaves/')
            etcd_client.unlock()
            for slave in slaves_list:
                url = 'http://' + slave + '/get_containers'
                req = requests.get(url)
                for container in yaml.safe_load(req.text):
                    container['slave_name'] = slave
                    info.append(container)
            self.write(str(yaml.safe_dump(info)))
            self.set_status(200)

    class PodsInfoHandler(tornado.web.RequestHandler):
        def get(self):
            ''' get pods info '''
            logging.info('/pods_info')
            etcd_client.lock()
            pods_info = []
            pods = etcd_client.ls('pods/')
            for pod in pods:
                pod_info = yaml.safe_load(etcd_client.get('pods/' + pod))
                pods_info.append(pod_info)
            etcd_client.unlock()
            self.write(yaml.safe_dump(pods_info))
            self.set_status(200)

    def run(self):
        '''run tornado app'''
        self.tornadoapp = tornado.web.Application([
            (r'/slave_info', DockerWatcherMaster.SlaveInfoHandler),
            (r'/add_pod', DockerWatcherMaster.AddPodHandler),
            (r'/add_slave', DockerWatcherMaster.AddSlaveHandler),
            (r'/run_pod', DockerWatcherMaster.RunPodHandler),
            (r'/cluster_info', DockerWatcherMaster.ClusterInfoHandler),
            (r'/containers_info', DockerWatcherMaster.ContainersInfoHandler),
            (r'/stop_master', DockerWatcherMaster.StopMasterHandler),
            (r'/stop_slave', DockerWatcherMaster.StopSlaveHandler),
            (r'/pods_info', DockerWatcherMaster.PodsInfoHandler)
            # (r'/kill/(.*)', DockerWatcherMaster.KillHandler)
        ])
        self.tornadoapp.listen(settings_master.listen_port,
                               settings_master.listen_ip)
        tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    docker_watcher = DockerWatcherMaster()
    docker_watcher.run()
