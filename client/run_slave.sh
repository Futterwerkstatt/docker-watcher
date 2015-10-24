#!/usr/bin/env bash
set -x
SRV=$1
ssh root@$SRV mkdir -p /opt/docker-watcher/slave
scp ../slave/slave.py root@$SRV:/opt/docker-watcher/slave
scp ../slave/settings_slave.py root@$SRV:/opt/docker-watcher/slave
scp ../slave/docker-watcher-slave.conf root@$SRV:/etc/init/
ssh root@$SRV service docker-watcher-slave restart