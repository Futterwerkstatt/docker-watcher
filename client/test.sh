#!/usr/bin/env bash
set -x
SRV=rusik-dev1.adfox.yandex-team.ru
ssh root@$SRV service docker-watcher-watcher stop
ssh root@$SRV service docker-watcher-master stop
ssh root@$SRV service docker-watcher-slave stop
ssh root@$SRV service docker-watcher-web stop
rsync -a ../../docker-watcher root@$SRV:/opt/
scp ../master/docker-watcher-master.conf root@$SRV:/etc/init/
scp ../watcher/docker-watcher-watcher.conf root@$SRV:/etc/init/
scp ../slave/docker-watcher-slave.conf root@$SRV:/etc/init/
scp ../web/docker-watcher-web.conf root@$SRV:/etc/init/
SRV=rusik-dev2.adfox.yandex-team.ru
ssh root@$SRV service docker-watcher-slave stop
ssh root@$SRV rm /opt/docker-watcher/slave/*.pyc
rsync -a ../../docker-watcher root@$SRV:/opt/
scp ../slave/docker-watcher-slave.conf root@$SRV:/etc/init/
ssh root@$SRV service docker-watcher-slave start
SRV=rusik-dev3.adfox.yandex-team.ru
ssh root@$SRV service docker-watcher-slave stop
ssh root@$SRV rm /opt/docker-watcher/slave/*.pyc
rsync -a ../../docker-watcher root@$SRV:/opt/
scp ../slave/docker-watcher-slave.conf root@$SRV:/etc/init/
ssh root@$SRV service docker-watcher-slave start
ssh root@rusik-dev1.adfox.yandex-team.ru << EOF
    set -x
    rm /opt/docker-watcher/watcher/*.pyc
    rm /opt/docker-watcher/master/*.pyc
    rm /opt/docker-watcher/slave/*.pyc
    rm /opt/docker-watcher/web/*.pyc
    cd /opt/docker-watcher/client
    service docker-watcher-master start
    service docker-watcher-slave start
    service docker-watcher-web start
    etcdctl rm /docker-watcher/pods/example
    etcdctl rm /docker-watcher/slaves/rusik-dev1.adfox.yandex-team.ru:8888
    etcdctl rm /docker-watcher/slaves/rusik-dev2.adfox.yandex-team.ru:8888
    etcdctl rm /docker-watcher/slaves/rusik-dev3.adfox.yandex-team.ru:8888

    ./client.py -s rusik-dev1.adfox.yandex-team.ru:7777 -a add_slave -l rusik-dev1.adfox.yandex-team.ru:8888
    ./client.py -s rusik-dev1.adfox.yandex-team.ru:7777 -a add_slave -l rusik-dev2.adfox.yandex-team.ru:8888
    ./client.py -s rusik-dev1.adfox.yandex-team.ru:7777 -a add_slave -l rusik-dev3.adfox.yandex-team.ru:8888
    ./client.py -s rusik-dev1.adfox.yandex-team.ru:7777 -a add_pod -p ./pods.yml
    ./client.py -s rusik-dev1.adfox.yandex-team.ru:7777 -a run_pod -r example
    service docker-watcher-watcher start
EOF