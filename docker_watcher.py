#!/usr/bin/env python

import etcd.client
import docker
import yaml





def yaml_reader(filename):
    with  open(filename) as f:
        datamap = yaml.safe_load(f)
    return datamap
