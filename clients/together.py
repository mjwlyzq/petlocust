import uuid

import orjson as json
import random
import time

from libs.myRedis import get_range_pop, get_range_count, push_locust, get_range
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
        self.contentUniqueId = None
        self.contentUniqueIdList = [91719, 91701]
        self.roomId = None
        self.classroomCode = 'MULTIPLAYER'
        self.classroomType = "PRIVATE"
        self.MULTIPLAYER_STAGE_SKELETON_EXPORT = "MULTIPLAYER_STAGE_SKELETON_EXPORT"
        self.MULTIPLAYER_REALTIME_RANK = "MULTIPLAYER_REALTIME_RANK"
        self.targetId = None
        self.bizMark = None
        # 加入房间返回房间信息
        self.roomPlayerChannelTopicDTOToken = None
        self.interactChannelTopicToken = None
        self.channelTopicToken = None
        # 订阅topic
        self.topic = 'biz-to-iot-multiplayer'
        # 课程信息列表
        self.itemList = []
        # 服务器时间
        self.currentServerTime = None
        self.currentItemId = None
        self.currentItemType = None
        self.currentItemStatus = None
        self.trainingRecordId = None
        self.startRoom = False
        # 创建房间的数量
        self.createRoomCount = 1
        # 每个房间加入的人数
        self.joinRoomCount = 1
        # 加入房间信息key
        self.joinRoomKey = 'joinRoom'
        # 进入房间的人数
        self.enterRoomCount = 1
        # 进入房间信息key
        self.enterRoomKey = 'enterRoom'
        self.createRoomKey = 'createRoomUser'
        self.createRoomKeyBack = 'createRoomUserBack'
        self.setRoomAndUser = 'roomUser'
        self.roomIdListKey = 'roomIdList'
        self.createRoomUser = None
        self.roomIdList = None
        self.isJoin = False
        self.enterRoom = False

        self.broadcastStatus = None
        self.needReportScore = None
        self.currentVerseId = None
        self.verseIds = []
        self.seriesId = None

        self.totalScore = 0
        self.totalCalories = 0

        self.subBroadcastTopics = []
        self.subTopics = []

        self.httpClient = None
        self.mqttClient = None
        self.userinfo = dict()
        self.taurus_headers = None
        self.virgo_headers = None
        self.accountId = None

        self.lastHBtimestamp = 0
        self.lastScoretimestamp = 0
        self.lastTLtimestamp = 0
        self.lastBRtimestamp = 0
        self.lastIotMSGtimestamp = 0
        self.iotWasBroken = False
        self.startTimestamp = 0
        self.startCountdownRange = (0, 0)
        self.playingNodeRange = (0, 0)
        self.currentVerseRange = (0, 0)
        self.playingNodeRangeList = []
        self.currentVerseScores = 0
        self.currentVerseCalorie = 0
        self.nextVerseVotingRange = (0, 0)
        self.verseEndReceived = False
        self.stageSelectedUsers = []

        self.interactionId = None
        self.voteDoneList = []
        self.isLastRound = False
        self.running = True

        self.voteDelay = random.randint(10000, 20000)
        self.virgoResultDelay = random.randint(1, 2500)
        self.virgoExitDelay = random.randint(1, 3000)
        self.prepareDelay = random.randint(1, 3)
        self.bonesData = ["ƲɯŧɚǙɁźȪƇȽŠȾƧȎŨȔƻȗňȔƤǷŦǷŵȾƅǷƇǯ",
                          "ƲɯŧɚǙɁŻȪƇȽŠȾƦȎŨȔƻȗňȔƤǷŦǷŵȾƅǷƇǯ",
                          "ƱɰũɚǘɂźȪƆȾŠȾƧȎŧȕƺȗŇȔƣǷťǷŴȾƄǷƇǯ",
                          "ƱɯũɚǘɁźȪƆȾŠȾƧȎŧȕƺȗŇȔƤǷťǷŴȾƄǷƇǯ",
                          "ƱɯŲɘǘɁźȪƆȾŠȽƧȎŧȕƺȗŇȔƤǷťǷŴȾƄǷƇǯ",
                          "ƱɯŲɘǘɁźȪƆȾŠȽƧȎŧȕƺȗŇȔƤǷťǷŴȾƄǷƇǯ",
                          "ƱɯŢəǘɁŹȪƆȾŠȾƨȎŨȕƺȗŇȔƣǷťǷŴȾƄǷƇǯ",
                          "ƱɯŧəǘɁŹȪƆȾŠȾƧȎŨȕƺȗŇȔƣǷťǷŴȾƄǷƇǯ",
                          "ƱɯŨəǘɁŹȩƆȾŠȽƧȏŨȕƺȗŇȔƤǷťǷŴȾƄǷƇǯ",
                          "ƱɰŨɚǘɂŹȪƅȾşȾƦȏŧȕƹȗņȔƣǷŤǷųȾƄǷƇǯ",
                          "ƱɰŨəǘɂŸȪƅȾşȾƧȏŦȕƺȗņȔƣǷťǷųȾƄǷƇǯ",
                          "ƱɰŬəǘɂŸȪƅȾşȾƧȏŦȕƹȗņȔƣǷťǷųȾƄǷƆǯ"
                          ]
        self.bonesDataV2 = [
            "Ȯ˳ǠˁɜʑǡɞǌɣžɝǾȞŻȞȮȬļȫȁǨťǪƦɡƵǩưǗ00Ȯ˳ǡˀɜʑȓɤǌɣžɝǾȞżȞȮȬļȫȁǨťǪƦɡƵǩưǗ00ȭ˳ǟˁɜʐȐɢǌɣŽɝǾȞżȞȮȫļȫȁǨťǪƦɡƵǩƱǗ00Ȯ˳ǟ˅ɜʑȗɬǌɣŽɝǾȞżȞȮȫļȫȁǨťǪƦɡƵǩƱǗ00ȭ˳ǟʽɜʑȏɣǌɣŽɝȀȞŻȝȮȫĽȫȁǨŦǪƥɡƵǩƲǗ00ȭ˳ǝʾɜʐȏɣǌɣŽɝȀȞŻȝȮȫĽȫȁǨŦǪƤɡƵǩƲǗ00ȭ˳ǝˀɜʐȫɩǌɣŽɝȀȞżȞȮȫĽȫȁǨťǪƤɡƵǩƱǗ00ȭ˳ǝˁɜʐǾɦǌɣŽɝȀȞżȞȮȫĽȫȁǨťǪƤɡƵǩƱǗ00ȭ˳ǜ˃ɜʐǮɥǌɣŽɜǾȞżȞȮȫĽȫȀǨťǪƤɡƵǩƱǗ00ȭ˴ǜ˄ɜʐǬɥǌɣŽɝǾȞżȞȮȫļȫȁǨťǪƤɡƴǩƱǗ00ȭ˴ǚ˅ɜʑǦɤǋɣŽɜȀȞżȞȭȫļȫȀǨťǪƤɡƳǩƲǗ00ȭ˴ǘ˅ɜʑȑɤǋɣžɜȀȞżȞȭȫļȫȀǨťǪƤɡƳǩƱǗ00Ȭ˴Ǘ˅ɛʑȖɤǋɣžɜȁȞŽȞȭȬļȫǾǨŦǪƣɡƳǩƱǗ00Ȭ˴Ǖ˃ɛʑǽɤǋɣżɜȁȞŽȞȭȬļȫǾǨŦǪƣɡƳǩƱǗ00Ȭ˴Ǖ˂ɛʑǼɤǋɣżɜȀȞŽȞȭȬļȫǾǨŦǪƣɡƳǩƱǗ00"
        ]

        self.bonesDataV3 = "ж˄ЮʼќɧЮəύɧΕɠұȝшȤњȘϳȖϮǭίǪεɢϊǪϔǤ00ж˅ЯʽѝɧЮəϊɧΔɟҰțчȤњȘϳȗϮǭίǪεɢϊǪϔǤ00з˅аʾѝɧвɚύɧΕɟҰȜчȤћȘϳȖϯǭΰǪηɢϋǪϕǤ00з˅бʾѝɧвɚόɧΕɟҰȜчȤћȘϳȖϯǭΰǪηɢϋǪϔǤ00б˂ЭʽіɦЪəϋɦΒɞҥȜуȤєȘϰȖϪǮάǪαɢφǪϐǤ00б˃ЭʽіɦЪəψɦΓɞҧȜфȤіȘϰȖϪǮάǪαɢφǪϐǤ00в˃ЯʾїɦШɘωɦΒɟҩȜцȤїȘϲȗϫǭΧǪβɢχǪϏǤ00г˃ЯʿјɦШəϋɦΓɞҪȜцȤїȘϲȗϫǭΨǪβɢψǪϐǤ00г˃аʿјɦШəύɦΔɟҪȜхȤјȘϲȗϫǭΨǪβɢψǪϐǤ00е˄аˀњɧЮəϐɦΗɟҭȜцȣљȘϲȗϭǭΧǪζɢωǪϓǤ00е˄аˀљɧЭəϏɦΗɟүțчȣњȘϳȗϮǭΩǪζɢϊǪϓǤ00ж˄бˁїɧЮəϐɥΗɟүȜшȣњȘϳȗϮǭΩǪζɢϊǪϔǤ00з˅ЬʾљɧЯɚϒɦΘɟҰȜшȣћȘϳȗϯǭΩǪθɢϋǪϔǤ00лˆбˀўɨгɚϔɧΜɠҶțьȤџșϷȗϲǬήǪλɢώǪϖǤ00лˆбˀўɨгəϔɧΜɠҶțыȤѠș϶ȗϲǬήǪλɢώǪϕǤ00"

    def prepare(self, client, userinfo):
        self.httpClient = client
        self.userinfo = userinfo
        self.taurus_headers = LocustPublic.taurus_headers(self.userinfo['taurus_headers'],
                                                          self.userinfo['authentication'])
        self.virgo_headers = LocustPublic.taurus_headers(userinfo['virgo_headers'], userinfo['authentication'])
        self.accountId = self.userinfo.get("authentication").get("accountId")

        if get_range_count(self.createRoomKey) < self.createRoomCount:
            push_locust(self.createRoomKey, dict(accountId=self.accountId, virgo_headers=self.virgo_headers,
                                                 taurus_headers=self.taurus_headers))
            push_locust(self.createRoomKeyBack, dict(accountId=self.accountId, virgo_headers=self.virgo_headers,
                                                     taurus_headers=self.taurus_headers))
        self.startTimestamp = TimeUtil.now()

    def send_post(self, client, userinfo, nacos: NACOS):
        # 初始化用户信息
        time.sleep(self.prepareDelay)
        self.prepare(client, userinfo)
        time.sleep(self.prepareDelay)
        while True:
            if get_range_count(self.createRoomKeyBack) >= self.createRoomCount:
                break
            else:
                log.info(f'创建房间的用户信息还没有准备好')
                time.sleep(2)
        # 获取创建room的用户信息
        self.createRoomUser = get_range_pop(self.createRoomKey)
        # 初始化mqtt信息
        self.mqttClient = LocustMqttPublit.getClientConnected(client, userinfo,
                                                              msgHandler=self.messageHandler,
                                                              closeCallback=self.iotCloseCallback,
                                                              extTopics=[])
        # 开始创建房间
        time.sleep(self.prepareDelay)
        self.createRoom()
        # 检查所有房间是否创建完毕
        while True:
            if get_range_count(self.roomIdListKey) >= self.createRoomCount:
                break
            else:
                log.info(f'房间还没有创建好，请稍后')
                time.sleep(2)
        # 获取roomId列表
        self.roomIdList = get_range(self.roomIdListKey)
        # 加入房间
        time.sleep(self.prepareDelay)
        if not self.isJoin:
            self.joinRoom()
        time.sleep(self.prepareDelay)
        # 进入房间
        if not self.enterRoom:
            self.roomEnter()
        time.sleep(self.prepareDelay)
        # 订阅topic
        self.mqttClient.subscribe(*self.topic)
        # 获取资源
        self.resourceGet()
        # 开始上课/骨骼点数据丢IOT/实时排行榜分数丢IOT
        for item in self.itemList:
            types = item.get('type')
            if types == 'COURSE':
                while True:
                    self.classroomStart(item)
                    if self.startRoom:
                        break
                    else:
                        time.sleep(2)
            else:
                try:
                    expectEndTime = int(item.get('expectEndTime'))
                except Exception:
                    expectEndTime = int(self.currentServerTime) + int(item.get('duration'))
                while True:
                    self.sendOneBonesDataV2()
                    self.sendOneBonesDataV4()
                    if not self.iotWasBroken:
                        self.sendHeartbeat()
                    if expectEndTime - TimeUtil.now() <= 0:
                        log.info(f"当前休息环节结束: {item}，开始播放下节课")
                        break
                    time.sleep(1)
        if not self.iotWasBroken:
            self.mqttClient.disconnect()
        # virgo exit接口
        self.classroomExit(ignoreError=True)
        time.sleep(15 - self.virgoExitDelay / 1000)
        # virgo结果页
        self.virgoResult(ignoreError=True)
        time.sleep(15 - self.virgoResultDelay / 1000)
        # taurus v3结果页
        self.taurusResultB(ignoreError=True)
        log.info("客户端模拟结束")

    def sendHeartbeat(self):
        # 30s发一次
        now = TimeUtil.now()
        if now - self.lastHBtimestamp > 30 * 1000:
            LocustMqttPublit.sendHeartbeat(self.mqttClient)
            self.lastHBtimestamp = now

    def sendRoundScores(self, score):
        if self.playingNodeRange[0] < TimeUtil.now() < self.playingNodeRange[1]:
            score = random.randint(10, 20) if score == -1 else score
            calories = 5
            self.currentVerseScores += score
            self.currentVerseCalorie += calories
            playDuration = self.playingNodeRange[1] - self.playingNodeRange[0]
            duration = self.currentVerseRange[1] - self.currentVerseRange[0]
            effectiveDuration = int(playDuration * 0.9)
            LocustMqttPublit.sendRoundRealtimeScore(self.mqttClient, ext=dict(roomId=self.roomId, topic=self.pubTopic,
                                                                              trainingRecordId=self.trainingRecordId,
                                                                              verseId=self.currentVerseId,
                                                                              score=self.currentVerseScores,
                                                                              calories=self.currentVerseCalorie,
                                                                              accountId=self.accountId,
                                                                              playDuration=playDuration,
                                                                              effectiveDuration=effectiveDuration,
                                                                              duration=duration))
            self.lastScoretimestamp = TimeUtil.now()
            self.totalScore += score
            self.totalCalories += calories
        else:
            self.currentVerseCalorie = 0
            self.currentVerseCalorie = 0

    def createRoom(self):
        if not self.createRoomUser:
            log.info(f'约练房间已满，无需创建了')
            return
        if get_range_count(self.roomIdListKey) < self.createRoomCount:
            desc = '(Taurus创建约练房间)'
            self.taurus_headers = self.createRoomUser.get('taurus_headers')
            self.virgo_headers = self.createRoomUser.get('virgo_headers')
            self.accountId = self.createRoomUser.get('accountId')
            payload = dict(contentIds=self.contentUniqueIdList,
                           subject=dict(type="aim", name="瘦肚子", value="stomach"),
                           classroomCode=self.classroomCode,
                           name=f"性能测试房间-{random.randint(1, 9999)}",
                           type="PUBLIC"
                           )
            url = f"{self.recordingHost}/taurus/classroom/multi/create-room"
            log.info(f"create-room: {payload}")
            resp = LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
            content = resp.get("content")
            self.roomId = content.get("roomId")
            push_locust(self.roomIdListKey, self.roomId)
            self.joinRoom(self.roomId, self.taurus_headers)
            time.sleep(self.prepareDelay)
            # 进入房间
            self.roomEnter(self.roomId, self.virgo_headers)
            log.debug(f"创建约练房间: msg={payload}, resp={resp}")
        else:
            log.info(f'房间已满，无需创建')

    def roomDetail(self):
        desc = '(Taurus约练房间详情)'
        payload = dict(id=self.roomId)
        url = f"{self.recordingHost}/taurus/room/detail"
        log.info(f"room-detail: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
        content = resp.get("content")
        self.contentUniqueIdList = [i.get('contentCardDTO').get('contentId') for i in content.get("itemList")]
        log.debug(f"Taurus约练房间详情: contentUniqueIdList: {self.contentUniqueIdList}，roomId：{self.roomId}")

    def joinRoom(self, getRoomId=None, taurus_headers=None):
        desc = '(Taurus加入约练房间)'
        if getRoomId is not None:
            self.roomId = getRoomId
        else:
            for i in self.roomIdList:
                if get_range_count(self.joinRoomKey) >= self.joinRoomCount:
                    continue
                if self.roomId is None:
                    self.roomId = i
                    break
        if self.roomId is None:
            log.info(f'房间：{self.roomId} 已经加满')
            return
        if taurus_headers is None:
            taurus_headers = self.taurus_headers
        payload = dict(roomId=self.roomId, deviceType="TAURUS")
        url = f"{self.recordingHost}/taurus/classroom/multi/user/join-room"
        log.info(f"join-room: {payload}")
        resp = LocustPublic.post(self.httpClient, url, taurus_headers, payload, desc)
        content = resp.get("content")
        roomPlayerChannelTopicDTO = content.get('roomPlayerChannelTopicDTO')
        self.bizMark = roomPlayerChannelTopicDTO.get('bizMark')
        try:
            self.targetId = content.get('bizIdentifiers')[0]
        except Exception:
            self.targetId = content.get('bizIdentifiers')
        push_locust(self.roomId, dict(accountId=self.accountId))
        log.debug(f"Taurus加入约练房间: msg={payload}, resp={resp}")
        self.isJoin = True

    def roomEnter(self, getRoomId=None, virgo_headers=None):
        desc = '(Taurus进入约练房间)'
        if getRoomId is not None:
            self.roomId = getRoomId
        else:
            for i in self.roomIdList:
                if get_range_count(self.enterRoomKey) >= self.enterRoomCount:
                    continue
                if self.roomId is None:
                    self.roomId = i
                    break
        if self.roomId is None:
            log.info(f'房间：{self.roomId} 进入人数已经加满')
            return
        if virgo_headers is None:
            virgo_headers = self.virgo_headers
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
        resp = LocustPublic.post(self.httpClient, url, virgo_headers, payload, desc)
        content = resp.get("content")
        push_locust(self.enterRoomKey, dict(accountId=self.accountId))
        log.debug(f"Taurus进入约练房间: msg={payload}, resp={resp}")
        self.enterRoom = True

    def resourceGet(self):
        desc = '(virgo获取资源)'
        payload = dict(roomId=self.roomId)
        url = f"{self.recordingHost}/virgo/classroom/resource/get"
        log.info(f"enter-room: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        content = resp.get("content")
        self.itemList = content.get('itemList')
        self.currentServerTime = content.get('currentServerTime')
        log.info(f'itemList：{self.itemList}')
        log.debug(f"virgo获取课程信息：{self.itemList}")

    def classroomStart(self, item):
        desc = '(virgo开始上课)'
        payload = dict(
            clientLocalTime=TimeUtil.now(),
            contentUniqueId=item.get('contentId'),
            deviceMode="DOMESTIC",
            deviceType="VIRGO",
            roomId=item.get('roomId'),
            roomItemId=item.get('id'),
            source="TAURUS",
            trainingType="COURSE_MODE"
        )
        url = f"{self.recordingHost}/virgo/classroom/user/start"
        log.info(f"virgo开始上课: {payload}")
        resp = LocustPublic.post_ignore(self.httpClient, url, self.virgo_headers, payload, desc)
        if resp['status'] != 'SUCCESS':
            log.error(f"virgo开始上课失败: {resp}")
            return
        log.info(f'virgo: 开始上课：{resp}')
        self.startRoom = True
        try:
            expectEndTime = int(item.get('expectEndTime'))
        except Exception:
            expectEndTime = int(self.currentServerTime) + int(item.get('duration'))
        content = resp.get('content')
        self.trainingRecordId = content.get('trainingRecordId')
        log.info(f'开始上传骨骼点和排行榜：{item}')
        while True:
            self.sendOneBonesDataV2()
            self.sendOneBonesDataV4()
            if not self.iotWasBroken:
                self.sendHeartbeat()
            if expectEndTime - TimeUtil.now() <= 0:
                log.info(f"当前课程播放结束: {payload}，开始播放下个环节")
                return
            time.sleep(1)

    def getCourseInfo(self, ignoreError=True):
        desc = '(Virgo课程详情)'
        payload = dict(contentId=self.contentUniqueId)
        url = f'{self.contentHost}/virgo/content/detail'
        if ignoreError:
            try:
                resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
            except Exception as err:
                pass
            else:
                content = resp.get("content")
                contentInfo = content.get("contentInfo")
                contentType = contentInfo.get("contentType")
                status = contentInfo.get("status")
                assert status == "ONLINE", f"课程未上线: {status}"
                assert contentType == "STADIUM", f"课程类型不支持: {contentType}"
        else:
            resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
            content = resp.get("content")
            contentInfo = content.get("contentInfo")
            contentType = contentInfo.get("contentType")
            status = contentInfo.get("status")
            assert status == "ONLINE", f"课程未上线: {status}"
            assert contentType == "STADIUM", f"课程类型不支持: {contentType}"

    def reverve(self):
        desc = '(Taurus预约)'
        payload = dict(contentId=str(self.contentUniqueId))
        url = f"{self.contentHost}/taurus/content-booking/reserve"
        LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
        print(f"运动场预约: {self.userinfo.get('phone')}")

    def cancelReverve(self):
        desc = '(Taurus取消预约)'
        payload = dict(contentId=str(self.contentUniqueId))
        url = f"{self.contentHost}/taurus/content-booking/cancel-reserve"
        LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)

    def getRealTimeRankData(self):
        desc = '(Virgo获取实时排行榜数据)'
        payload = dict(contentId=int(self.contentUniqueId),
                       businessId=str(self.businessId),
                       classroomType=self.classroomType,
                       accountId=self.accountId)
        url = f'http://stable-cp-recording-bff-nt.qa.fiture.com/recording/rank/ai-realtime/get/data'
        LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)

    def classroomEnter(self):
        desc = '(Virgo进入课堂)'
        payload = dict(contentUniqueId=int(self.contentUniqueId),
                       trainingType="COURSE_MODE",
                       deviceMode="DOMESTIC",
                       clientLocalTime=TimeUtil.now(),
                       source="TAURUS",
                       classroom=dict(roomId=self.roomId,
                                      type=self.classroomType),
                       contentRelationship=dict()
                       )
        url = f'{self.recordingHost}/virgo/classroom/multi/user/enter'
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        content = resp.get("content")
        self.trainingRecordId = content.get("trainingRecordId")
        self.needReportScore = content.get("reportDetail").get("needReportScore")
        self.channelTopicToken = content.get("channelTopic").get("playerToken")
        self.currentVerseId = content.get("timingLineDetail").get("currentRound").get("verseId")
        if self.currentVerseId not in self.verseIds:
            self.verseIds.append(self.currentVerseId)

    def getDeviceChannel(self):
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
            bizIdentifier = channel.get("bizIdentifier")
            if bizIdentifier.endswith("high"):
                # self.bizIdentifier = channel.get("bizIdentifier")
                # self.bizMark = channel.get("bizMark")
                self.pubTopic = channel.get("pubTopic")
                log.info(f"发送Topic: {self.pubTopic}")
                return
        raise FitureException("没有找到standard_stadium 通道！")

    def getPlayerList(self, ignoreError=True):
        desc = '(Virgo获取沸腾运动场用户信息)'
        payload = dict(roomId=self.roomId)
        url = f'{self.recordingHost}/virgo/classroom/boiling-stadium/player/list'
        if ignoreError:
            try:
                LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
            except Exception as err:
                pass
        else:
            LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)

    def verseListByIds(self):
        desc = '(Virgo根据段落id批量拉取沸腾运动场段落数据)'
        payload = dict(verseIds=[self.currentVerseId])
        url = f'{self.contentHost}/virgo/verse/list-by-ids'
        LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)

    def getTimingLine(self):
        # MQTT中断的情况下(15s没有消息)，每三秒调用一次
        now = TimeUtil.now()
        if now - self.lastTLtimestamp > 3 * 1000 and (
                self.iotWasBroken or now - self.lastIotMSGtimestamp > 15 * 1000):
            desc = '(Virgo获取沸腾运动场的时间轴数据)'
            payload = dict(roomId=self.roomId, hasCurrentTimeScale=True)
            url = f'{self.recordingHost}/virgo/classroom/boiling-stadium/get-timing-line'
            resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
            self.lastTLtimestamp = now
            content = resp.get("content")
            if content:
                currentRound = content.get("currentRound")
                self.currentVerseId = currentRound.get("verseId")
                if self.currentVerseId not in self.verseIds:
                    self.verseIds.append(self.currentVerseId)
                timeNodes = currentRound.get("timeNodes")
                playingNodes = list(
                    filter(lambda node: node.get("timeNodeType") == timeNodeEnum.VERSE_PLAYING.value, timeNodes))
                if playingNodes:
                    self.playingNodeRange = (playingNodes[0].get("beginDate"), playingNodes[0].get("endDate"))
                    if self.playingNodeRange not in self.playingNodeRangeList:
                        self.playingNodeRangeList.append(self.playingNodeRange)
                voteNodes = list(
                    filter(lambda node: node.get("timeNodeType") == timeNodeEnum.NEXT_VERSE_VOTING.value, timeNodes))
                if voteNodes:
                    self.nextVerseVotingRange = (voteNodes[0].get("beginDate"), voteNodes[0].get("endDate"))
                timeNodesStart = timeNodes[0].get("beginDate")
                timeNodesEnd = timeNodes[-1].get("endDate")
                self.currentVerseRange = (timeNodesStart, timeNodesEnd)
                currentTimeScale = content.get("currentTimeScale")
                if currentTimeScale and currentTimeScale.get("timeNode") and currentTimeScale.get("timeNode").get(
                        "timeNodeType") == "SHOW_GAME_OVER":
                    # 发现课程以及结束
                    self.running = False
            else:
                self.running = False
                log.error("时间轴为空")

    def virgoVerseRankDataGet(self):
        desc = '(Virgo获取段落排行榜数据)'
        payload = dict(roomId=self.roomId, contentId=self.contentUniqueId,
                       verseId=self.currentVerseId)
        url = f'{self.recordingHost}/virgo/verse/rank/data/get'
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        content = resp.get("content")
        log.debug(f"段落排行榜数据: {content}")

    def virgoContentRankDataGet(self):
        desc = '(Virgo获取全场排行榜数据)'
        payload = dict(roomId=self.roomId, contentId=self.contentUniqueId)
        url = f'{self.recordingHost}/virgo/content/rank/data/get'
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        content = resp.get("content")
        log.debug(f"段落排行榜数据: {content}")

    def taurusVerseRankDataGet(self):
        desc = '(Taurus获取段落排行榜数据)'
        payload = dict(roomId=self.roomId, contentId=self.contentUniqueId,
                       verseId=self.currentVerseId)
        url = f'{self.recordingHost}/taurus/verse/rank/data/get'
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        content = resp.get("content")
        worldRanks = content.get("worldRank")
        # 获取所有6个用户排行
        worldRanksLiked = list(filter(lambda rank: rank.get("position", 99999) <= 1000, worldRanks))
        log.debug(f"段落排行榜数据: {content}")
        return worldRanksLiked

    def taurusContentRankDataGet(self, ignoreError=True):
        desc = '(Taurus获取全场排行榜数据)'
        payload = dict(roomId=self.roomId, contentId=self.contentUniqueId)
        url = f'{self.recordingHost}/taurus/content/rank/data/get'
        if ignoreError:
            try:
                resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
            except Exception as err:
                pass
            else:
                content = resp.get("content")
                log.debug(f"段落排行榜数据: {content}")
        else:
            resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
            content = resp.get("content")
            log.debug(f"段落排行榜数据: {content}")

    def taurusUpvoteVerse(self, trainingRecordId, verseId, likedUserId, ignoreError=True):
        desc = '(Taurus段落点赞)'
        payload = dict(
            seriesId=self.seriesId,
            trainingRecordId=trainingRecordId,
            verseId=verseId,
            contentId=self.contentUniqueId,
            likedUserId=likedUserId,
            event="LIKE")
        url = f'{self.recordingHost}/taurus/classroom/upvote/verse'
        if ignoreError:
            try:
                resp = LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
            except Exception as err:
                pass
        else:
            resp = LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
        log.debug(f"给用户: {likedUserId} 点赞! req:{payload} resp: {resp}")

    def attendInteraction(self, optionIndex: int = 1):
        if self.interactionId and (self.interactionId not in self.voteDoneList) and (
                self.nextVerseVotingRange[0] < TimeUtil.now() - self.voteDelay < self.nextVerseVotingRange[1]):
            optionIndex = random.randint(1, 2)
            desc = '(Virgo参与互动投票)'
            virgo_headers = LocustPublic.taurus_headers(self.userinfo['virgo_headers'], self.userinfo['authentication'])
            payload = dict(interactionId=str(self.interactionId),
                           optionIndex=optionIndex,
                           roomId=str(self.roomId),
                           interactionType="BOILING_STADIUM_VOTE",
                           accountId=self.accountId,
                           isSystemAccount=False,
                           contentId=self.contentUniqueId)
            url = f'{self.recordingHost}/virgo/classroom/boiling-stadium/attend-interaction'
            LocustPublic.post(self.httpClient, url, virgo_headers, payload, desc)
            self.voteDoneList.append(self.interactionId)

    def taurusBarrageSend(self, barrageInterval: int):
        if self.playingNodeRange[0] < TimeUtil.now() < self.playingNodeRange[1]:
            return
        barrageInterval = barrageInterval if barrageInterval > 0 else 0
        now = TimeUtil.now()
        if now - self.lastBRtimestamp > barrageInterval * 1000:
            desc = '(Taurus弹幕发送)'
            payload = dict(barrageLabel="ugc_word",
                           contentId=self.contentUniqueId,
                           barrageText=f"今晚8点，明世隐大哥带你上分！",
                           barrageType="ugc_word")
            url = f'{self.recordingHost}/taurus/barrage/send'
            LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
            self.lastBRtimestamp = now

    def classroomExit(self, ignoreError=True):
        time.sleep(self.virgoExitDelay / 1000)
        desc = '(Virgo退出课堂)'
        playDuration = 0
        for playingNodeRange in self.playingNodeRangeList:
            duration = playingNodeRange[1] - playingNodeRange[0]
            playDuration += duration
        payload = dict(
            effectiveness="EFFECTIVE",
            classroomType=self.classroomCode,
            exitType="EXIT_SECTION",
            trainingRecordId=self.trainingRecordId,
            classroomCode=self.classroomCode,
            endType="FINISH",
            clientLocalTime=TimeUtil.now(),
            calories=6,
            roomId=self.roomId,
            isRoomExit=True
        )
        url = f'{self.recordingHost}/virgo/classroom/multi/user/exit'
        if ignoreError:
            try:
                LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
            except Exception as err:
                pass
        else:
            LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)

    def taurusResultA(self, ignoreError=True):
        desc = '(Taurus完成页A)'
        payload = dict(contentId=self.contentUniqueId,
                       moduleId=102,
                       sourceType="POPUP",
                       accountId=self.accountId,
                       recordId=self.trainingRecordId,
                       roomId=self.roomId,
                       fieldKeys=[
                           "backgroundImage", "sourceImage", "titleImage", "qrCodeImage", "achievement", "courseName",
                           "duration", "calories", "level", "score", "rank", "avatarUrl", "userName", "courseEndTime",
                           "transcendental", "newRecord", "totalGroup", "totalRepeat", "liveCourse", "multiTraining",
                           "encouragingWords", "stadiumData"]
                       )
        url = f"{self.contentHost}/taurus/training/popup/h5/data"
        if ignoreError:
            try:
                LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
            except Exception as err:
                pass
        else:
            LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)

    def taurusResultB(self, ignoreError=True):
        desc = '(Taurus完成页)'
        payload = dict(queryScene="TRAINING_COMPLETE", roomId=self.roomId)
        url = f"{self.contentHost}/taurus/room/training/results/info"
        if ignoreError:
            try:
                LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
            except Exception as err:
                pass
        else:
            LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)

    def virgoResult(self, ignoreError=True):
        time.sleep(self.virgoResultDelay / 1000)
        desc = '(Virgo完成页)'
        payload = dict(roomId=self.roomId)
        url = f"{self.contentHost}/virgo/room/training/results/info"
        if ignoreError:
            try:
                LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
            except Exception as err:
                pass
        else:
            LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)

    def verseEndOperation(self):
        if self.verseEndReceived:
            self.verseEndReceived = False
            self.virgoVerseRankDataGet()
            worldRanksLiked = self.taurusVerseRankDataGet()
            if not worldRanksLiked:
                log.error(f"Taurus落排行榜数据异常: {worldRanksLiked}")
            self.verseListByIds()
            for liked in worldRanksLiked:
                self.taurusUpvoteVerse(liked.get("trainingRecordId"), self.currentVerseId, liked.get("accountId"))

    def sendBonesData(self):
        if int(self.accountId) in self.stageSelectedUsers:
            bonesData = random.choice(self.bonesData)
            for i in range(25):
                LocustMqttPublit.sendBonesData(self.mqttClient, ext=dict(roomId=self.roomId,
                                                                         topic=self.pubTopic,
                                                                         contentId=self.contentUniqueId,
                                                                         accountId=self.accountId,
                                                                         bonesData=bonesData
                                                                         ))
                time.sleep(0.002)

    def sendOneBonesDataV2(self):
        LocustMqttPublit.sendBonesDataV2(self.mqttClient, ext=dict(roomId=self.roomId,
                                                                   topic=self.topic,
                                                                   contentId=self.contentUniqueId,
                                                                   accountId=self.accountId,
                                                                   bonesData=self.bonesDataV3
                                                                   ))

    def sendOneBonesDataV3(self):
        print('上传骨骼点...')
        LocustMqttPublit.sendBonesDataV3(self.mqttClient, ext=dict(
            topic=self.topic,
            eventId=uuid.uuid4().hex[:16],
            schemaHash=None,
            eventModule=self.classroomCode,
            eventName=self.MULTIPLAYER_STAGE_SKELETON_EXPORT,
            operatorId="system",
            operatorType="system",
            targetId=self.targetId,
            targetType=self.classroomCode,
            eventTime=TimeUtil.now(),
            data=dict(
                bizMark=self.bizMark,
                bizIdentifier=self.targetId,
                serialNumber=None,
                tag=self.classroomCode,
                payload=dict(
                    tag=self.MULTIPLAYER_STAGE_SKELETON_EXPORT,
                    version=1,
                    content=dict(
                        accountId=self.accountId,
                        roomId=self.roomId,
                        contentId=None,
                        showType="START_WAITING",
                        bonesData=self.bonesDataV3,
                        reportTimestamp=TimeUtil.now(),
                        exportTimestamp=TimeUtil.now()
                    )
                )
            )
        ))

    def sendOneBonesDataV4(self):
        print('上传分数...')
        LocustMqttPublit.sendBonesDataV3(self.mqttClient, ext=dict(
            topic=self.topic,
            eventId=uuid.uuid4().hex[:16],
            schemaHash=None,
            eventModule=self.classroomCode,
            eventName=self.MULTIPLAYER_REALTIME_RANK,
            operatorId="system",
            operatorType="system",
            targetId=self.targetId,
            targetType=self.classroomCode,
            eventTime=TimeUtil.now(),
            data=dict(
                bizMark=self.bizMark,
                bizIdentifier=self.targetId,
                serialNumber=None,
                tag=self.classroomCode,
                payload=dict(
                    tag=self.MULTIPLAYER_REALTIME_RANK,
                    version=1,
                    content=dict(
                        enterOrders=None,
                        scores=None,
                        total=None,
                    )
                )
            )
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
        else:
            log.warning(f"未识别的消息类型: {MSG}")

    def iotCloseCallback(self):
        self.mqttClient.disconnect()
        self.iotWasBroken = True
