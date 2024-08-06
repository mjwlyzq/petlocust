from libs.base import PerformanceTest
from locust import HttpUser, constant_pacing, FastHttpUser
from clients.together import TogetherClient
from libs.logger import log
from libs.myRedis import rm_locust

PerformanceTest.synchronizing = False  # 是否开启集合点
PerformanceTest.defaultClient = TogetherClient
deleteKey = ['joinRoom', 'enterRoom', 'createRoomUser', 'roomUser', 'roomIdList']
for i in deleteKey:
    log.info(f'删除redis：{i}')
    rm_locust(i)


class WebsiteUser(HttpUser):
    """一起练"""
    host = ''
    tasks = [PerformanceTest]
    wait_time = constant_pacing(7 * 24 * 3600)  # 一个userX秒发一次,间隔X秒后再发
    # locust -f task_goddess.py --web-host=10.1.20.103 --headless --reset-stats -u 1 -r 11 -t 10 --csv=result --logfile=result.log --master
    # locust -f task_goddess.py --web-host=10.1.20.103 --reset-stats --master
    # locust -f task_goddess.py --master-host=10.1.20.103  --worker
