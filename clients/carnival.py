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


class CarnivalClient(object):
    def __init__(self):
        super(CarnivalClient, self).__init__()
        self.contentHost = 'http://stable-cp-content-nt.qa.fiture.com'
        self.recordingHost = 'http://stable-cp-recording-bff-nt.qa.fiture.com'
        self.iotHost = 'http://stable.up-iot-device.nt.qa.fiture.com'
        self.timeout = 5 * 60
        self.contentUniqueId = None
        self.broadcastStatus = None
        self.channelTopicToken = None
        self.classroomType = "BOILING_STADIUM"
        self.roomId = None
        self.trainingRecordId = None
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
        self.CONTENT_END = False

        self.voteDelay = random.randint(10000, 20000)
        self.virgoResultDelay = random.randint(1, 2500)
        self.virgoExitDelay = random.randint(1, 3000)
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
        self.mqttClient = LocustMqttPublit.getClientConnected(client, userinfo,
                                                              msgHandler=self.messageHandler,
                                                              closeCallback=self.iotCloseCallback,
                                                              extTopics=[])
        self.getLatestStadiumDetail(ignoreError=True)
        self.classroomType = "BOILING_STADIUM"
        self.contentUniqueId = nacos.config.get("carnival", dict()).get("contentId", 1)
        self.createRoom()
        self.getCourseInfo(ignoreError=True)
        self.classroomEnter()
        self.getPlayerList(ignoreError=True)
        self.getDeviceChannel()
        self.mqttClient.subscribe(*self.subBroadcastTopics, *self.subTopics)
        lastRunningtimestamp = TimeUtil.now()
        pushScore = nacos.config.get("carnival", dict()).get("push_score", -1)
        barrageInterval = nacos.config.get("carnival", dict()).get("barrage_interval", 10)
        while self.running:
            try:
                if TimeUtil.now() - lastRunningtimestamp > 60 * 1000:
                    EventReport.success(name="循环超时", response_time=TimeUtil.now() - lastRunningtimestamp)
                lastRunningtimestamp = TimeUtil.now()
                if nacos.config.get("carnival", dict()).get("exit", False):
                    break
                # 一秒发送一帧
                self.sendOneBonesDataV2()
                if not self.iotWasBroken:
                    self.sendHeartbeat()
                    self.sendRoundScores(pushScore)
                self.getTimingLine()
                self.attendInteraction()
                self.verseEndOperation()
                self.taurusBarrageSend(barrageInterval)
                # self.sendBonesData()
                now = TimeUtil.now()
                cost = now - lastRunningtimestamp
                if cost < 500:
                    time.sleep((500 - cost) / 1000)
                # self.sendOneBonesDataV2()
            except Exception as err:
                pass
            finally:
                now = TimeUtil.now()
                cost = now - lastRunningtimestamp
                if cost < 1000:
                    time.sleep((1000 - cost) / 1000)
        time.sleep(15)
        if not self.iotWasBroken:
            self.mqttClient.disconnect()
        # taurus全场点赞（给自己点赞）
        self.verseFullEndOperation()
        # virgo exit接口
        self.classroomExit(ignoreError=True)
        # taurus全场点赞（给自己点赞）
        self.verseFullEndOperation()
        self.CONTENT_END = False
        time.sleep(15 - self.virgoExitDelay / 1000)
        # virgo结果页
        self.virgoResult(ignoreError=True)
        # taurus全场排行榜
        self.taurusContentRankDataGet(ignoreError=True)
        time.sleep(15 - self.virgoResultDelay / 1000)
        # taurus v3结果页
        self.taurusResultB(ignoreError=True)
        # taurus h5结果页
        self.taurusResultA(ignoreError=True)
        log.info("客户端模拟结束")

    def send_post_2(self, client, userinfo, nacos: NACOS):
        roomId = 1621031158452707330
        contentId = 94472
        verseId = 702
        def upvote_list():
            desc = '(获取沸腾运动场房间段落点赞列表)'
            payload = dict(roomId=roomId, verseId=verseId, accountIds=[1542776629048369154, 1401805710601428994, 1498563497447985153])
            url = f'{self.recordingHost}/virgo/classroom/boiling-stadium/upvote-list'
            LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)

        def get_verse_rank():
            desc = '(Virgo获取段落排行榜数据)'
            payload = dict(roomId=roomId, contentId=contentId,
                           verseId=verseId)
            url = f'{self.recordingHost}/virgo/verse/rank/data/get'
            resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
            content = resp.get("content")
            worldRanks = content.get("worldRank")
            # 获取所有6个用户排行
            worldRanksLiked = list(filter(lambda rank: rank.get("position", 99999) <= 1000, worldRanks))
            log.debug(f"virgo段落排行榜数据: {content}")
            accountIds = [liked.get("accountId") for liked in worldRanksLiked]
            log.info(f'获取到排行榜用户：{accountIds}')
        self.prepare(client, userinfo)
        upvote_list()
        # get_verse_rank()

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

    def getLatestStadiumDetail(self, ignoreError=False):
        desc = '(Taurus获取沸腾运动信息)'
        url = f"{self.contentHost}/taurus/series/latest-stadium-detail"
        payload = dict()
        if ignoreError:
            try:
                resp = LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
            except Exception as err:
                return
        else:
            resp = LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
        content = resp.get("content")
        classroomInfo = content.get("classroomInfo")
        log.debug(f"Taurus获取沸腾运动信息: {content}")
        if classroomInfo:
            self.classroomType = classroomInfo.get("classroomTypes")[0].get("classroomType")
        stadiumInfo = content.get("stadiumInfo")
        if stadiumInfo:
            self.contentUniqueId = stadiumInfo.get("contentId")
            self.broadcastStatus = stadiumInfo.get("broadcastStatus")

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
        worldRanks = content.get("worldRank")
        # 获取所有6个用户排行
        worldRanksLiked = list(filter(lambda rank: rank.get("position", 99999) <= 1000, worldRanks))
        log.debug(f"virgo段落排行榜数据: {content}")
        return worldRanksLiked

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
        desc = '(Taurus段落&排行榜点赞)'
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

    def taurusFullUpvoteVerse(self, trainingRecordId, likedUserId, ignoreError=True):
        desc = '(Taurus全场点赞)'
        payload = dict(
            trainingRecordId=trainingRecordId,
            contentId=self.contentUniqueId,
            likedUserId=likedUserId,
            event="LIKE")
        url = f'{self.recordingHost}/taurus/classroom/upvote/record'
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
        payload = dict(roomId=str(self.roomId),
                       classroomType=self.classroomType,
                       trainingRecordId=str(self.trainingRecordId),
                       duration=TimeUtil.now() - self.startTimestamp,
                       effectiveDuration=playDuration,
                       playDuration=playDuration,
                       result=float(self.totalScore),
                       unit="SCORE",
                       endType="FINISH",
                       clientLocalTime=TimeUtil.now(),
                       effectiveness="EFFECTIVE",
                       calories=66,
                       wearHrmEffectiveDuration=0,
                       timeNodeType="STOP",
                       isRoomExit=True,
                       verse=dict(
                           currentVerseId=self.currentVerseId,
                           verseIds=self.verseIds
                       )
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
        desc = '(Taurus完成页B)'
        payload = dict(trainingRecordId=self.trainingRecordId, queryScene="TRAINING_COMPLETE")
        url = f"{self.contentHost}/taurus/training/results/info/v3"
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
        payload = dict(trainingRecordId=self.trainingRecordId, accountId=self.accountId)
        url = f"{self.contentHost}/virgo/stadium/end/result"
        if ignoreError:
            try:
                LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
            except Exception as err:
                pass
        else:
            LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)

    def verseEndOperation(self):
        if self.verseEndReceived:
            self.verseEndReceived = True
            VirgoWorldRanksLiked = self.virgoVerseRankDataGet()
            if not VirgoWorldRanksLiked:
                log.error(f"Virgo排行榜数据异常: {VirgoWorldRanksLiked}")
            worldRanksLiked = self.taurusVerseRankDataGet()
            if not worldRanksLiked:
                log.error(f"Taurus落排行榜数据异常: {worldRanksLiked}")
            self.verseListByIds()
            for liked in worldRanksLiked:
                self.taurusUpvoteVerse(liked.get("trainingRecordId"), self.currentVerseId, liked.get("accountId"))
            for liked in VirgoWorldRanksLiked:
                self.taurusUpvoteVerse(liked.get("trainingRecordId"), self.currentVerseId, liked.get("accountId"))
            time.sleep(1)

    def verseFullEndOperation(self):
        if self.CONTENT_END:
            for i in range(10):
                self.taurusFullUpvoteVerse(self.trainingRecordId, self.accountId)
                time.sleep(1)

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
        if int(self.accountId) in self.stageSelectedUsers:
            bonesDataV2 = random.choice(self.bonesDataV2)
            LocustMqttPublit.sendBonesDataV2(self.mqttClient, ext=dict(roomId=self.roomId,
                                                                       topic=self.pubTopic,
                                                                       contentId=self.contentUniqueId,
                                                                       accountId=self.accountId,
                                                                       bonesData=bonesDataV2
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
        else:
            log.warning(f"未识别的消息类型: {MSG}")

    def iotCloseCallback(self):
        self.mqttClient.disconnect()
        self.iotWasBroken = True
