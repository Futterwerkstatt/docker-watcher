import etcd
import logging


class EtcdClient:
    def __init__(self, host='localhost', port=4001):
        self.etcd_client = etcd.client.Client(host=host, port=port)

    def set(self, key, value):
        key_str = '/docker-watcher/' + key
        self.etcd_client.set(key_str, value)

    def get(self, key):
        key_str = '/docker-watcher/' + key
        logging.debug(key_str)
        return self.etcd_client.get(key_str).value

    def lock(self, key):
        key_str = '/docker-watcher/' + key
        i = 0
        lock = self.etcd_client.get_lock(key_str, ttl=60)
        while (i < 60):
            lock.acquire()
            if (lock.is_locked()):
                logging.debug(key_str + ' locked')
                return lock
            else:
                time.sleep(1)
        logging.debug('unable to get lock on ' + key_str)
        return 1

    def unlock(self, lock):
        logging.debug('unlock ' + lock)
        lock.release()
        return 0

    def ls(self, key):
        ret = []
        key_str = '/docker-watcher/' + key
        r = self.etcd_client.read(key_str, recursive=True, sorted=True)
        for d in r.children:
            ret.append(str(d.key).split('/')[-1])
        return ret
