import json
import random
import time
from enum import Enum

from libs.eventReport import EventReport
from libs.exception import FitureException
from libs.logger import log
from libs.nacos import NACOS
from libs.public import LocustPublic, LocustMqttPublit
from libs.timeUtil import TimeUtil
from tools.create_room import CreateRoom


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
        self.httpClient = None
        self.mqttClient = None
        self.userinfo = None
        self.taurus_headers = None
        self.virgo_headers = None
        self.accountId = None
        self.startTimestamp = None
        self.roomId = None
        self.contentIds = None
        self.classroomCode = 'MULTIPLAYER'
        self.itemId = None
        self.contentId = None
        self.currentServerTime = None
        self.trainingRecordId = None
        self.expectEndTime = 0
        self.channelTopicToken = None
        self.pubTopics = []
        self.subBroadcastTopics = None
        self.subTopics = None
        self.targetId = None
        self.bizMark = None
        self.playingNodeRangeList = []
        self.verseIds = []
        self.startClassTimestamp = None
        self.sendReport = False
        self.bonePoint = False  # 是否上报骨骼点
        self.MULTIPLAYER_STAGE_SKELETON_REPORT = "MULTIPLAYER_STAGE_SKELETON_REPORT"
        self.MULTIPLAYER_REALTIME_DATA = "MULTIPLAYER_REALTIME_DATA"
        self.bonesDataV3 = "ǍˇȿˏƽɴȟɱƴȍȄȌ÷ơ˂ƄţƯɺƤƖƔȦƒǟȍǛƔǝſ00ǌ˅ɁˍƼɮȡɪƵȌȅȉęņˇƋőƣɹƣƖƒȦƒǠȌǛƔǜƀ00ǋˆɂˋƻɬȣɩƶȌȆȊĩĥˊƙŎƖɸƦƗƒȦƒǢȌǚƓǛƀ00ǉ˅ɀˉƽɭȤɫƹȋȆȇĽŒ˂ƧœƗɲƪƘƑȣƑǣȋǙƓǜƁ00ǊˉɀˋƽɭȥɩƺȉȈȆųŞ˃ƧŒƓɭƬƘƏȡƏǣȉǚƐǚƀ00ǈˋȿˍƽɯȦɬƺȉȋȅƘŠˁƸőƅɫƯƗƎȡƎǣȇǘƏǙſ00ǈˍɀˎƽɰȧɬƺȈȋȅƿŢ˂ǕřƇɦƱƗƍȡƎǣȇǘƎǙſ00ǉˌȿˍƽɯȧɫƻȈȋȅǒţʻǫśƊɣƳƘƍȠƎǥȇǙƏǙſ00ǉˌȿˍƽɯȨɫƻȈȌȅǙťʱǴśƘɢƷƙƍȠƎǦȇǚƎǚſ00ǊˌȿˍƽɱȪɬƼȇȌȅǉŦʚǴŢƔɡƽƚƍȠƏǨȆǛƎǛž00ǋˏȿːƽɱȬɮƼȇȍȅǖūʗǪŧƐɡƽƚƋȠƏǪȆǛƎǛż00ǋˏɀːƽɱȬɭƼȇȍȅǑƚʘǢŧƑɣƼƚƋȡƏǪȆǛƎǛż00ǋˏȿˏƽɱȫɭƼȇȍȅƸǁʵǛūơɣƻƛƋȢƏǪȆǝƎǜŽ00ǋːɀˑƽɱȪɮƺȇȎȆƥǝʿǓŮưɧƸƛƋȤƏǨȆǠƎǞż00Ǌˑɀ˒ƽɲȩɯƻȈȎȆźǡˁƼŰƲɯƴƛƌȥƏǧȆǢƎǡŻ00"

    def prepare(self, client, userinfo):
        self.httpClient = client
        self.userinfo = userinfo
        self.taurus_headers = LocustPublic.taurus_headers(self.userinfo['taurus_headers'],
                                                          self.userinfo['authentication'])
        self.virgo_headers = LocustPublic.taurus_headers(userinfo['virgo_headers'], userinfo['authentication'])
        self.accountId = self.userinfo.get("authentication").get("accountId")
        self.roomId = self.userinfo.get("roomId")
        self.bonePoint = self.userinfo.get("bonePoint")
        self.startTimestamp = TimeUtil.now()
        self.contentIds = CreateRoom().contentUniqueIdList

    def send_post(self, client, userinfo, nacos: NACOS):
        self.prepare(client, userinfo)
        self.mqttClient = LocustMqttPublit.getClientConnected(client, userinfo,
                                                              msgHandler=self.messageHandler,
                                                              closeCallback=self.iotCloseCallback,

                                                              extTopics=[])
        # time.sleep(random.randint(3, 8))
        self.join_room()
        # time.sleep(random.randint(3, 8))
        self.enter_room()
        # time.sleep(random.randint(3, 8))
        self.get_resource()
        # time.sleep(random.randint(3, 8))
        self.get_device_channel()
        # time.sleep(random.randint(3, 8))
        self.mqttClient.subscribe(*self.subBroadcastTopics, *self.subTopics)
        # time.sleep(random.randint(3, 8))
        self.startClassTimestamp = TimeUtil.now()

        while True:
            getNacos = nacos.config.get("together", {})
            isRunSub = getNacos.get("isRunSub", False)
            if isRunSub:
                # time.sleep(random.randint(3, 8))
                self.start_room()
                if self.sendReport:
                    log.info(f'开始上课：roomId:{self.roomId} accountId: {self.accountId}')
                    break
            else:
                time.sleep(1)
                log.info(f'等待开始上课。。。')

        while True:
            getNacos = nacos.config.get("together", {})
            exit = getNacos.get("exit", False)
            if self.bonePoint:
                self.send_nebones_data()
            # self.report_ranking_scores()
            if exit:
                log.info(f'退出上课：roomId:{self.roomId} accountId: {self.accountId}')
                break
            else:
                time.sleep(1)
                log.info(f'等待退出。。。')

        # time.sleep(random.randint(3, 8))
        self.exit_course()
        while True:
            getNacos = nacos.config.get("together", {})
            exit = getNacos.get("exitBonePoint", False)
            if exit:
                if self.bonePoint:
                    self.send_nebones_data()
                log.info(f'退出课程后，发送骨骼点：roomId:{self.roomId} accountId: {self.accountId}')
            else:
                break
        # time.sleep(random.randint(3, 8))
        self.exit_room()
        # time.sleep(random.randint(3, 8))
        self.taurus_result()
        # time.sleep(random.randint(3, 8))
        self.virgo_result()
        #
        # while True:
        #     getNacos = nacos.config.get("together", {})
        #     isExit = getNacos.get("room_list", False)
        #     # if self.bonePoint:
        #     #     self.send_nebones_data()
        #     # self.report_ranking_scores()
        #     if isExit:
        #         self.room_list()
        #         log.info(f'跳出上课环节。。。')
        #         break
        #     else:
        #         time.sleep(1)
        #         log.info(f'等待发送骨骼点和上报分数。。。')
        #
        # while True:
        #     getNacos = nacos.config.get("together", {})
        #     isExit = getNacos.get("room_detail", False)
        #     # if self.bonePoint:
        #     #     self.send_nebones_data()
        #     # self.report_ranking_scores()
        #     if isExit:
        #         self.room_detail()
        #         log.info(f'跳出上课环节。。。')
        #         break
        #     else:
        #         time.sleep(1)
        #         log.info(f'等待发送骨骼点和上报分数。。。')
            # else:
            #     log.info(f'上课中。。。')
        # time.sleep(random.randint(3, 8))
        # self.exit_room()
        # time.sleep(random.randint(3, 8))
        # self.taurus_result()
        # time.sleep(random.randint(3, 8))
        # self.virgo_result()
        # time.sleep(random.randint(3, 8))
        # self.room_list()
        # time.sleep(random.randint(3, 8))
        # self.room_detail()
        # time.sleep(random.randint(3, 8))
        # self.room_list_refresh()
        # time.sleep(random.randint(3, 8))
        # self.room_detail_refresh()

    def room_list(self):
        desc = '(Taurus房间列表)'
        payload = dict(pageSize=10, pageNumber=1)
        url = f"{self.recordingHost}/taurus/room/list"
        log.info(f"Taurus房间列表: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
        content = resp.get('content')
        log.debug(f"Taurus房间列表: msg={payload}, resp={resp}")

    def room_list_refresh(self):
        desc = '(Taurus房间列表刷新)'
        payload = dict(roomIds=[self.roomId])
        url = f"{self.recordingHost}/taurus/room/list-refresh"
        log.info(f"Taurus房间列表刷新: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
        content = resp.get('content')
        log.debug(f"Taurus房间列表刷新: msg={payload}, resp={resp}")

    def join_room(self):
        desc = '(Taurus加入约练房间)'
        payload = dict(roomId=self.roomId, deviceType="TAURUS")
        url = f"{self.recordingHost}/taurus/classroom/multi/user/join-room"
        log.info(f"join-room: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
        content = resp.get('content')
        roomPlayerChannelTopicDTO = content.get('roomPlayerChannelTopicDTO')
        self.bizMark = roomPlayerChannelTopicDTO.get('bizMark')
        try:
            self.targetId = content.get('bizIdentifiers')[0]
        except Exception:
            self.targetId = content.get('bizIdentifiers')
        log.debug(f"Taurus加入约练房间: msg={payload}, resp={resp}")

    def enter_room(self):
        desc = '(Taurus进入约练房间)'
        payload = dict(
            source="TAURUS",
            clientLocalTime=TimeUtil.now(),
            classroom=dict(
                roomId=self.roomId,
                code=self.classroomCode,
            ),
            deviceMode="DOMESTIC",
            deviceType="VIRGO",
            trainingType="COURSE_MODE"
        )
        url = f"{self.recordingHost}/virgo/classroom/multi/user/enter"
        log.info(f"enter-room: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        connect = resp.get('content')
        channelTopic = connect.get('channelTopic')
        self.channelTopicToken = channelTopic.get('playerToken')
        log.debug(f"Taurus进入约练房间: msg={payload}, resp={resp}")

    def room_detail_refresh(self):
        desc = '(Taurus房间详情自动轮询接口)'
        payload = dict(id=self.roomId)
        url = f"{self.recordingHost}/taurus/room/detail-refresh"
        log.info(f"Taurus房间列表刷新: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
        content = resp.get('content')
        log.debug(f"Taurus房间列表刷新: msg={payload}, resp={resp}")

    def room_detail(self):
        desc = '(Taurus房间详情接口)'
        payload = dict(id=self.roomId)
        url = f"{self.recordingHost}/taurus/room/detail"
        log.info(f"Taurus房间列表刷新: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
        content = resp.get('content')
        log.debug(f"Taurus房间列表刷新: msg={payload}, resp={resp}")

    def get_resource(self):
        desc = '(virgo获取资源)'
        payload = dict(roomId=self.roomId)
        url = f"{self.recordingHost}/virgo/classroom/resource/get"
        log.info(f"enter-room: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        content = resp.get("content")
        itemList = content.get('itemList')
        self.itemId = itemList[0].get('id')
        self.contentId = itemList[0].get('contentId')
        self.currentServerTime = itemList[0].get('currentServerTime')
        try:
            self.expectEndTime = int(itemList[0].get('expectEndTime', 20 * 60))
        except Exception:
            self.expectEndTime = int(self.currentServerTime) + int(itemList[0].get('duration', 20 * 60))
        log.debug(f"virgo获取课程信息：{resp}")

    def start_room(self):
        desc = '(virgo开始上课)'
        payload = dict(
            clientLocalTime=TimeUtil.now(),
            contentUniqueId=self.contentId,
            deviceMode="DOMESTIC",
            deviceType="VIRGO",
            roomId=self.roomId,
            roomItemId=self.itemId,
            source="TAURUS",
            trainingType="COURSE_MODE"
        )
        url = f"{self.recordingHost}/virgo/classroom/user/start"
        log.info(f"virgo开始上课: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        content = resp.get('content')
        self.trainingRecordId = content.get('trainingRecordId')
        self.sendReport = True
        log.debug(f"virgo开始上课：{resp}")

    def exit_course(self):
        desc = '(virgo退出课堂)'
        payload = {
            "effectiveness": "EFFECTIVE",
            "classroomType": "MULTIPLAYER",
            "exitType": "EXIT_SECTION",
            "trainingRecordId": self.trainingRecordId,
            "classroomCode": self.classroomCode,
            "endType": "FINISH",
            "clientLocalTime": TimeUtil.now(),
            "calories": 6,
            "roomId": self.roomId,
            "duration": 600000,
            "result": 10,
            "unit": "SCORE",
            "playDuration": 620000,
            "generalDevice": False,
            "effectiveDuration": 600000,
            "isRoomExit": True
        }
        url = f"{self.recordingHost}/virgo/classroom/multi/user/exit"
        log.info(f"virgo开始上课: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        log.debug(f"virgo开始上课：{resp}")

    def exit_room(self):
        desc = '(virgo退出房间)'
        payload = dict(roomId=self.roomId)
        url = f"{self.recordingHost}/virgo/classroom/multi/user/exit"
        log.info(f"virgo退出房间: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        log.debug(f"virgo退出房间：{resp}")

    def taurus_result(self):
        desc = '(taurus结果页)'
        payload = dict(roomId=self.roomId, queryScene="TRAINING_COMPLETE")
        url = f"{self.recordingHost}/taurus/room/training/results/info"
        log.info(f"taurus结果页: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        log.debug(f"taurus结果页：{resp}")

    def virgo_result(self):
        desc = '(virgo结果页)'
        payload = dict(roomId=self.roomId)
        url = f"{self.recordingHost}/virgo/room/training/results/info"
        log.info(f"virgo结果页: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        log.debug(f"virgo结果页：{resp}")

    def get_device_channel(self):
        desc = '(Virgo获取场景通道)'
        payload = dict(token=self.channelTopicToken)
        url = f'{self.iotHost}/ban/scene/get-device-channel'
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        content = resp.get("content")
        log.info(f"获取场景通道： {content}")
        # "high_stadium","low_stadium","standard_stadium"
        self.subBroadcastTopics = list(map(lambda c: c.get("subBroadcastTopic"), content))
        self.subTopics = list(map(lambda c: c.get("pubTopic"), content))
        log.info(f"订阅广播topic: {self.subBroadcastTopics}")
        log.info(f"订阅单播topic: {self.subTopics}")
        for channel in content:
            pubTopic = channel.get('pubTopic')
            self.pubTopics.append(pubTopic)
        log.info(f"广播topic列表: {self.pubTopics}")

    def send_nebones_data(self):
        """上报骨骼点"""
        log.info(f'上报骨骼点: pubTopics:{self.pubTopics}')
        if not self.pubTopics:
            raise Exception(f'没有找到topic：pubTopics:{self.pubTopics}')
        LocustMqttPublit.sendBonesDataV3(self.mqttClient, ext=dict(topic=self.pubTopics[0],
                                                                   accountId=self.accountId,
                                                                   contentId=self.contentId,
                                                                   roomId=self.roomId,
                                                                   bonesData=self.bonesDataV3,
                                                                   tag=self.MULTIPLAYER_STAGE_SKELETON_REPORT
                                                                   ))

    def messageHandler(self, msg: str, topic: str = "?", host: str = "?", port: int = 0):
        msgLength = len(msg)
        MSG = json.loads(msg)
        startProcessTimestamp = TimeUtil.now()
        if MSG.get("tag") == "MSG":
            payload = MSG.get("payload")
            payload = json.loads(payload)
            tag = payload.get("tag")
            if tag == "VERSE_REALTIME":
                EventReport.success(request_type="MQTT",
                                    name="RoundScore-ACK",
                                    response_time=TimeUtil.now() - startProcessTimestamp,
                                    response_length=msgLength)
            else:
                log.debug(f"通用消息: {MSG}")
        elif MSG.get("tag") == "INIT":
            log.debug(f"INIT消息: {MSG}")
        elif MSG.get("tag") == "STADIUM":
            self.lastIotMSGtimestamp = TimeUtil.now()
            payload = MSG.get("payload")
            payload = json.loads(payload)
            tag = payload.get("tag")
            if tag == "LAST_ROUND":
                log.debug(f"嘉年华消息: 最后一轮 {payload}")
                self.isLastRound = True
            elif tag == "NEXT_ROUND":
                log.debug(f"嘉年华消息: 下一轮 {payload}")
            elif tag == "FIXED_VERSE":
                log.debug(f"嘉年华消息: 下一轮固定段落数据 {payload}")
            elif tag == "NEXT_VOTE_OPTIONS":
                log.debug(f"嘉年华消息: 下一轮投票 {payload}")
                self.interactionId = payload.get("content").get("interactionId")
            elif tag == "VERSE_CALC_END":
                log.debug(f"嘉年华消息: 段落成绩结算完成 {payload}")
                self.verseEndReceived = True
                if self.isLastRound:
                    self.running = False
                    EventReport.success(request_type="MQTT",
                                        name=f"STADIUM:Last-{tag}",
                                        response_time=TimeUtil.now() - startProcessTimestamp,
                                        response_length=msgLength)
                else:
                    EventReport.success(request_type="MQTT",
                                        name=f"STADIUM:{tag}",
                                        response_time=TimeUtil.now() - startProcessTimestamp,
                                        response_length=msgLength)
            elif tag == "VOTE_END":
                log.debug(f"嘉年华消息: 投票结束 {payload}")
            elif tag == "VOTE_STATISTICS":
                log.debug(f"嘉年华消息: 投票数据 {payload}")
            elif tag == "ROUND_END":
                log.debug(f"嘉年华消息: 本轮结束 {payload}")
            elif tag == "RANK":
                log.debug(f"嘉年华消息: 实时排行榜消息 {payload}")
            elif tag == "ATTEND_USER":
                log.debug(f"嘉年华消息: 新用户加入 {payload}")
            elif tag == "TIME_LINE_CURRENT":
                log.debug(f"嘉年华消息: 时间轴信息 {payload}")
                content = payload.get("content")
                self.currentVerseId = content.get("verseId")
                if self.currentVerseId not in self.verseIds:
                    self.verseIds.append(self.currentVerseId)
                timeNode = content.get("timeNode")
                if timeNode and timeNode.get("timeNodeType") == "VERSE_PLAYING":
                    self.playingNodeRange = (timeNode.get("beginDate"), timeNode.get("endDate"))
                    if self.playingNodeRange not in self.playingNodeRangeList:
                        self.playingNodeRangeList.append(self.playingNodeRange)
                elif timeNode and timeNode.get("timeNodeType") == "NEXT_VERSE_VOTING":
                    self.nextVerseVotingRange = (timeNode.get("beginDate"), timeNode.get("endDate"))
                elif timeNode and timeNode.get("beginDate") == "SHOW_GAME_OVER":
                    self.running = False
            elif tag == "BARRAGE":
                log.debug(f"嘉年华消息: 弹幕 {payload}")
            elif tag == "CONTENT_END":
                log.debug(f"嘉年华消息: 全场结束 {payload}")
            elif tag == "COMPLETE_SHOW":
                log.debug(f"嘉年华消息: 全场结束展示 {payload}")
                self.running = False
            elif tag == "VERSE_REALTIME":
                log.debug(f"嘉年华消息: 段落实时分数 {payload}")
            elif tag == "STAGE_SELECTED_USERS":
                log.debug(f"嘉年华消息: 舞台抢占 {payload}")
                content = payload.get("content")
                self.stageSelectedUsers = list(map(lambda user: user.get("accountId"), content.get("userList")))
            elif tag == "STAGE_EXPORT_SKELETON":
                log.debug(f"嘉年华消息: 展示舞台骨骼点 {payload}")
            elif tag == "STAGE_REPORT_SKELETON":
                log.debug(f"嘉年华消息: 上报舞台骨骼点 {payload}")
            else:
                log.warning(f"嘉年华消息: 未知消息 {payload}")
                print(payload)

            if tag == "VERSE_REALTIME":
                # 单播
                EventReport.success(request_type="MQTT",
                                    name=f"STADIUM:{tag}",
                                    response_time=TimeUtil.now() - startProcessTimestamp,
                                    response_length=msgLength)
            elif tag == "VERSE_CALC_END":
                # 已经单独处理
                pass
            else:
                # 广播
                if tag == "BARRAGE":
                    label = payload.get("content").get("label")
                    EventReport.success(request_type="MQTT",
                                        name=f"STADIUM:{tag}_{label}",
                                        response_time=TimeUtil.now() - startProcessTimestamp,
                                        response_length=msgLength)
                else:
                    EventReport.success(request_type="MQTT",
                                        name=f"STADIUM:{tag}",
                                        response_time=TimeUtil.now() - startProcessTimestamp,
                                        response_length=msgLength)
        elif MSG.get("msgType") == "RESET":
            EventReport.success(request_type="MQTT",
                                name=f"RESET:{host.split('.')[0]}:{port}:{topic}",
                                response_time=TimeUtil.now() - startProcessTimestamp,
                                response_length=msgLength)
        elif MSG.get("msgType") == "MSG":
            EventReport.success(request_type="MQTT",
                                name=f"MSG:{host.split('.')[0]}:{port}:{topic}",
                                response_time=TimeUtil.now() - startProcessTimestamp,
                                response_length=msgLength)

        else:
            log.warning(f"未识别的消息类型: {MSG}")

    def iotCloseCallback(self):
        self.mqttClient.disconnect()
        self.iotWasBroken = True
