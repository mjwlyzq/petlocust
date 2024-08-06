from locust import HttpUser, constant_pacing

from clients.ton import TonClient
from libs.base import PerformanceTest

PerformanceTest.synchronizing = False
PerformanceTest.defaultClient = TonClient


class WebsiteUser(HttpUser):
    """0721速燃团课"""
    host = ''
    tasks = [PerformanceTest]
    wait_time = constant_pacing(7 * 24 * 3600)  # 一个userX秒发一次,间隔X秒后再发
    # locust -f task_digital.py --web-host=10.1.20.122 --headless --reset-stats -u 1 -r 11 -t 10 --csv=result --logfile=result.log --master
    # locust -f task_ton.py --web-host=192.168.1.8 --reset-stats --master
    # locust -f task_ton.py --web-host=192.168.1.8 --master
    # locust -f task_ton.py --master-host=192.168.1.8 --worker
