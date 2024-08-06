import traceback
from locust import HttpUser, task, TaskSet, events, constant_pacing
from gevent._semaphore import BoundedSemaphore
from libs.logger import log
from libs.public import TAAS, LocustPublic
from libs.exception import AccountInvalidException, ResponseException
from clients.realtime_rank import AiRealTimeRankClient
from libs.nacos import NACOS
from locust.runners import MasterRunner, WorkerRunner, LocalRunner

# ******************* Locust Set  Start*****************************
all_locusts_spawned = BoundedSemaphore()
all_locusts_spawned.acquire()


def on_hatch_complete(**kwargs):
    # 创建钩子方法
    all_locusts_spawned.release()


events.spawning_complete.add_listener(on_hatch_complete)
# ******************* Locust Set End *****************************

# ******************* Nacos Config ******************* #
log.set_info_level()
nacos = NACOS("http://nacos.qa.fiture.com/nacos/v1/cs/configs?dataId=locust&group=DEFAULT_GROUP")
LocustPublic.isGray = nacos.config.get("gray", False)

log.set_info_level()
log.debug("获取用户Sessions")
taasClient = TAAS()
realTimeRankClient = AiRealTimeRankClient()
userQueue = None


class PerformanceTest(TaskSet):
    u"""蝗虫类"""

    @events.init.add_listener
    def on_locust_init(environment, **Kwargs):
        if isinstance(environment.runner, MasterRunner):
            log.info("启动Master")
        elif isinstance(environment.runner, LocalRunner) or isinstance(environment.runner, WorkerRunner):
            log.info(f"启动Worker")
            global userQueue
            userQueue = taasClient.get_user_info(
                int(nacos.config.get("users_count", 1) / nacos.config.get("worker", 1) * 1.5),
                ignoreGrayAccount=True)
        else:
            log.warning("未知启动方式!退出～")
            exit(0)

    def on_start(self):
        self.require()
        # 每一次开始一个任务时执行
        if all_locusts_spawned.locked():
            all_locusts_spawned.wait()

    @task(1)
    def get_rank_data(self):
        global realTimeRankClient, taasClient
        for i in range(20):
            try:
                realTimeRankClient.send_post(self.client, self.userInfo, nacos)
            except AccountInvalidException as err:
                log.warning(err)
                self.require()
            except ResponseException as err:
                log.error(err)
                break
            except Exception as err:
                log.error(err)
                traceback.print_exc()
                break
            else:
                break

    def on_stop(self):
        self.release()

    def require(self):
        global userQueue
        assert userQueue.empty() is False, "获取可用用户失败，用户数不足"
        self.userInfo = userQueue.get()

    def release(self):
        global userQueue
        userQueue.put(self.userInfo)


class WebsiteUser(HttpUser):
    host = ''
    tasks = [PerformanceTest]
    # min_wait = 30000000  # 虚拟用户等待最小时间
    # max_wait = 60000000  # 虚拟用户等待最大时间
    wait_time = constant_pacing(1000)  # 一个user一秒发一次,间隔1000秒后再发
    # locust -f task_goddess.py --web-host=10.1.20.103 --headless --reset-stats -u 1 -r 11 -t 10 --csv=result --logfile=result.log --master
    # locust -f task_goddess.py --web-host=10.1.20.103 --reset-stats --master
    # locust -f task_goddess.py --master-host=10.1.20.103  --worker
