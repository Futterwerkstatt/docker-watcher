#!/usr/bin/env bash
set -x
SRV=$1
scp ../master/master.py root@$SRV:/opt/docker-watcher/master/
scp ../master/settings_master.py root@$SRV:/opt/docker-watcher/master/
scp ../master/docker-watcher-master.conf root@$SRV:/etc/init/
ssh root@$SRV service docker-watcher-master restart