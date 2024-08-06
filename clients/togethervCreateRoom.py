import orjson as json
import random
import time

from libs.timeUtil import TimeUtil
from libs.public import LocustPublic
from libs.public import LocustMqttPublit
from libs.nacos import NACOS
from enum import Enum
from libs.exception import FitureException
from libs.logger import log
from libs.eventReport import EventReport


class timeNodeEnum(Enum):
    START_COUNTDOWN = "START_COUNTDOWN"  # 开场倒计时
    VERSE_PLAYING = "VERSE_PLAYING"  # 段落进行中
    VERSE_DATA_REPORT = "VERSE_DATA_REPORT"  # 段落数据上报
    VERSE_RESULT_CALC = "VERSE_RESULT_CALC"  # 段落成绩结算
    SHOW_VERSE_RANK = "SHOW_VERSE_RANK"  # 段落排名展示
    NEXT_VERSE_VOTING = "NEXT_VERSE_VOTING"  # 下一轮段落投票
    VOTE_RESULT_RECEIPT = "VOTE_RESULT_RECEIPT"  # 投票结果回执
    SHOW_GAME_OVER = "SHOW_GAME_OVER"  # 全场结束展示


class TogetherClient(object):
    def __init__(self):
        super(TogetherClient, self).__init__()
        self.contentHost = 'http://stable-cp-content-nt.qa.fiture.com'
        self.recordingHost = 'http://stable-cp-recording-bff-nt.qa.fiture.com'
        self.iotHost = 'http://stable.up-iot-device.nt.qa.fiture.com'
        self.timeout = 5 * 60
        self.httpClient = None
        self.userinfo = None

    def prepare(self, client, userinfo):
        self.httpClient = client
        self.userinfo = userinfo
        self.taurus_headers = LocustPublic.taurus_headers(self.userinfo['taurus_headers'],
                                                          self.userinfo['authentication'])
        self.virgo_headers = LocustPublic.taurus_headers(userinfo['virgo_headers'], userinfo['authentication'])
        self.accountId = self.userinfo.get("authentication").get("accountId")
        self.startTimestamp = TimeUtil.now()

    def send_post(self, client, userinfo, nacos: NACOS):
        self.prepare(client, userinfo)
