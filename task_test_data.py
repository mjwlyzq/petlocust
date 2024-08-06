from libs.base import PerformanceTest
from locust import HttpUser, constant_pacing, FastHttpUser
from clients.test_data_client import QuickBurningClient

PerformanceTest.synchronizing = False
PerformanceTest.defaultClient = QuickBurningClient


class WebsiteUser(HttpUser):
    """0721速燃团课"""
    host = ''
    tasks = [PerformanceTest]
    wait_time = constant_pacing(7 * 24 * 3600)  # 一个userX秒发一次,间隔X秒后再发
    # locust -f task_digital.py --web-host=10.1.20.122 --headless --reset-stats -u 1 -r 11 -t 10 --csv=result --logfile=result.log --master
    # locust -f task_digital.py --web-host=10.1.20.122 --reset-stats --master
    # locust -f task_quick_burning.py --web-host=10.1.20.55 --master
    # locust -f task_quick_burning.py --master-host=10.1.20.55 --worker
