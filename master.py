#!/usr/bin/env python

import settings_master
import docker_watcher
import commands

class DockerWatcherMaster:
    def __init__(self, settings):
        self.settings=settings
        self.etcd_client = docker_watcher.EtcdClient(settings_master.etcd_host, settings_master.etcd_port)
        self.pods_map = docker_watcher.yaml_reader(settings_master.pods_file)

    def get_total_memory(self):
        output = commands.getoutput(free -m)
        return output

    #def run(self):

if __name__ == '__main__':
    docker_watcher = DockerWatcherMaster(settings_master)
    #docker_watcher.run()
