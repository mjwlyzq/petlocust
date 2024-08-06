from libs.base import PerformanceTest
from locust import HttpUser, constant_pacing
from clients.taurus_index import TaurusIndexClient

PerformanceTest.defaultClient = TaurusIndexClient()
PerformanceTest.synchronizing = True


class WebsiteUser(HttpUser):
    host = ''
    tasks = [PerformanceTest]
    wait_time = constant_pacing(10)  # 一个userX秒发一次,间隔X秒后再发
    # locust -f task_goddess.py --web-host=10.1.20.103 --headless --reset-stats -u 1 -r 11 -t 10 --csv=result --logfile=result.log --master
    # locust -f task_goddess.py --web-host=10.1.20.103 --reset-stats --master

    # locust -f task_goddess.py --master-host=10.1.20.103  --worker
