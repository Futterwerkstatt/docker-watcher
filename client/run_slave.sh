#!/usr/bin/env bash
SRV=$1
ssh root@$SRV service docker-watcher-slave stop
rsync -a ../../docker-watcher root@$SRV:/opt/
scp ../slave/docker-watcher-slave.conf root@$SRV:/etc/init/
ssh root@$SRV service docker-watcher-slave start