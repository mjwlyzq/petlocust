import threading, queue
import time
import requests
from libs.timeUtil import TimeUtil
from libs.logger import log


class Spawn(threading.Thread):
    def __init__(self, ratio: int, times: int, q: queue.Queue):
        super(Spawn, self).__init__()
        self.ratio = ratio  # x/5s
        self.times = times
        self.queue = q

    def run(self) -> None:
        for _ in range(self.times):
            for _ in range(self.ratio):
                self.queue.put("OK")
            time.sleep(5)


class NACOS(object):
    def __init__(self, url):
        super(NACOS, self).__init__()
        self.url = url
        self.resp = {}
        self.lastUpdateTimestamp = 0
        self.lock = threading.Lock()
        self.queue1 = queue.Queue()
        self.queue2 = queue.Queue()
        self.queueThreadStarted = False
        self.queueInit()

    def get_config(self):
        resp = requests.session().get(self.url)
        self.resp = resp.json()
        self.lastUpdateTimestamp = TimeUtil.now()
        # flag = self.resp.get("all_locusts_spawned", False)
        # ratio = self.resp.get("spanwned", 20)
        # users_count = self.resp.get("users_count", 1000)
        # worker = self.resp.get("worker", 10)
        # if flag and not self.queueThreadStarted:
        #     self.queueThreadStarted = True
        #     Spawn(int(ratio / worker * 5), int(users_count / ratio * 1.1), self.queue1).start()
        return self.resp

    @property
    def config(self):
        if not self.resp:
            self.resp = self.get_config()
        elif TimeUtil.now() - self.lastUpdateTimestamp > 1 * 1000 and not self.lock.locked():
            if self.lock.acquire(timeout=0.1):
                self.resp = self.get_config()
                self.lock.release()
        return self.resp

    # def spawn(self, timeout: int = 300):
    #     self.queue1.get(timeout=timeout)

    def queueInit(self):
        self.get_config()
        for record in self.resp.get("trainingRecords", []):
            self.queue2.put(record)

    @property
    def trainingRecordId(self):
        return self.queue2.get(timeout=300)


if __name__ == "__main__":
    nacos = NACOS()
    print(nacos.config)
    for i in range(100):
        print(nacos.config)
        time.sleep(1)
