#!/usr/bin/env python
import settings_watcher
import requests
import sys
import os
import yaml
import ipdb

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from common import EtcdClient
import time
import logging

logging.basicConfig(filename=settings_watcher.log, level=30,
                    format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', )
ch = logging.StreamHandler(sys.stdout)

etcd_client = EtcdClient.EtcdClient(settings_watcher.etcd_host, settings_watcher.etcd_port,
                                    settings_watcher.etcd_timeout)


class DockerWatcher:
    def get_pods_running_on_slave(self, slavename):
        url = 'http://' + slavename + '/get_pods'
        req = requests.get(url)
        return req.text

    def run_pod_on_slave(self, pod, slave):
        url = 'http://' + slave + '/run_pod'
        data = etcd_client.get('pods/' + pod)
        req = requests.post(url, data=data)
        if req.status_code == 500:
            logging.warning('pod ' + pod + ' run on ' + slave + ' failed: ' + req.text)
            return 0
        else:
            logging.warning('pod ' + pod + ' runned on ' + slave + ' id: ' + req.text)
        return req.text

    def run_pods(self):
        logging.warning('run_pods')
        pods = etcd_client.ls('pods/')
        slaves = etcd_client.ls('slaves/')
        for pod in pods:
            logging.warning('checking pod ' + pod)
            pod_config = yaml.safe_load(etcd_client.get('pods/' + pod))
            running_containers = pod_config['containers']
            if pod_config['enabled'] == 1:
                instances = pod_config['instances']
                if len(running_containers) < instances:
                    containers_to_run = instances - len(running_containers)
                    for slave in slaves:
                        if containers_to_run == 0:
                            break
                        slave_cfg = yaml.safe_load(etcd_client.get('slaves/' + slave))
                        if not any(d.get('slave', None) == slave for d in running_containers):
                            slave_free_cpus = int(slave_cfg['total_cpus']) - int(slave_cfg['used_cpus'])
                            slave_free_memory = int(slave_cfg['total_memory']) - int(slave_cfg['used_memory'])
                            slave_free_disk = int(slave_cfg['total_disk']) - int(slave_cfg['used_disk'])
                            pod_required_cpus = pod_config['cpus']
                            pod_required_memory = pod_config['memory']
                            pod_required_disk = pod_config['disk']
                            if pod_required_cpus <= slave_free_cpus and pod_required_memory <= slave_free_memory \
                                    and pod_required_disk <= slave_free_disk:
                                container_id = DockerWatcher.run_pod_on_slave(self, pod, slave)
                                slave_cfg['used_cpus'] += pod_required_cpus
                                slave_cfg['used_memory'] += pod_required_memory
                                slave_cfg['used_disk'] += pod_required_disk
                                etcd_client.set('slaves/' + slave, yaml.safe_dump(slave_cfg))
                                containers_to_run -= 1
                                running_containers.append({'slave': slave, 'id': container_id})
                                logging.debug('run pod ' + pod + ' on ' + slave + ' container ' + container_id)
                        if containers_to_run == 0:
                            logging.warning('all containers of pod ' + pod + ' running')
            pod_config['containers'] = running_containers
            etcd_client.set('pods/' + pod, pod_config)
        logging.warning('run_pods finished')


    def check_pods(self):
        logging.warning('check_pods')
        slaves_list = etcd_client.ls('slaves/')
        pods_list = etcd_client.ls('pods/')
        current_running_pods_list = []
        for pod in pods_list:
            if pod['enabled'] == 1:
                current_running_pods_list.append(pod)

        # TODO
        # for slave in slaves_list:
        #    current_running_pods_list.append(self.get_pods_running_on_slave(slave))

        # for q in queue:
        #    for slave, pod in q.iteritems():
        #        url = 'http://' + slave + '/run_pod'
        #        data = etcd_client.get('pods/' + pod)
        #        req = requests.post(url, data=data)
        #        if req.status_code == 200:
        #            logging.warning('run pod ' + pod + ' on slave ' + slave + ' id: ' + req.text)
        #            queue.remove({slave: pod})
        #        else:
        #            logging.warning('failed to run pod ' + pod + 'on slave ' + slave)
        # etcd_client.set('queue', queue)

    def run(self):
        while True:
            etcd_client.lock()
            self.run_pods()
            self.check_pods()
            etcd_client.unlock()
            logging.warning('sleeping for ' + str(settings_watcher.sleep) + ' seconds')
            time.sleep(settings_watcher.sleep)


if __name__ == '__main__':
    logging.warning('starting watcher')
    docker_watcher = DockerWatcher()
    docker_watcher.run()
