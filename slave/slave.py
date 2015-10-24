#!/usr/bin/env python
import logging
import sys

import tornado.ioloop
import tornado.web
import tornado.httputil
import tornado.escape
import yaml
import psutil
import docker

import settings_slave

logging.basicConfig(filename=settings_slave.log, level=4)
ch = logging.StreamHandler(sys.stdout)
logging.debug('starting slave')


class DockerWatcherSlave:
    docker_client = docker.Client()

    def __init__(self):
        self.docker_client = docker.Client(base_url=settings_slave.docker_url)

    class InfoHandler(tornado.web.RequestHandler):
        def return_mb(self, value):
            return int(value / float(2 ** 20))

        def get(self):
            logging.debug('/info')
            info_dict = {}
            info_dict['total_cpus'] = psutil.cpu_count()
            info_dict['total_memory'] = self.return_mb(psutil.virtual_memory().total)
            info_dict['total_disk'] = self.return_mb(psutil.disk_usage('/').total)
            info_dict['total_network'] = psutil.net_if_stats()['eth0'].speed
            self.write(yaml.dump(info_dict))
            self.set_status(200)

    class StopHandler(tornado.web.RequestHandler):
        def get(self):
            logging.debug('/stop')
            self.write('stopping\n')
            self.set_status(200)
            tornado.ioloop.IOLoop.instance().stop()

    class RunHandler(tornado.web.RequestHandler):
        def post(self):
            logging.debug('/run')
            data = yaml.safe_dump(self.request.body)
            logging.debug(data)
            image = data['image']
            command = data['command']
            DockerWatcherSlave.docker_client.pull(image)
            self.container = DockerWatcherSlave.docker_client.create_container(
                image=image, command=command)
            # start_response = DockerWatcherSlave.docker_client \
            #    .start(container=self.container.get('Id'))
            # self.write(self.container.get('Id'))
            self.set_status(200)

    class KillHandler(tornado.web.RequestHandler):
        def get(self):
            logging.debug('/kill')
            container_id = self.request.body
            kill_response = DockerWatcherSlave.docker_client.kill(
                container=container_id)
            self.write(kill_response)

    def run(self):
        self.tornadoapp = tornado.web.Application([
            (r'/info', DockerWatcherSlave.InfoHandler),
            (r'/stop', DockerWatcherSlave.StopHandler),
            (r'/run_pod', DockerWatcherSlave.RunHandler),
            (r'/kill', DockerWatcherSlave.KillHandler)
        ])
        self.tornadoapp.listen(settings_slave.listen_port,
                               settings_slave.listen_host)
        tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    docker_watcher = DockerWatcherSlave()
    docker_watcher.run()
    exit(0)
