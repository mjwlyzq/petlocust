import json
import random
import time
import traceback
from locust import task, TaskSet, events
from locust.runners import MasterRunner, WorkerRunner, LocalRunner
from gevent._semaphore import BoundedSemaphore
from libs.logger import log
from libs.myRedis import rm_locust
from libs.public import TAAS, LocustPublic
from libs.exception import AccountInvalidException, ResponseException, IotException, FitureException, \
    RequestWasAbortedException
from libs.nacos import NACOS
from libs.ton_config import TonUser

# ******************* Nacos Config ******************* #
log.set_info_level()
# nacos = NACOS("http://nacos.qa.fiture.com/nacos/v1/cs/configs?dataId=locust&group=DEFAULT_GROUP")
# LocustPublic.isGray = nacos.config.get("carnival", {}).get("gray", False)

# ******************* Locust Set  Start ********************** #
all_locusts_spawned = BoundedSemaphore()
all_locusts_spawned.acquire()


def on_hatch_complete(**kwargs):
    # 创建钩子方法
    if all_locusts_spawned.locked():
        all_locusts_spawned.release()


events.spawning_complete.add_listener(on_hatch_complete)
# ******************* Locust Set End *****************************

taasClient = TonUser()


# userQueue = None


# ******************* 用户获取 10s内完成 *****************************

class PerformanceTest(TaskSet):
    u"""蝗虫类"""
    synchronizing = True
    defaultClient = None

    @events.init.add_listener
    def on_locust_init(environment, **Kwargs):
        if isinstance(environment.runner, MasterRunner):
            log.info("启动Master")
            # taasClient.init_user()
            log.info(f"用户队列初始化完毕")

        elif isinstance(environment.runner, LocalRunner) or isinstance(environment.runner, WorkerRunner):
            log.info(f"启动Worker")
        else:
            log.warning("未知启动方式!退出～")
            exit(0)

    def on_start(self):
        # 每一次开始一个任务时执行
        self.require()
        if self.synchronizing:
            # 设置集合点
            all_locusts_spawned.wait()

    # def on_stop(self):
    #     # 每一次结束一个任务时执行
    #     for k in self.deleteKey:
    #         rm_locust(k)

    @task(1)
    def do(self):
        if isinstance(self.defaultClient, type):
            self.defaultClient = self.defaultClient()
        assert self.defaultClient is not None, "未设置接口类"
        for i in range(20):
            try:
                log.info(f"客户端模拟: {self.userInfo}")
                self.defaultClient.send_post(self.client, self.userInfo)
            except RequestWasAbortedException as err:
                log.warning(err)
                # self.require()
            except IotException as err:
                log.warning(err)
                # 当发现IOT异常后，换个设备
                break
            except ResponseException as err:
                log.error(err)
                break
            except FitureException as err:
                log.error(err)
                break
            except Exception as err:
                log.error(err)
                traceback.print_exc()
                break
            else:
                break

    def require(self):
        self.userInfo = json.loads(taasClient.get_one_user())
        log.info(f'当前获得的用户：{self.userInfo}')
        assert self.userInfo, "队列里的用户为空"
