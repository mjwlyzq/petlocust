import json
import random
import time

from datas.bones import get_bones
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


class DigitalClient(object):
    def __init__(self):
        super(DigitalClient, self).__init__()
        self.contentHost = 'http://stable-cp-content-nt.qa.fiture.com'
        self.recordingHost = 'http://stable-cp-recording-bff-nt.qa.fiture.com'
        self.iotHost = 'http://stable.up-iot-device.nt.qa.fiture.com'
        self.cmsHost = 'http://cms-api.qa.fiture.com'
        self.timeout = 5 * 60
        self.contentUniqueId = None
        # self.broadcastStatus = None
        self.channelTopicToken = None
        self.groupClassSkeletonTopicToken = None  # 发送后台骨骼点topic兑换
        # self.classroomType = "BOILING_STADIUM"
        self.roomId = None
        self.trainingRecordId = None
        self.needReportScore = None
        self.currentVerseId = None
        self.verseIds = []
        # self.seriesId = None
        #
        self.totalScore = 0
        self.totalCalories = 0
        #
        self.subBroadcastTopics = []
        self.subTopics = []
        #
        self.httpClient = None
        self.mqttClient = None
        self.userinfo = dict()
        self.taurus_headers = None
        self.virgo_headers = None
        self.cms_headers = dict(
            Authorization='Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ5MG1SMjJXU1JHTGZYZnMyTkNsU2piWEFkWXFMaG1LeEFacHpUTnhXak04In0.eyJqdGkiOiI4YWMzY2ZlMy1kOTExLTQ2N2YtYmFkNS0wMmNjZTY0Y2E4OGMiLCJleHAiOjE2ODIwNDIwNTAsIm5iZiI6MCwiaWF0IjoxNjgxOTU1NjUwLCJpc3MiOiJodHRwczovL2tleWNsb2FrLmRldi5maXR1cmUuY29tL2F1dGgvcmVhbG1zL2ZpdHVyZSIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiI1NjRiMTQzYy00ODhlLTRlNDAtODgxOS1mNDE2ZTZiZDAzMGYiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJjbXMiLCJub25jZSI6IjlhMWNmNzRhLWNjNzMtNDBmNi05NzEzLTliYzE3NjFmZjFhNCIsImF1dGhfdGltZSI6MTY4MTk1NTYyMCwic2Vzc2lvbl9zdGF0ZSI6IjM1NjNlMjQ1LTI4ZTEtNGZmNS05MTExLWQ4ZDMyNGNmNGMyMSIsImFjciI6IjAiLCJhbGxvd2VkLW9yaWdpbnMiOlsiKiJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsIm5hbWUiOiLlv5flvLog5LqOIiwicHJlZmVycmVkX3VzZXJuYW1lIjoieXpxIiwiZ2l2ZW5fbmFtZSI6IuW_l-W8uiIsImZhbWlseV9uYW1lIjoi5LqOIiwiZW1haWwiOiJ5enFAZml0dXJlLmNvbSJ9.HGoaB2plLN-7kj3kglz0WHnb5tfheN_Z2lEcYoJcNnw724g7bYwnu_qd_fle6EFurZ0hnM00a4kisIDEz6mBlcvqG4zstMqXxcUpFhnOkh97y5Xh3wTcKlnROCtpy3QKtZJHb6LNriZ47ggXTRSM9v6Fy1xxr5VdjRHQsL6RuzL-X5DIvBq826NnnneLviDAr7KaQrSHYYJVGpuQL2Fprb7AHlWdMGzWg7zGlN_bwUVXe9bbvdtDeOCJGdn1y5qgAgkdp_lpciFSO6Wv1pVZf5MOXSXqavkKdNwxxjA3u9mzqqEyhfuIfCafIuXa6lkRrwZuj9WrvEtVxvk0MqtP_A')
        self.accountId = None
        #
        self.lastHBtimestamp = 0
        self.lastHBtimestampGroupCourses = 0
        self.lastHBtimestampBonesData = 0
        self.lastHBtimestampFitnessBonesData = 0
        self.lastHBtimestampBeat = 0
        self.lastScoretimestamp = 0
        # self.lastTLtimestamp = 0
        # self.lastBRtimestamp = 0
        # self.lastIotMSGtimestamp = 0
        self.iotWasBroken = False
        self.startTimestamp = 0
        # self.startCountdownRange = (0, 0)
        # self.playingNodeRange = (0, 0)
        # self.currentVerseRange = (0, 0)
        self.playingNodeRangeList = []
        self.currentVerseScores = 0
        self.currentVerseCalorie = 0
        # self.nextVerseVotingRange = (0, 0)
        # self.verseEndReceived = False
        self.stageSelectedUsers = []
        #
        # self.interactionId = None
        # self.voteDoneList = []
        # self.isLastRound = False
        # self.running = True
        # self.CONTENT_END = False
        #
        # self.voteDelay = random.randint(10000, 20000)
        # self.virgoResultDelay = random.randint(1, 2500)
        self.virgoExitDelay = random.randint(1, 3000)
        self.virgoEnter = random.randint(1, 10000)
        # self.bonesData = ["ƲɯŧɚǙɁźȪƇȽŠȾƧȎŨȔƻȗňȔƤǷŦǷŵȾƅǷƇǯ",
        #                   "ƲɯŧɚǙɁŻȪƇȽŠȾƦȎŨȔƻȗňȔƤǷŦǷŵȾƅǷƇǯ",
        #                   "ƱɰũɚǘɂźȪƆȾŠȾƧȎŧȕƺȗŇȔƣǷťǷŴȾƄǷƇǯ",
        #                   "ƱɯũɚǘɁźȪƆȾŠȾƧȎŧȕƺȗŇȔƤǷťǷŴȾƄǷƇǯ",
        #                   "ƱɯŲɘǘɁźȪƆȾŠȽƧȎŧȕƺȗŇȔƤǷťǷŴȾƄǷƇǯ",
        #                   "ƱɯŲɘǘɁźȪƆȾŠȽƧȎŧȕƺȗŇȔƤǷťǷŴȾƄǷƇǯ",
        #                   "ƱɯŢəǘɁŹȪƆȾŠȾƨȎŨȕƺȗŇȔƣǷťǷŴȾƄǷƇǯ",
        #                   "ƱɯŧəǘɁŹȪƆȾŠȾƧȎŨȕƺȗŇȔƣǷťǷŴȾƄǷƇǯ",
        #                   "ƱɯŨəǘɁŹȩƆȾŠȽƧȏŨȕƺȗŇȔƤǷťǷŴȾƄǷƇǯ",
        #                   "ƱɰŨɚǘɂŹȪƅȾşȾƦȏŧȕƹȗņȔƣǷŤǷųȾƄǷƇǯ",
        #                   "ƱɰŨəǘɂŸȪƅȾşȾƧȏŦȕƺȗņȔƣǷťǷųȾƄǷƇǯ",
        #                   "ƱɰŬəǘɂŸȪƅȾşȾƧȏŦȕƹȗņȔƣǷťǷųȾƄǷƆǯ"
        #                   ]
        # self.bonesDataV3 = ["ǍˇȿˏƽɴȟɱƴȍȄȌ÷ơ˂ƄţƯɺƤƖƔȦƒǟȍǛƔǝſ00ǌ˅ɁˍƼɮȡɪƵȌȅȉęņˇƋőƣɹƣƖƒȦƒǠȌǛƔǜƀ00ǋˆɂˋƻɬȣɩƶȌȆȊĩĥˊƙŎƖɸƦƗƒȦƒǢȌǚƓǛƀ00ǉ˅ɀˉƽɭȤɫƹȋȆȇĽŒ˂ƧœƗɲƪƘƑȣƑǣȋǙƓǜƁ00ǊˉɀˋƽɭȥɩƺȉȈȆųŞ˃ƧŒƓɭƬƘƏȡƏǣȉǚƐǚƀ00ǈˋȿˍƽɯȦɬƺȉȋȅƘŠˁƸőƅɫƯƗƎȡƎǣȇǘƏǙſ00ǈˍɀˎƽɰȧɬƺȈȋȅƿŢ˂ǕřƇɦƱƗƍȡƎǣȇǘƎǙſ00ǉˌȿˍƽɯȧɫƻȈȋȅǒţʻǫśƊɣƳƘƍȠƎǥȇǙƏǙſ00ǉˌȿˍƽɯȨɫƻȈȌȅǙťʱǴśƘɢƷƙƍȠƎǦȇǚƎǚſ00ǊˌȿˍƽɱȪɬƼȇȌȅǉŦʚǴŢƔɡƽƚƍȠƏǨȆǛƎǛž00ǋˏȿːƽɱȬɮƼȇȍȅǖūʗǪŧƐɡƽƚƋȠƏǪȆǛƎǛż00ǋˏɀːƽɱȬɭƼȇȍȅǑƚʘǢŧƑɣƼƚƋȡƏǪȆǛƎǛż00ǋˏȿˏƽɱȫɭƼȇȍȅƸǁʵǛūơɣƻƛƋȢƏǪȆǝƎǜŽ00ǋːɀˑƽɱȪɮƺȇȎȆƥǝʿǓŮưɧƸƛƋȤƏǨȆǠƎǞż00Ǌˑɀ˒ƽɲȩɯƻȈȎȆźǡˁƼŰƲɯƴƛƌȥƏǧȆǢƎǡŻ00"]
        self.bonesDataV3 = get_bones()
        self.bone = None
        self.isCreated = False
        self.GROUP_FITNESS_CLASS = "GROUP_FITNESS_CLASS"
        self.roomItemId = None
        self.courseType = None
        # self.lastStatus = None
        # self.lastTraining = None
        self.expectEndTime = None  # 最后一节课程退出时间，调用退出训练接口时机
        self.pubTopic = None
        self.pubTopics = []
        self.pubTopicsBackstage = []  # 后台pubTopices
        self.GROUP_FITNESS_CLASS_REALTIME_DATA_REPORT = 'GROUP_FITNESS_CLASS_REALTIME_DATA_REPORT'  # 团课实时数据上报消息tag
        self.isRunning = True  # 是否在上课
        self.roomStatus = None  # 房间状态
        self.GROUP_FITNESS_CLASS_SKELETON_REPORT = 'GROUP_FITNESS_CLASS_SKELETON_REPORT'  # 骨骼点上报tag
        self.isStartTraining = False
        self.isExitTraining = False
        self.expectStartTime = 0  # 房间开始时间
        self.MULTIPLAYER_ROOM_START = False  # 是否开始上课
        self.MULTIPLAYER_ROOM_END = False  # 房间结束
        self.startResource = False

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
        getNacos = nacos.config.get("Digital", {})
        self.contentUniqueId = getNacos.get("contentUniqueId", 0)
        self.roomId = getNacos.get("roomId", 0)
        self.mqttClient = LocustMqttPublit.getClientConnected(client, userinfo,
                                                              msgHandler=self.messageHandler,
                                                              closeCallback=self.iotCloseCallback,
                                                              extTopics=[])
        # 创建房间
        # self.createRoom()
        # 房间列表，查询房间是否为CREATE且类型为团课
        # 如果查询到团课，就返回
        # while True:
        #     self.room_list()
        #     if self.isCreated:
        #         break
        # time.sleep(self.virgoEnter / 1000)
        self.room_enter()
        self.getDeviceChannel()
        self.getDeviceChannelToGroupClassSkeleton()
        self.mqttClient.subscribe(*self.subBroadcastTopics, *self.subTopics)
        self.get_resource()

        while self.isRunning:
            lastRunningtimestamp = TimeUtil.now()
            self.sendHeartbeat()
            self.run_get_resource()
            self.bone = random.choice(self.bonesDataV3)
            if self.MULTIPLAYER_ROOM_START or self.roomStatus == 'STARTED':
                if not self.startResource:
                    self.get_resource()
                if not self.isStartTraining:
                    self.start_training()
                if self.courseType in ['COURSE', 'PK']:
                    self.send_one_bones_data_v2()
            log.info(f'获取到 roomStatus 状态：{self.roomStatus}')
            if self.roomStatus in ['CREATED', 'STARTED']:
                self.send_report_group_courses()
                self.send_fitness_bones_data_v3()
            if self.expectEndTime:
                if time.time() * 1000 >= int(self.expectEndTime):
                    if not self.isExitTraining:
                        self.exit_course()
            if self.MULTIPLAYER_ROOM_END or self.roomStatus == 'END':
                log.info(f'课堂结束，模拟团课退出')
                break
            # now = TimeUtil.now()
            # cost = now - lastRunningtimestamp
            # if cost < 500:
            #     time.sleep((500 - cost) / 1000)

    # step_1
    def createRoom(self):
        desc = '(Taurus创建房间)'
        payload = dict(classroomType=self.classroomType,
                       contentId=self.contentUniqueId)
        url = f"{self.recordingHost}/taurus/classroom/multi/create-room"
        log.info(f"create-room: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
        content = resp.get("content")
        self.roomId = content.get("roomId")
        log.debug(f"开始运动场: contentId: {self.contentUniqueId}")

    # step_2
    def room_list(self):
        desc = '(Taurus房间列表)'
        payload = dict(pageSize=10, pageNumber=1)
        url = f"{self.recordingHost}/taurus/room/list"
        log.info(f"Taurus房间列表: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
        content = resp.get('content')
        log.debug(f"Taurus房间列表: msg={payload}, resp={resp}")
        if content:
            self.isCreated = True

    # step_3
    def room_enter(self):
        desc = '(Virgo进入&加入房间)'
        payload = dict(
            trainingType="COURSE_MODE",
            deviceMode="DOMESTIC",
            clientLocalTime=TimeUtil.now(),
            source="VIRGO",
            classroom=dict(roomId=self.roomId,
                           code=self.GROUP_FITNESS_CLASS),
            deviceType="VIRGO"
        )
        url = f'{self.recordingHost}/virgo/classroom/multi/user/enter'
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        content = resp.get("content")
        self.channelTopicToken = content.get("channelTopic").get("playerToken")
        self.groupClassSkeletonTopicToken = content.get("groupClassSkeletonTopic").get("playerToken")

    # step_4
    def start_training(self):
        desc = '(开始跟练)'
        payload = dict(
            classroom=dict(
                type="GROUP_FITNESS_CLASS",
                roomId=self.roomId,
            ),
            trainingType="PLAN_MODE",
            contentUniqueId=self.contentUniqueId,
            clientLocalTime=TimeUtil.now(),
            deviceMode="DOMESTIC",
            deviceType="VIRGO",
            source="TAURUS",
            contentRelationship=dict(
                subjectId=50,
                fromSubject=False,
                plan=dict(),
                roomId=self.roomId,
                roomItemId=self.roomItemId,
            ),
            roomId=self.roomId,
            roomItemId=self.roomItemId
        )
        url = f'{self.recordingHost}/virgo/classroom/multi/user/start'
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        content = resp.get("content")
        log.info(f'开始跟练：{content}')
        self.trainingRecordId = content.get("trainingRecordId")
        self.isStartTraining = True

    # step_5
    def classroom_exit(self, ignoreError=True):
        time.sleep(self.virgoExitDelay / 1000)
        desc = '(Virgo退出课堂)'
        playDuration = 0
        for playingNodeRange in self.playingNodeRangeList:
            duration = playingNodeRange[1] - playingNodeRange[0]
            playDuration += duration
        payload = dict(
            roomId=str(self.roomId),
            classroomCode="GROUP_FITNESS_CLASS",
            trainingRecordId=str(self.trainingRecordId),
            isRoomExit=True,
            calories=36,
            duration=TimeUtil.now() - self.startTimestamp,
            effectiveDuration=playDuration,
            playDuration=playDuration,
            endType="EXIT",
            clientLocalTime=TimeUtil.now(),
            result=float(self.totalScore),
            unit="SCORE",
            effectiveness="EFFECTIVE",
            timeNodeType="VERSE_PLAYING",
            verse=dict(
                currentVerseId=self.currentVerseId,
                verseIds=self.verseIds
            ),
            heartRateChart=dict(
                chartType="HEART_RATE_CHART",
                points=list(dict(x=769, y=0.0))
            ),
            avgHeartRate=104,
            wearHrmEffectiveDuration=393000,
        )
        url = f'{self.recordingHost}/virgo/classroom/multi/user/exit'
        if ignoreError:
            try:
                LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
            except Exception as err:
                pass
        else:
            LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)

    # step_6
    def room_prepare(self):
        time.sleep(self.virgoExitDelay / 1000)
        desc = '(cms后台房间准备)'
        payload = dict(
            contentId=self.contentUniqueId,
            expectStartTime=TimeUtil.now() + 3.5 * 60 * 60 * 60
        )
        url = f'{self.cmsHost}/api/room/prepare'
        resp = LocustPublic.post(self.httpClient, url, self.cms_headers, payload, desc)
        content = resp.get("content")
        self.roomId = content.get('roomId')

    # step_7
    def room_create(self):
        time.sleep(self.virgoExitDelay / 1000)
        desc = '(cms后台房间创建)'
        payload = {"contentIds": [self.contentUniqueId], "name": "501一周两节课", "tags": ["PLAN_SERIALISED"],
                   "type": "PUBLIC",
                   "accountId": self.accountId, "classroomCode": "SINGLE_SERIALISED", "creatorRole": "USER",
                   "deviceMode": "DOMESTIC", "source": "TAURUS",
                   "transparentFields": {"userPlanId": "9645", "planType": "UGC", "planId": "4389",
                                         "items": "[{\"cid\":90662,\"scheduleId\":54179}]"}}
        url = f'{self.cmsHost}/room/create'
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        content = resp.get("content")
        self.roomId = content.get('roomId')

    # step_8
    def getDeviceChannel(self):
        desc = '(Virgo获取Channel场景通道)'
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
        if not self.pubTopics:
            raise FitureException("没有找到standard_stadium 通道！")

    # step_9
    def getDeviceChannelToGroupClassSkeleton(self):
        desc = '(Virgo获取groupClassSkeleton场景通道)'
        payload = dict(token=self.groupClassSkeletonTopicToken)
        url = f'{self.iotHost}/ban/scene/get-device-channel'
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        content = resp.get("content")
        log.info(f"获取后端骨骼点Topic通道： {content}")
        # "high_stadium","low_stadium","standard_stadium"
        # self.subBroadcastTopics += list(map(lambda c: c.get("subBroadcastTopic"), content))
        # self.subTopics += list(map(lambda c: c.get("pubTopic"), content))
        # log.info(f"订阅广播后台topic: {self.subBroadcastTopics}")
        # log.info(f"订阅单播后台topic: {self.subTopics}")
        for channel in content:
            pubTopic = channel.get('pubTopic')
            self.pubTopicsBackstage.append(pubTopic)
        log.info(f"广播后台topic列表: {self.pubTopicsBackstage}")
        if not self.pubTopicsBackstage:
            raise FitureException("没有找到后台standard_stadium 通道！")

    # step_10
    def report_group_courses(self):
        """上报团课实时数据"""
        log.info(f'上报团课实时数据: pubTopics:{self.pubTopics}')
        if not self.pubTopics:
            raise Exception(f'没有找到topic：pubTopics:{self.pubTopics}')
        heartRate = random.randint(70, 200)
        maxHeartRatePer = int(heartRate / 190 * 100)
        LocustMqttPublit.sendGroupCourses(self.mqttClient, ext=dict(
            topic=self.pubTopics[0],
            roomId=self.roomId,
            roomItemId=self.roomItemId,
            accountId=self.accountId,
            trainingRecordId=self.trainingRecordId,
            calories=random.randint(20, 99),
            duration=600000,
            effectiveDuration=600000,  # 房间item总有效运动时长(ms)
            playDuration=600000,
            score=random.randint(22, 99),  # 当前环节分数
            unit="SCORE",
            wearHrmEffectiveDuration=20,
            effectiveness="EFFECTIVE",
            tag=self.GROUP_FITNESS_CLASS_REALTIME_DATA_REPORT,
            totalCalories=13,  # room期间总卡路里(累积值)
            totalScore=self.totalScore,  # room期间总分数
            magic=random.randint(1, 9),  # 当前环节魔力值
            totalMagic=random.randint(9, 36),  # room期间总魔力值(累积值)
            heartRate=heartRate,  # 心率值
            maxHeartRatePer=maxHeartRatePer,  # 最大心率值百分比
            currentTimestamp=TimeUtil.now(),  # 当前上报时间戳(精确到毫秒)
        ))

    # step_11
    def get_resource(self):
        desc = '(virgo获取资源)'
        payload = dict(roomId=self.roomId)
        url = f"{self.recordingHost}/virgo/classroom/resource/get"
        log.info(f"enter-room: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        content = resp.get("content")
        log.info(f'virgo获取资源：{json.dumps(content)}')
        self.roomStatus = content.get('roomStatus')
        self.expectStartTime = content.get('expectStartTime')
        log.info(f"/resource/get: {self.roomStatus}")
        roomItemId = list(filter(lambda x: x.get('status') == 'STARTED', content.get('itemList')))
        if roomItemId:
            self.roomItemId = roomItemId[0].get('id')
            log.info(f'获取到roomItemId = {self.roomItemId}')
            self.courseType = roomItemId[0].get('type')
        courseAndPk = list(filter(lambda x: x.get('type') in ['COURSE', 'PK'], content.get('itemList')))
        log.info(f'获取到数据111：{json.dumps(courseAndPk)}')
        try:
            lastData = sorted(courseAndPk, key=lambda keys: keys['expectEndTime'], reverse=True)
            log.info(f'获取到 resource数据：{json.dumps(lastData)}')
            self.expectEndTime = lastData[0].get('expectEndTime') if lastData else None
        except Exception:
            pass
        log.info(f'获取到roomItemId = {self.roomItemId}')
        self.startResource = True
        if not self.roomStatus:
            FitureException(msg='resource接口获取房间状态失败')

    # step_12
    def run_get_resource(self):
        # 2s发一次
        now = TimeUtil.now()
        if now - self.lastHBtimestamp > 2 * 1000:
            self.get_resource()
            self.lastHBtimestamp = now

    # step_13
    def sendHeartbeat(self):
        # 5s发一次
        now = TimeUtil.now()
        if now - self.lastHBtimestampBeat > 5 * 1000:
            LocustMqttPublit.sendHeartbeat(self.mqttClient)
            self.lastHBtimestampBeat = now

    # step_14
    def send_report_group_courses(self):
        # 1s发一次
        now = TimeUtil.now()
        if now - self.lastHBtimestampGroupCourses > 1 * 1000:
            self.report_group_courses()
            self.lastHBtimestampGroupCourses = now

    # step_15
    def send_one_bones_data_v2(self):
        # 500ms发一次
        now = TimeUtil.now()
        if now - self.lastHBtimestampBonesData > 0.5 * 1000:
            self.sendOneBonesDataGroupClass()
            self.lastHBtimestampBonesData = now

    # step_16
    def send_fitness_bones_data_v3(self):
        # 500ms发一次
        now = TimeUtil.now()
        if now - self.lastHBtimestampFitnessBonesData > 0.5 * 1000:
            self.sendFitnessBonesDataGroupClass()
            self.lastHBtimestampFitnessBonesData = now

    # step_17
    def exit_course(self):
        desc = '(virgo退出课堂)'
        payload = {
            "isRoomExit": True,
            "roomId": self.roomId,
            "classroomCode": self.GROUP_FITNESS_CLASS,
            "trainingRecordId": self.trainingRecordId,
            "calories": 36,
            "duration": 555976,
            "effectiveDuration": 555976,
            "playDuration": 368000,
            "endType": "EXIT",
            "clientLocalTime": TimeUtil.now(),
            "unit": "SCORE",
            "result": 10.0,
            "effectiveness": "EFFECTIVE",
            "timeNodeType": "VERSE_PLAYING",
            "heartRateChart": {
                "chartType": "HEART_RATE_CHART",
                "points": [
                    dict(x=(int(time.time() / 1000 - self.expectStartTime / 1000)), y=float(random.randint(70, 220)))
                    for i in range(300)]
            },
            "avgHeartRate": 104,
            "wearHrmEffectiveDuration": 393000,
            "exitType": "ACTIVE_EXIT_ROOM"
        }
        url = f"{self.recordingHost}/virgo/classroom/multi/user/exit"
        log.info(f"virgo退出课堂: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        log.debug(f"virgo退出课堂：{resp}")
        self.isExitTraining = True

    # step_18
    def sendOneBonesDataGroupClass(self):
        """上报骨骼点"""
        log.info(f'上报骨骼点: pubTopics:{self.pubTopics}')
        if not self.pubTopics:
            raise Exception(f'没有找到topic：pubTopics:{self.pubTopics}')
        if int(self.accountId) in self.stageSelectedUsers:
            LocustMqttPublit.sendBonesDataGroupClass(self.mqttClient, ext=dict(topic=self.pubTopics[0],
                                                                               accountId=self.accountId,
                                                                               contentId=self.contentUniqueId,
                                                                               roomId=self.roomId,
                                                                               bonesData=self.bone,
                                                                               tag=self.GROUP_FITNESS_CLASS_SKELETON_REPORT
                                                                               ))

    # step_19
    def sendFitnessBonesDataGroupClass(self):
        """上报骨骼点到后台"""
        log.info(f'上报骨骼点到后台: pubTopics:{self.pubTopicsBackstage}')
        if not self.pubTopicsBackstage:
            raise Exception(f'没有找到后台topic：pubTopics:{self.pubTopicsBackstage}')
        # if int(self.accountId) in self.stageSelectedUsers:
        LocustMqttPublit.sendBonesFitnessDataGroupClass(self.mqttClient, ext=dict(topic=self.pubTopicsBackstage[0],
                                                                                  accountId=self.accountId,
                                                                                  contentId=self.contentUniqueId,
                                                                                  roomId=self.roomId,
                                                                                  bonesData=self.bone,
                                                                                  tag=self.GROUP_FITNESS_CLASS_SKELETON_REPORT
                                                                                  ))

    def messageHandler(self, msg: str, topic: str = "?", host: str = "?", port: int = 0):
        msgLength = len(msg)
        MSG = json.loads(msg)
        startProcessTimestamp = TimeUtil.now()
        # log.info(f'接收到的消息：{json.dumps(MSG)}')
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
                self.CONTENT_END = True
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
        elif MSG.get("tag") == "MULTIPLAYER":
            log.info(f'MULTIPLAYER数据：：{json.dumps(MSG)}')
            payload = json.loads(MSG.get('payload'))
            tag = payload.get("tag")
            content = payload.get("content")
            if tag == 'MULTIPLAYER_STAGE_EXPORT':
                log.info(f"团课后端选人:  {payload}")
                self.stageSelectedUsers = list(map(lambda user: user.get("accountId"), content.get("userList")))
            elif tag == 'MULTIPLAYER_ROOM_START':
                log.info(f"开始上课:  {payload}")
                self.MULTIPLAYER_ROOM_START = True
                self.roomItemId = content.get('roomItemId')
            elif tag == 'MULTIPLAYER_ROOM_END':
                log.info(f"房间结束:  {payload}")
                self.MULTIPLAYER_ROOM_END = True
        else:
            log.warning(f"未识别的消息类型: {MSG}")

    def iotCloseCallback(self):
        self.mqttClient.disconnect()
        self.iotWasBroken = True
