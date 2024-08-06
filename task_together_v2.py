from locust import HttpUser, constant_pacing

from clients.togetherv2 import TogetherClient
from libs.base import PerformanceTest

PerformanceTest.synchronizing = False  # 是否开启集合点
PerformanceTest.defaultClient = TogetherClient


class WebsiteUser(HttpUser):
    """一起练"""
    host = ''
    tasks = [PerformanceTest]
    wait_time = constant_pacing(7 * 24 * 3600)  # 一个userX秒发一次,间隔X秒后再发
    # locust -f task_together_v2.py --web-host=10.1.21.8 --headless --reset-stats -u 1 -r 11 -t 10 --csv=result --logfile=result.log --master
    # locust -f task_together_v2.py --web-host=10.1.21.8 --reset-stats --master
    # locust -f task_together_v2.py --master-host=10.1.21.8 --worker
