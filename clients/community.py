import os
import random

from libs.public import LocustPublic
from libs.timeUtil import TimeUtil

PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)


class CommunityClient(object):
    def __init__(self):
        super(CommunityClient, self).__init__()
        self.timeout = 5 * 60

    def page_get(self, client, userinfo):
        desc = '(社区tab页)'
        taurus_headers = LocustPublic.taurus_headers(userinfo['taurus_headers'], userinfo['authentication'])
        payload = {'page': 'SOCIAL_SQUARE'}
        url = 'http://stable.up-aldebaran.nt.qa.fiture.com/component/page/get'
        LocustPublic.post(client, url, taurus_headers, payload, desc)
