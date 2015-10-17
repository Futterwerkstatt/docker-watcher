#!/usr/bin/env python
import tornado.ioloop
import tornado.web
import tornado.httputil
import tornado.escape
import yaml

import psutil

import docker

import settings_slave


class DockerWatcherSlave:
    docker_client = docker.Client()

    def __init__(self):
        self.docker_client = docker.Client(base_url=settings_slave.docker_url)

    class InfoHandler(tornado.web.RequestHandler):
        def return_mb(self, value):
            return int(value / float(2 ** 20))

        def get(self):
            print '/info'
            info_dict = {}
            info_dict['total_cpus'] = psutil.cpu_count()
            info_dict['total_memory'] = self.return_mb(psutil.virtual_memory().total)
            info_dict['total_disk'] = self.return_mb(psutil.disk_usage('/').total)
            info_dict['total_network'] = psutil.net_if_stats()['eth0'].speed
            self.write(yaml.dump(info_dict))

    class StopHandler(tornado.web.RequestHandler):
        def get(self):
            print '/stop'
            self.write('stopping\n')
            tornado.ioloop.IOLoop.instance().stop()

    class RunHandler(tornado.web.RequestHandler):
        def post(self):
            print yaml.load(self.request.body)
            self.image =
            self.command =
            DockerWatcherSlave.docker_client.pull(image)
            self.container = DockerWatcherSlave.docker_client.create_container(
                image=self.image, command=self.command
            )
            #start_response = DockerWatcherSlave.docker_client \
            #    .start(container=self.container.get('Id'))
            #self.write(self.container.get('Id'))
            #self.set_status(200)

    class KillHandler(tornado.web.RequestHandler):
        def get(self, container_id):
            print 'killing ' + container_id
            kill_response = DockerWatcherSlave.docker_client.kill(
                container=container_id)
            self.write(kill_response)

    def run(self):
        self.tornadoapp = tornado.web.Application([
            (r'/info', DockerWatcherSlave.InfoHandler),
            (r'/stop', DockerWatcherSlave.StopHandler),
            (r'/run', DockerWatcherSlave.RunHandler),
            (r'/kill/(.*)', DockerWatcherSlave.KillHandler)
        ])
        self.tornadoapp.listen(settings_slave.listen_port,
                               settings_slave.listen_host)
        tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    print 'starting'
    docker_watcher = DockerWatcherSlave()
    docker_watcher.run()
    print 'exiting'
    exit(0)
