import etcd
import logging
import time
import random

class EtcdClient:
    def __init__(self, host='localhost', port=4001, timeout=30):
        self.timeout = timeout
        self.etcd_client = etcd.client.Client(host=host, port=port)

    def set(self, key, value):
        key_str = '/docker-watcher/' + key
        self.etcd_client.set(key_str, value)

    def get(self, key):
        key_str = '/docker-watcher/' + key
        logging.debug(key_str)
        value = self.etcd_client.get(key_str).value
        if isinstance(value, unicode):
            value = value.encode('ascii')
        return value

    def lock(self):
        lock_str = '/docker-watcher/lock'
        ts_now = int(time.time())
        ts_lock = int(self.etcd_client.get(lock_str).value)
        i = 0
        while i < self.timeout:
            if ts_now - ts_lock >= self.timeout:
                self.etcd_client.set(lock_str, str(ts_now))
                break
            time.sleep(random.randint(100, 1000) / 1000)
            i += 1
        return ts_now

    def unlock(self):
        lock_str = '/docker-watcher/lock'
        self.etcd_client.set(lock_str, '0')

    def ls(self, key):
        ret = []
        key_str = '/docker-watcher/' + key
        r = self.etcd_client.read(key_str, recursive=True, sorted=True)
        for d in r.children:
            ret.append(str(d.key).split('/')[-1])
        return ret
