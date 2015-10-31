import settings_watcher
import requests
import yaml
from common import EtcdClient

import time
import logging

logging.basicConfig(filename=settings_master.log, level=4,
                    format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', )
ch = logging.StreamHandler(sys.stdout)
logging.debug('starting watcher')

etcd_client = EtcdClient.EtcdClient(settings_watcher.etcd_host, settings_watcher.etcd_port)


class DockerWatcher:
    def check_pods(self):
        logging.debug('check_slaves')
        slaves_list = etcd_client.ls('slaves/')
        pods_list = etcd_client.ls('pods/')
        for pod in pods_list:
            pod_config = yaml.safe_load(etcd_client.get('pods/' + pod))
            instances = pod_config['instances']

    def run(self):
        while True:
            check_pods(self)
            time.sleep(30)


if __name__ == '__main__':
    docker_watcher = DockerWatcher()
    docker_watcher.run()
