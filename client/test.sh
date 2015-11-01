#!/usr/bin/env bash
set -x
SRV=rusik-dev1.adfox.yandex-team.ru
ssh root@$SRV service docker-watcher-master stop
rsync -a ../../docker-watcher root@$SRV:/opt/
> /opt/docker-watcher/master/master.log
scp ../master/docker-watcher-master.conf root@$SRV:/etc/init/
ssh root@$SRV service docker-watcher-master start
ssh root@$SRV service docker-watcher-watcher stop
> /opt/docker-watcher/watcher/watcher.log
scp ../watcher/docker-watcher-watcher.conf root@$SRV:/etc/init/
ssh root@$SRV service docker-watcher-slave stop
> /opt/docker-watcher/slave/slave.log
scp ../slave/docker-watcher-slave.conf root@$SRV:/etc/init/
ssh root@$SRV service docker-watcher-slave start
ssh root@$SRV service docker-watcher-web stop
scp ../web/docker-watcher-web.conf root@$SRV:/etc/init/
> /opt/docker-watcher/web/web.log
ssh root@$SRV service docker-watcher-web start
SRV=rusik-dev2.adfox.yandex-team.ru
ssh root@$SRV service docker-watcher-slave stop
rsync -a ../../docker-watcher root@$SRV:/opt/
> /opt/docker-watcher/slave/slave.log
scp ../slave/docker-watcher-slave.conf root@$SRV:/etc/init/
ssh root@$SRV service docker-watcher-slave start
SRV=rusik-dev3.adfox.yandex-team.ru
ssh root@$SRV service docker-watcher-slave stop
rsync -a ../../docker-watcher root@$SRV:/opt/
> /opt/docker-watcher/slave/slave.log
scp ../slave/docker-watcher-slave.conf root@$SRV:/etc/init/
ssh root@$SRV service docker-watcher-slave start
ssh root@rusik-dev1.adfox.yandex-team.ru << EOF

    set -x
    etcdctl set /docker-watcher/queue '[]'
    etcdctl set /docker-watcher/running '[]'
    etcdctl rm /docker-watcher/pods/example
    etcdctl rm /docker-watcher/slaves/rusik-dev1.adfox.yandex-team.ru:8888
    etcdctl rm /docker-watcher/slaves/rusik-dev2.adfox.yandex-team.ru:8888
    etcdctl rm /docker-watcher/slaves/rusik-dev3.adfox.yandex-team.ru:8888
    cd /opt/docker-watcher/client
    ./client.py -s rusik-dev1.adfox.yandex-team.ru:7777 -a add_slave -l rusik-dev1.adfox.yandex-team.ru:8888
    ./client.py -s rusik-dev1.adfox.yandex-team.ru:7777 -a add_slave -l rusik-dev2.adfox.yandex-team.ru:8888
    ./client.py -s rusik-dev1.adfox.yandex-team.ru:7777 -a add_slave -l rusik-dev3.adfox.yandex-team.ru:8888
    ./client.py -s rusik-dev1.adfox.yandex-team.ru:7777 -a add_pod -p ./pods.yml
    ./client.py -s rusik-dev1.adfox.yandex-team.ru:7777 -a run_pod -r example
    service docker-watcher-watcher start
EOF