#!/usr/bin/env python
import settings_watcher
import requests
import sys
import os
import yaml

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
        running = yaml.safe_load(etcd_client.get('running'))
        queue = yaml.safe_load(etcd_client.get('queue'))
        for pod in queue:
            queue = yaml.safe_load(etcd_client.get('queue'))
            slaves = etcd_client.ls('slaves/')
            suitable_slaves = []
            pod_config = yaml.safe_load(etcd_client.get('pods/' + pod))
            required_cpus = int(pod_config['cpus'])
            required_disk = int(pod_config['disk'])
            required_memory = int(pod_config['memory'])
            required_instances = int(pod_config['instances'])
            for slave in slaves:
                slave_config = yaml.safe_load(etcd_client.get('slaves/' + slave))
                slave_free_cpus = int(slave_config['total_cpus']) - int(slave_config['used_cpus'])
                slave_free_memory = int(slave_config['total_memory']) - int(slave_config['used_memory'])
                slave_free_disk = int(slave_config['total_disk']) - int(slave_config['used_memory'])
                if slave_free_cpus >= required_cpus and slave_free_memory >= required_memory \
                        and slave_free_disk >= required_disk:
                    suitable_slaves.append(slave)
            if required_instances > len(suitable_slaves):
                logging.warning("don't have required resources to run pod " + pod)
                return 0
            used_slaves = []
            for slave in suitable_slaves:
                task_id = self.run_pod_on_slave(pod, slave)
                logging.warning('run ' + pod + ' on ' + slave + ' id: ' + task_id)
                running.append({'pod': pod, 'slave': slave, 'id': run})
                slave_config = yaml.safe_load(etcd_client.get('slaves/' + slave))
                slave_config['used_cpus'] += required_cpus
                slave_config['used_memory'] += required_memory
                slave_config['used_disk'] += required_disk
                etcd_client.set('slaves/' + slave, yaml.safe_dump(slave_config))
                used_slaves.append(slave)
            if required_instances > used_slaves:
                logging.warning('unable to run required instances of pod ' + pod + ', will try next time')
            else:
                queue.remove(pod)
            etcd_client.set('queue', queue)
        etcd_client.set('running', yaml.safe_dump(running))
        return 0

    def check_pods(self):
        logging.warning('check_pods')
        # slaves_list = etcd_client.ls('slaves/')
        # queue = yaml.safe_load(etcd_client.get('queue'))
        # pods_list = etcd_client.ls('pods/')
        # current_running_pods_list = []
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
            # self.check_pods()
            etcd_client.unlock()
            logging.warning('sleeping for ' + str(settings_watcher.sleep) + ' seconds')
            time.sleep(settings_watcher.sleep)


if __name__ == '__main__':
    logging.warning('starting watcher')
    docker_watcher = DockerWatcher()
    docker_watcher.run()
