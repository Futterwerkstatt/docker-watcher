#!/usr/bin/env python

import settings_master
import docker_watcher
import multiprocessing
import commands

class DockerWatcherMaster:
    def __init__(self):
        self.etcd_client = docker_watcher.EtcdClient(settings_master.etcd_host, settings_master.etcd_port)
        self.pods_map = docker_watcher.yaml_reader(settings_master.pods_file)
        print self.etcd_client.get('slaves')

    def get_cpu_count(self):
        return multiprocessing.cpu_count()

    def get_total_memory(self):
        output = commands.getoutput(free -m)
        return output

    #def run(self):

if __name__ == '__main__':
    docker_watcher = DockerWatcherMaster()
    #docker_watcher.run()
