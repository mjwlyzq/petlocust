import random

from libs.logger import log
from libs.nacos import NACOS
from libs.public import LocustPublic


class QuickBurningClient(object):
    def __init__(self):
        super(QuickBurningClient, self).__init__()
        self.contentHost = 'http://stable-cp-content-nt.qa.fiture.com'
        self.recordingHost = 'http://stable-cp-recording-bff-nt.qa.fiture.com'
        self.iotHostApp = 'http://stable-bfs-app-nt.qa.fiture.com'
        self.aldebaranHost = 'http://stable.up-aldebaran.nt.qa.fiture.com'
        self.contentHostNew = 'http://content.qa.fiture.com'
        # self.cmsHost = 'http://cms-api.qa.fiture.com'
        self.userinfo = None
        self.taurus_headers = None
        self.virgo_headers = None
        self.accountId = None
        self.httpClient = None

    def prepare(self, client, userinfo):
        self.httpClient = client
        self.userinfo = userinfo
        self.taurus_headers = LocustPublic.taurus_headers(self.userinfo['taurus_headers'],
                                                          self.userinfo['authentication'])
        self.virgo_headers = LocustPublic.taurus_headers(userinfo['virgo_headers'], userinfo['authentication'])
        self.accountId = self.userinfo.get("authentication").get("accountId")

    def send_post(self, client, userinfo):
        self.prepare(client, userinfo)
        # self.like_submit()
        self.reserve_add()

    def like_submit(self):
        desc = f'(评论点赞)'
        payload = {"event": "LIKE", "likedUserId": 1337301673435369474, "commentId": 513506}
        url = f"{self.aldebaranHost}/comment/like/submit"
        log.info(f"评论点赞: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
        log.info(f"评论点赞：{resp}")

    def add_submit(self):
        desc = f'(评论)'
        payload = {"entityType": "COMMENT", "entityId": 513470, "comment": "测试服",
                   "items": [{"type": "TEXT", "text": f"测试服{random.randint(1, 9999)}"}],
                   "repliedAccountId": 1620990120842371073}
        url = f"{self.aldebaranHost}/comment/add"
        log.info(f"评论: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
        log.info(f"评论：{resp}")

    def reserve_add(self):
        desc = f'(预约)'
        payload = {"reserveBizId": "3433", "reserveBizType": "GROUP_FITNESS_CLASS"}
        url = f"{self.contentHostNew}/taurus/reserve/add"
        log.info(f"预约: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
        log.info(f"预约：{resp}")
