#!/usr/bin/env bash
SRV=$1
ssh root@$SRV service docker-watcher-master stop
rsync -a ../../docker-watcher root@$SRV:/opt/
scp ../master/docker-watcher-master.conf root@$SRV:/etc/init/
ssh root@$SRV service docker-watcher-master start