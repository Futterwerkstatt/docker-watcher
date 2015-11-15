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
            logging.warning('pod ' + pod + ' running on ' + slave + ' id: ' + req.text)
        return req.text.encode('ascii')

    def run_pods(self):
        logging.warning('run_pods')
        pods = etcd_client.ls('pods/')
        logging.warning('pods: ' + str(pods))
        slaves = etcd_client.ls('slaves/')
        for pod in pods:
            logging.warning('running pod ' + pod)
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
        pods = etcd_client.ls('pods/')
        slaves = etcd_client.ls('slaves/')
        slaves_containers = []  # all running containers on all slaves
        pods_containers = []  # all pods containers

        for slave in slaves:  # get all running containers
            url = 'http://' + slave + '/get_containers'
            slave_containers = yaml.safe_load(requests.get(url).text)
            for container in slave_containers:
                slaves_containers.append(container)

        for pod in pods:  # get all pods containers
            pod_containers = yaml.safe_load(etcd_client.get('pods/' + pod))['containers']
            for d in pod_containers:  # loop through slave running containers
                pods_containers.append({'pod': pod, 'slave': d['slave'], 'id': d['id']})

        logging.warning('slaves_containers: ' + str(len(slaves_containers)))
        logging.warning('pods_containers: ' + str(len(pods_containers)))

        for pod_container in pods_containers:  # remove not running containers from pod_cfg
            container_running = False
            for slave_container in slaves_containers:
                #logging.warning('pod_container id: ' + str(pod_container['id']))
                #logging.warning('slave_container id: ' + str(slave_container['Id']))
                #logging.warning(pod_container['id'].encode('ascii') == slave_container['Id'])
                #logging.warning(type(slave_container['Id']))
                if pod_container['id'] == slave_container['Id']:
                    container_running = True
                    break

            if not container_running:
                pod_cfg = yaml.safe_load(etcd_client.get('pods/' + pod))
                pod_cfg['containers'].remove({'id': pod_container['id'], 'slave': pod_container['slave']})
                etcd_client.set('pods/' + pod, yaml.safe_dump(pod_cfg))
                slave_cfg = yaml.safe_load(etcd_client.get('slaves/' + pod_container['slave']))
                slave_cfg['used_cpus'] = int(slave_cfg['used_cpus']) - int(pod_cfg['cpus'])
                slave_cfg['used_memory'] = int(slave_cfg['used_memory']) - int(pod_cfg['memory'])
                slave_cfg['used_disk'] = int(slave_cfg['used_disk']) - int(pod_cfg['disk'])
                etcd_client.set('slaves/' + pod_container['slave'], yaml.safe_dump(slave_cfg))
                logging.warning('pod ' + pod + ' container ' + pod_container['id'].encode('ascii') +
                                ' not running, scheduling to run')
        logging.warning('check_pods finished')

    def run(self):
        while True:
            etcd_client.lock()
            self.run_pods()
            etcd_client.unlock()
            time.sleep(settings_watcher.sleep)
            etcd_client.lock()
            self.check_pods()
            etcd_client.unlock()
            logging.warning('sleeping for ' + str(settings_watcher.sleep) + ' seconds')
            time.sleep(settings_watcher.sleep)


if __name__ == '__main__':
    try:
        logging.warning('starting watcher')
        docker_watcher = DockerWatcher()
        docker_watcher.run()
    except Exception, e:
        logging.error(e, exc_info=True)
        exit(1)
