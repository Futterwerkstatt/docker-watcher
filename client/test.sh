#!/usr/bin/env bash
./run_master.sh rusik-dev1.adfox.yandex-team.ru > /dev/null
./run_slave.sh rusik-dev1.adfox.yandex-team.ru > /dev/null
./run_slave.sh rusik-dev2.adfox.yandex-team.ru > /dev/null
./run_slave.sh rusik-dev3.adfox.yandex-team.ru > /dev/null
