import json
import random
import time
import uuid

from datas.bones import get_bones
from datas.heart import HEART
from libs.eventReport import EventReport
from libs.iot.protobuf_operation import ProtoBufQuickBurning
from libs.timeUtil import TimeUtil
from libs.public import LocustPublic, LocustNewMqttPublit
from libs.public import LocustMqttPublit
from libs.nacos import NACOS
from libs.logger import log
from libs.protobuf_file import COLLECTIVE_CHALLENGE_SHOW_PLAYERS_EVENT_pb2, \
    ROOM_TIMING_LINE_SYNC_EVENT_pb2, COACH_POST_EMOJI_EVENT_pb2, \
    STAGE_SHOW_RESULT_EVENT_pb2, MC_COACH_REPORT_SKELETON_EVENT_pb2, \
    COLLECTIVE_CHALLENGE_PROGRESS_EVENT_pb2, MC_COACH_STOP_REPORT_SKELETON_EVENT_pb2, \
    ENTRY_GROUP_UPDATE_EVENT_pb2, \
    SEND_ONLINE_PLAYER_EVENT_pb2, BOTH_PK_SUMMARY_EVENT_pb2, \
    COACH_GUIDE_DETAIL_EVENT_pb2, \
    PK_SERVER_TRANSFER_PLAYER_DATA_EVENT_pb2, PLAYER_TRAINING_MOMENT_EVENT_pb2, \
    START_ROOM_EVENT_pb2, END_ROOM_EVENT_pb2, \
    COLLECTIVE_CHALLENGE_SUMMARY_EVENT_pb2, PLAYER_HIGH_FIVE_EVENT_pb2, \
    ASSIGN_STAGE_SHOW_SKELETON_EVENT_pb2, quick_burning_pb2, BOTH_PK_PROGRESS_EVENT_pb2, \
    BOTH_PK_GROUPING_EVENT_pb2, BARRAGE_EVENT_pb2, ENTRY_GROUPING_EVENT_pb2, PLAYER_ENTRY_EVENT_pb2


class QuickBurningClient(object):
    def __init__(self):
        super(QuickBurningClient, self).__init__()
        self.contentHost = 'http://stable-cp-content-nt.qa.fiture.com'
        self.recordingHost = 'http://stable-cp-recording-bff-nt.qa.fiture.com'
        self.iotHostApp = 'http://stable-bfs-app-nt.qa.fiture.com'
        # self.cmsHost = 'http://cms-api.qa.fiture.com'
        self.timeout = 5 * 60
        self.trainingRecordId = None
        self.needReportScore = None
        self.currentVerseId = None
        self.verseIds = []
        #
        self.subBroadcastTopics = []
        self.subTopicsB = None
        self.subTopicsC = None
        #
        self.httpClient = None
        self.mqttClient = None
        self.userinfo = dict()
        self.taurus_headers = None
        self.virgo_headers = None
        self.lastHBtimestamp = 0
        self.lastHBtimestampGroupCourses = 0
        self.lastHBtimestampBonesData = 0
        self.lastHBtimestampFitnessBonesData = 0
        self.lastHBtimestampBeat = 0
        self.lastScoretimestamp = 0
        self.lastSendAllstamp = 0
        self.lastAllstamp = 0
        self.lastGetResourceStamp = 0
        self.simulatedHeartRateStamp = 0
        self.burningPointsSimulatedTimeStamp = 0
        self.burningPointsSimulatedStamp = 0
        self.iotWasBroken = False
        self.startTimestamp = 0
        self.playingNodeRangeList = []
        self.currentVerseScores = 0
        self.currentVerseCalorie = 0
        self.stageSelectedUsers = []

        self.virgoExitDelay = random.randint(1, 3000)
        self.virgoEnter = random.randint(1, 10000)
        self.bonesDataV3 = get_bones()
        self.bone = None
        self.isCreated = False
        self.GROUP_FITNESS_CLASS = "GROUP_FITNESS_CLASS"
        self.roomItemId = None
        self.courseType = None
        self.item_update_list = []
        self.expectEndTime = None  # 最后一节课程退出时间，调用退出训练接口时机
        self.pubTopic = None
        self.pubTopics = []
        self.pubTopicsBackstage = []  # 后台pubTopices

        self.bizId = None
        self.bizType = None
        self.clientId = None
        self.customizeTopicPrefix = None
        self.password = None
        self.sslUrl = None
        self.wssUrl = None
        self.username = None
        self.barrageSubTopic = None
        self.coachSubTopic = None

        self.accountId = None
        self.isRunning = True
        self.roomStatus = None  # 房间状态
        self.expectStartTime = 0  # 房间预计开始时间
        self.playergroupTopicB = None
        self.playergroupTopicC = None
        self.ENTRY_GROUPING_EVENT = False  # 分组完成
        self.LastMotionMessageStamp = 0
        self.LastPointMessageStamp = 0
        self.LastDanmuStamp = 0
        self.itemList = None
        self.accountIdList = []
        self.skeleton_event_accountIds = None  # 教练通知骨骼点上报指令对应的人
        self.WEBBREPORT = False  # web端通知上报骨骼点
        self.showRoomItemId = None  # 抢镜发生在哪个环节
        self.VirgoBShow = False  # virgo展示骨骼点
        self.roomItemLastDuration = None  # 最后一个Item的总时长（毫秒）
        self.roomItemLastProgress = None  # 最后一个Item的当前进度（毫秒）
        self.RoomExit = False  # 房间结束
        self.HIGH_FIVE = False  # 是否击掌
        self.roomItemType = None
        self.roomItemSubType = None
        self.is_get_all = False
        self.score = 0
        self.getAllData = {}
        self.TRAINING_RESULT = False
        self.heartRate = 60
        self.calories = 0
        self.burningPointsNumber = 0
        self.ENTER_SEND_RATE = []  # 候场页发送心率的人
        self.lastRoomItemId = None
        self.groupCodeList = {}
        self.roomInfo = None
        self.verseIdList = []
        self.verseIdContent = None

        self.contentUniqueId = 96393
        self.roomId = 1716996624931057666
        self.playerScore = 0  # 星
        self.keyframe = 100  # 关键帧分数
        self.keyframeTotal = 100  # 关键帧总分
        self.awesome = 15  # 超赞
        self.resonance = 15  # 同屏共振次数
        self.ROOM_TYPE = 'FAST_BURNING'  # 'RHYTHM'  # 'FAST_BURNING'
        self.maxBurningPointsNumber = 12  # 获得的最大燃点

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
        userinfo['roomId'] = self.roomId
        userinfo['tags'] = self.ROOM_TYPE
        self.roomInfo = dict(accountId=self.accountId, roomId=self.roomId, tags=self.ROOM_TYPE)

        getNacos = nacos.config.get("quick_burning", {})
        self.contentUniqueId = getNacos.get("contentUniqueId", 0)
        self.roomId = getNacos.get("roomId", 0)
        self.ROOM_TYPE = getNacos.get("roomType", 'FAST_BURNING')
        self.keyframeTotal = getNacos.get("keyframeTotal", 100)
        self.keyframe = getNacos.get("keyframeTotal", 100)
        self.maxBurningPointsNumber = getNacos.get('maxBurningPointsNumber', 12)
        # 创建房间
        # self.create_room()
        # 房间列表，查询房间是否为CREATE且类型为团课1
        # 如果查询到团课，就返回
        # while True:
        #     self.room_list()
        #     if self.isCreated:
        #         break
        # time.sleep(self.virgoEnter / 1000)
        self.content_detail()
        self.list_by_ids()
        self.get_resource()
        self.room_enter()
        self.getDeviceChannelTopic()
        self.mqttClient = LocustMqttPublit.getClientConnected(client, userinfo,
                                                              msgHandler=self.messageHandler,
                                                              closeCallback=self.iotCloseCallback,
                                                              extTopics=[],
                                                              type='quick_burning',
                                                              mqttConfig=dict(
                                                                  clientId=self.clientId,
                                                                  password=self.password,
                                                                  sslUrl=self.sslUrl,
                                                                  wssUrl=self.wssUrl,
                                                                  username=self.username,
                                                                  subTopicsB=self.subTopicsB,
                                                                  subTopicsC=self.subTopicsC,
                                                              )
                                                              )
        self.mqttClient.roomId = self.roomId
        self.mqttClient.coachSubTopic = self.coachSubTopic
        self.mqttClient.subscribe(*[self.subTopicsB], *[self.subTopicsC, self.barrageSubTopic])

        if self.roomStatus == 'STARTED' and self.trainingRecordId is None:
            self.get_resource()
            self.mqttClient.subscribe(*[self.playergroupTopicB], *[self.playergroupTopicC])
            self.mqttClient.playergroupTopicB = self.playergroupTopicB
            self.mqttClient.playergroupTopicC = self.playergroupTopicC
            self.start_room()
            self.ENTRY_GROUPING_EVENT = True

        lastRunningtimestamp = TimeUtil.now()
        while self.isRunning:
            try:
                if TimeUtil.now() - lastRunningtimestamp > 60 * 1000:
                    EventReport.success(name="循环超时", response_time=TimeUtil.now() - lastRunningtimestamp)
                lastRunningtimestamp = TimeUtil.now()
                self.sendHeartbeat()
                self.simulated_heart_rate()
                self.burningPointsSimulated()
                if not self.ENTRY_GROUPING_EVENT:
                    log.info(f'分组前发送心率的用户数据：currentAccountId={self.accountId}, 发送心率的用户列表：{self.ENTER_SEND_RATE}')
                    if int(self.accountId) in self.ENTER_SEND_RATE:
                        # log.info(f'分组前发送消息：{self.subTopicsB}')
                        self.sendMotionMessage(self.subTopicsB)
                if self.ENTRY_GROUPING_EVENT:
                    log.info(f'分组后发送消息：{self.playergroupTopicB}')
                    self.sendMotionMessage(self.playergroupTopicB)
                if self.WEBBREPORT:
                    self.sendBonePoints('COACH_SKELETON_EVENT')  # web端骨骼点展示
                if self.showRoomItemId == self.roomItemId and self.VirgoBShow:
                    self.sendBonePoints('ASSIGN_STAGE_SHOW_SKELETON_EVENT')  # virgo端骨骼点展示
                # self.sendVirgoBarrageSend()
                log.info(
                    f'发送阶段结果上报：trainingRecordId={self.trainingRecordId}, roomItemType={self.roomItemType}，roomItemId={self.roomItemId}，item_update_list={self.item_update_list}')
                if self.trainingRecordId is not None and self.roomItemType != 'REST':
                    if f'COURSE_{self.roomItemId}' not in self.item_update_list:
                        self.item_update('item阶段结果上报')
                        self.item_update_list.append(f'COURSE_{self.roomItemId}')

                # 击掌结果上报
                if self.roomItemSubType == 'TRAINING_RESULT':
                    if not self.TRAINING_RESULT:
                        LocustNewMqttPublit.high_fives_result(self.mqttClient, 'PLAYER_HIGH_FIVE_EVENT',
                                                              self.roomInfo)
                        self.TRAINING_RESULT = True

                if self.roomItemType == 'REST' or self.roomItemSubType == 'INTERMISSION':
                    self.sendGetAll()
                # self.sendGetResource()
                # 获得燃点调用
                if self.roomStatus == 'STARTED' and self.ROOM_TYPE == 'FAST_BURNING':
                    self.sendGoalAchieve()
                # # 房间结束
                # if isinstance(self.roomItemProgress, int) and isinstance(self.roomItemDuration, int):
                #     if self.roomItemProgress >= self.roomItemDuration:
                #         self.item_update('最后一个item结束上报')
                #         log.info(f'房间结束：roomItemProgress={self.roomItemProgress}，roomItemDuration={self.roomItemDuration}')
                #         break

                if self.RoomExit:
                    log.info('房间结束')
                    break
                now = TimeUtil.now()
                cost = now - lastRunningtimestamp
                if cost < 500:
                    time.sleep((500 - cost) / 1000)
            except Exception as err:
                pass
            finally:
                now = TimeUtil.now()
                cost = now - lastRunningtimestamp
                if cost < 1000:
                    time.sleep((1000 - cost) / 1000)
        time.sleep(15)
        if not self.iotWasBroken:
            startTimeStamp = TimeUtil.now()
            self.mqttClient.disconnect()
            endTimeStamp = TimeUtil.now()
            EventReport.success(request_type="MQTT",
                                name=f"客户端模拟结束，IOT链接主动断开",
                                response_time=endTimeStamp - startTimeStamp,
                                response_length=0
                                )

    # step_1
    def create_room(self):
        desc = '(Virgo创建房间)'
        payload = {
            "contentId": self.contentUniqueId,
            "name": f"速燃课性能测试-{uuid.uuid4().hex[:4]}",
            "type": "PUBLIC",
            "accountId": self.accountId,
            "classroomCode": self.ROOM_TYPE,
            "creatorRole": "USER",
            "deviceMode": "DOMESTIC",
            "sourceDevice": "VIRGO",
            "mcCoachId": 1,
            # 预计创建时间expectCreateTime = 下一分钟；预计开始时间expectStartTime = 下两分钟。
            "expectCreateTime": TimeUtil.now() + 30 * 8,
            "expectStartTime": TimeUtil.now() + 60 * 9,
            "creatorName": "yzq"
        }
        url = f"{self.recordingHost}/room/prepare"
        log.info(f"create-room: {payload}")
        log.info(f'taurus_headers：{self.taurus_headers}')
        resp = LocustPublic.post(self.httpClient, url, self.taurus_headers, payload, desc)
        content = resp.get('content')
        self.roomId = content.get('roomId')
        log.debug(f"virgo创建房间: msg={payload}, resp={resp}")

    # step_2
    def room_enter(self):
        desc = '(Virgo进入&加入房间)'
        payload = {"source": "VIRGO", "clientLocalTime": TimeUtil.now(),
                   "classroom": {"roomId": self.roomId, "code": self.ROOM_TYPE}, "deviceMode": "DOMESTIC",
                   "deviceType": "VIRGO", "trainingType": "COURSE_MODE"}
        url = f'{self.recordingHost}/virgo/classroom/multi/user/enter'
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        content = resp.get("content")
        log.info(f'Virgo进入&加入房间：{json.dumps(content)}')
        self.bizId = content.get('channel').get('bizId')
        self.bizType = content.get('channel').get('bizType')
        # self.channelTopicToken = content.get("channelTopic").get("playerToken")
        # self.groupClassSkeletonTopicToken = content.get("groupClassSkeletonTopic").get("playerToken")

    # step_3
    def getDeviceChannelTopic(self):
        desc = '(Virgo获取Channel场景通道)'
        payload = dict(bizType=self.bizType, bizId=self.bizId)
        url = f'{self.iotHostApp}/iot/channel/fetch'
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        content = resp.get("content")

        log.info(f"获取场景通道： {json.dumps(content)}")
        self.subTopicsB = [i.get("topic") for i in content.get('mqttTopics') if i.get('topic').split('/')[-1] == 'b'][0]
        self.subTopicsC = [i.get("topic") for i in content.get('mqttTopics') if i.get('topic').split('/')[-1] == 'c'][0]
        self.clientId = content.get('clientId')
        self.customizeTopicPrefix = content.get('customizeTopicPrefix')
        self.password = content.get('password')
        self.sslUrl = content.get('sslUrl')
        self.wssUrl = content.get('wssUrl')
        self.username = content.get('username')
        self.barrageSubTopic = self.customizeTopicPrefix + 'barrage'  # 弹幕广播通道
        self.coachSubTopic = self.customizeTopicPrefix + 'coach'  # 教练广播通道
        # "high_stadium","low_stadium","standard_stadium"
        # self.subBroadcastTopics = list(map(lambda c: c.get("subBroadcastTopic"), content))
        # self.subTopics = list(map(lambda c: c.get("pubTopic"), content))
        # log.info(f"订阅广播topic: {self.subBroadcastTopics}")
        # log.info(f"订阅单播topic: {self.subTopics}")
        # for channel in content:
        #     pubTopic = channel.get('pubTopic')
        #     self.pubTopics.append(pubTopic)
        # log.info(f"广播topic列表: {self.pubTopics}")
        # if not self.pubTopics:
        #     raise FitureException("没有找到standard_stadium 通道！")

    # step_4
    def start_room(self):
        desc = '(virgo开始上课)'
        payload = {"clientLocalTime": TimeUtil.now(), "deviceMode": "DOMESTIC", "deviceType": "VIRGO",
                   "roomId": self.roomId, "roomItemId": self.roomItemId, "source": "TAURUS",
                   "trainingType": "COURSE_MODE"}
        url = f"{self.recordingHost}/virgo/classroom/user/start"
        log.info(f"virgo开始上课: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        content = resp.get('content')
        self.trainingRecordId = content.get('trainingRecordId')
        log.info(f"virgo开始上课：{resp}")

    def virgoBarrageSend(self):
        desc = '(弹幕发送)'
        danList = ['BODY_NAMASTE', 'BODY_HAND_HEART']
        payload_1 = {"sceneBizId": self.roomId, "scene": self.ROOM_TYPE, "barrageCode": random.choice(danList)}
        payload_2 = {"scene": self.ROOM_TYPE, "sceneBizId": self.roomId, "userId": 1, "userRole": "MC_COACH",
                     "barrageCode": "COACH_EMOJI",
                     "textArgsMap": {"coach": "大山", "user": "Test__111", "emojiCode": "COME_ON", "emojiText": "加油"}}
        payload_3 = {"scene": self.ROOM_TYPE, "sceneBizId": self.roomId, "userId": self.accountId,
                     "userRole": "ACCOUNT", "barrageCode": "UGC_WORD", "textArgsMap": {
                "text": "大哥带你起飞1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"}}
        payload = [payload_1, payload_2, payload_3]
        url = f'{self.recordingHost}/virgo/room/scene/barrage/send'
        LocustPublic.post(self.httpClient, url, self.virgo_headers, random.choice(payload), desc)

    # step_5
    def item_update(self, desc):
        desc = f'(virgo {desc})'
        _payload = {"burningPoint": [], "calories": self.calories, "clientLocalTime": TimeUtil.now(),
                    "deviceParam": {"deviceMode": "DOMESTIC", "heartRateDeviceName": "心率模拟器",
                                    "heartRateDeviceType": "VIRTUALLY", "sourceDevice": "VIRGO"}, "duration": 65317,
                    "effectiveDuration": 64243, "feedback": {"keyframeStrongDetail": []},
                    "heartRate": [105, 105, 105, 107, 108, 108, 108, 109, 111, 112, 114, 115, 115, 115, 116, 116, 114,
                                  114, 113, 113, 113, 114, 114, 115, 116, 116, 116, 116, 115, 115, 115, 116, 116, 117,
                                  117, 117, 119, 119, 117, 115, 115, 116, 117, 119, 119, 119, 118, 118, 118, 118, 119,
                                  119, 118, 118, 118, 118, 118, 117, 116, 116, 114, 114, 114, 114],
                    "playDuration": 65000, "result": float(self.playerScore), "roomId": self.roomId,
                    "roomItemId": self.roomItemId, "scores": [], "trainingRecordId": self.trainingRecordId,
                    "unit": "BURNING_POINT"}
        payload_2 = {"burningPoint": [], "calories": self.calories, "clientLocalTime": TimeUtil.now(),
                     "deviceParam": {"deviceMode": "DOMESTIC", "sourceDevice": "VIRGO"}, "duration": 189406,
                     "effectiveDuration": 187968, "feedback": {
                "keyframeStrongDetail": [{"key": "AWESOME", "repeats": 2}, {"key": "PERFECT", "repeats": 3},
                                         {"key": "GOOD", "repeats": 3}, {"key": "COME_ON", "repeats": 8}]},
                     "performance": {"resonance": 0}, "playDuration": 189000, "resonanceDetail": [],
                     "result": float(self.playerScore),
                     "roomId": self.roomId, "roomItemId": self.roomItemId,
                     "scores": [{"score": 15.0, "type": "ITEM", "unit": "STAR"},
                                {"score": 360.0, "type": "ITEM", "unit": "SCORE"}],
                     "trainingRecordId": self.trainingRecordId,
                     "unit": "STAR"}
        if self.ROOM_TYPE == 'FAST_BURNING':
            payload = _payload
        else:
            payload = payload_2
        url = f"{self.recordingHost}/virgo/classroom/multi/user/training/update"
        log.info(f"virgo item 阶段结果上报: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        log.info(f"virgo item阶段结果上报：{resp}")

    # step_5
    def end_training(self):
        desc = '(virgo 用户结束训练)'
        payload = {
            "burningPoint": [{"x": 827, "y": 1.0}, {"x": 887, "y": 1.0}, {"x": 947, "y": 1.0}, {"x": 1007, "y": 1.0},
                             {"x": 1067, "y": 1.0}, {"x": 1127, "y": 1.0}, {"x": 1187, "y": 1.0}, {"x": 1247, "y": 1.0},
                             {"x": 1307, "y": 1.0}, {"x": 1367, "y": 1.0}, {"x": 1427, "y": 1.0}, {"x": 1488, "y": 1.0},
                             {"x": 1548, "y": 1.0}, {"x": 1608, "y": 1.0}, {"x": 1668, "y": 1.0}], "calories": 138,
            "clientLocalTime": TimeUtil.now(), "deviceParam": {"deviceMode": "DOMESTIC", "sourceDevice": "VIRGO"},
            "duration": 961218, "effectiveDuration": 895800, "endType": "FINISH",
            "heartRate": HEART,
            "playDuration": 900000, "result": 15, "roomId": self.roomId, "trainingRecordId": self.trainingRecordId,
            "unit": "BURNING_POINT"}
        url = f"{self.recordingHost}/virgo/room/user/end-training"
        log.info(f"virgo item 用户结束训练: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        log.info(f"virgo 用户结束训练：{resp}")

    # step_5
    def get_all(self):
        desc = '(virgo [速燃团课]获取速燃课堂所有用户训练数据（按入场分组聚合返回）)'
        startTimeStamp = TimeUtil.now()
        payload = {"roomId": self.roomId}
        url = f"{self.recordingHost}/virgo/classroom/training-data/fast-burning/get-all"
        log.info(f"virgo 速燃团课]获取速燃课堂所有用户训练数据（按入场分组聚合返回）: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        log.info(f"virgo 速燃团课]获取速燃课堂所有用户训练数据（按入场分组聚合返回）：{resp}, getAllData={self.getAllData}")
        if self.getAllData.get(self.accountId) == json.dumps(resp):
            endTimeStamp = TimeUtil.now()
            EventReport.failure(request_type="接口",
                                name="[速燃团课]获取速燃课堂所有用户训练数据（按入场分组聚合返回）",
                                response_time=endTimeStamp - startTimeStamp,
                                response_length=0,
                                exception=Exception('和上次获取的数据一致')
                                )
            self.getAllData[self.accountId] = json.dumps(resp)

    # step_5
    def goal_achieve(self):
        desc = '速燃团课]查询是否首燃或者达到燃点目标'
        payload = {"roomId": self.roomId,
                   "burningPoint": self.burningPointsNumber if self.ROOM_TYPE == 'FAST_BURNING' else self.awesome}
        url = f"{self.recordingHost}/virgo/room/highlight/stage-show/burning-point/goal/achieve"
        log.info(f"速燃团课]查询是否首燃或者达到燃点目标: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        log.info(f"速燃团课]查询是否首燃或者达到燃点目标：{resp}")

    # step_5
    def content_detail(self):
        desc = '内容详情'
        payload = {"contentId": self.contentUniqueId}
        url = f"{self.contentHost}/virgo/content/detail"
        log.info(f"内容详情参数: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        log.info(f"内容详情返回body：{json.dumps(resp)}")
        content = resp.get('content')
        segmentList = list(filter(lambda x: x.get('verseId') is not None, content.get('segmentList')))
        # 获取verseId列表，用来在virgo/verse/list-by-ids接口查询自环节信息
        self.verseIdList = list(map(lambda x: str(x.get('verseId')), segmentList))

    def list_by_ids(self):
        desc = '环节信息'
        payload = {"verseIds": self.verseIdList}
        url = f"{self.contentHost}/virgo/verse/list-by-ids"
        log.info(f"环节信息参数: {payload}")
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        log.info(f"环节信息参数返回body：{json.dumps(resp)}")
        self.verseIdContent = resp.get('content')

    # step_11
    def get_resource(self):
        desc = '(virgo获取资源)'
        payload = dict(roomId=self.roomId)
        url = f"{self.recordingHost}/virgo/classroom/resource/get"
        log.info(f"enter-room: {payload}")
        log.info(f'virgo_headers：{self.virgo_headers}')
        resp = LocustPublic.post(self.httpClient, url, self.virgo_headers, payload, desc)
        content = resp.get("content")
        log.info(f'virgo获取资源：{json.dumps(content)}')
        self.roomStatus = content.get('roomStatus')
        self.expectStartTime = content.get('expectStartTime')
        self.itemList = content.get('itemList')
        try:
            self.roomItemId = list(filter(lambda x: x.get('status') in ('STARTED', 'CREATED'), self.itemList))[0].get(
                'id')
        except Exception:
            pass
        try:
            groupChannels = content['itemResources']['ENTRY_GROUPING']['channels']
            self.playergroupTopicB = self.customizeTopicPrefix + \
                                     list(filter(lambda x: x.get('type') == 'BROADCAST', groupChannels))[0].get(
                                         'topicSuffix')
            self.playergroupTopicC = self.customizeTopicPrefix + \
                                     list(filter(lambda x: x.get('type') == 'CONTROL', groupChannels))[0].get(
                                         'topicSuffix')
        except Exception:
            pass
        log.info(f'资源列表：{self.itemList}')
        try:
            EndItem = sorted(self.itemList, key=lambda keys: keys['expectEndTime'], reverse=True)
            self.expectEndTime = EndItem[0].get('expectEndTime')
            log.info(f'课堂结束时间：{self.expectEndTime}')
        except Exception:
            pass
        self.lastRoomItemId = self.itemList[-1].get('id')
        # FitureException(msg='resource接口获取房间状态失败')

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
        if now - self.lastHBtimestampBeat > 30 * 1000:
            LocustNewMqttPublit.sendHeartbeat(self.mqttClient, self.roomInfo)
            self.lastHBtimestampBeat = now

    # step_13
    def sendGoalAchieve(self):
        # 5s发一次
        now = TimeUtil.now()
        if now - self.lastSendAllstamp > 5 * 1000:
            if self.burningPointsNumber == 1 or self.burningPointsNumber >= self.maxBurningPointsNumber:
                self.goal_achieve()
            self.lastSendAllstamp = now

    # step_13
    def sendGetAll(self):
        # 5s发一次
        now = TimeUtil.now()
        if now - self.lastAllstamp > 60 * 1000:
            self.get_all()
            self.lastAllstamp = now

    # step_13
    def sendGetResource(self):
        # 5s发一次
        now = TimeUtil.now()
        if now - self.lastGetResourceStamp > 5 * 1000:
            self.get_resource()
            self.lastGetResourceStamp = now

    def simulated_heart_rate(self):
        # 模拟心率
        now = TimeUtil.now()
        if now - self.simulatedHeartRateStamp > 5 * 1000:
            if self.heartRate >= 160:
                self.heartRate = 160
            else:
                self.heartRate += random.randint(1, 10)
            self.calories += 10
            self.simulatedHeartRateStamp = now
        # now = TimeUtil.now()
        # if now - self.simulatedHeartRateStamp > 1:
        #     if self.heartRate >= 200:
        #         self.heartRate = 200
        #     else:
        #         self.heartRate += random.randint(0, 1)
        #     self.calories += 10
        #     self.simulatedHeartRateStamp = now

    def burningPointsSimulated(self):
        # 魔力点/星模拟
        now = TimeUtil.now()

        if now - self.burningPointsSimulatedTimeStamp > 30 * 1000:
            if self.heartRate >= 150:
                self.burningPointsNumber += 1
                if self.playerScore < 5:
                    self.playerScore += 1
            self.burningPointsSimulatedTimeStamp = now

    # step_13
    def sendMotionMessage(self, subTopic):
        # 1s发一次
        now = TimeUtil.now()
        if now - self.LastMotionMessageStamp > 1 * 1000:
            self.mqttClient.roomItemId = self.roomItemId
            try:
                getItem = list(filter(lambda ed: ed.get("id") == self.roomItemId, self.itemList))[0]
                self.mqttClient.roomItemType = getItem.get('type')
                self.mqttClient.roomItemSubType = getItem.get('subType')
                self.score += 1
                log.info(
                    f'上报分数：{self.score}, heartRate：{self.heartRate}, 卡路里：{self.calories}, 魔力点：{self.burningPointsNumber}')
                LocustNewMqttPublit.motion_message(self.mqttClient, dict(score=self.score, subTopic=subTopic,
                                                                         heartRate=self.heartRate,
                                                                         calories=self.calories,
                                                                         burningPoints=self.burningPointsNumber,
                                                                         playerScore=float(self.playerScore),
                                                                         keyframe=float(self.keyframe),
                                                                         keyframeTotal=float(self.keyframeTotal),
                                                                         awesome=self.awesome,
                                                                         resonance=self.resonance,
                                                                         **self.roomInfo
                                                                         ))
            except Exception:
                pass
            self.LastMotionMessageStamp = now

    # step_13
    def sendVirgoBarrageSend(self):
        # 1s发一次
        now = TimeUtil.now()
        if now - self.LastDanmuStamp > 5 * 1000:
            self.virgoBarrageSend()
            self.LastDanmuStamp = now

    # step_14
    def sendBonePoints(self, msgCode):
        # 1s发一次
        now = TimeUtil.now()
        if now - self.LastPointMessageStamp > 1 * 1000:
            # if self.accountId in self.accountIdList or self.accountId == self.skeleton_event_accountIds:
            LocustNewMqttPublit.send_bone_points(self.mqttClient, msgCode,
                                                 self.roomInfo)
            self.LastPointMessageStamp = now

    def messageHandler(self, msg: str, topic: str = "?", host: str = "?", port: int = 0):
        # log.info(f'得到消息：{msg}')
        # msgLength = len(msg)
        startTimeStamp = TimeUtil.now()
        startProcessTimestamp = TimeUtil.now()
        getObj = ProtoBufQuickBurning(self.mqttClient, quick_burning_pb2,
                                      self.roomInfo)
        getObj.default_filed(self.ROOM_TYPE)
        msgData = getObj.to_obj(msg)
        log.info(f'Msg，类型：{type(getObj)}，消息：{msgData}')
        tags = msgData.tags
        if tags != self.ROOM_TYPE:
            log.info(f'tags类型错误，不支持对类型：{tags}')
            return
        msgCode = msgData.msgCode
        log.info(f'msgCode，类型：{type(msgCode)}，消息：{msgCode}')
        if msgCode == 'ROOM_TIMING_LINE_SYNC_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, ROOM_TIMING_LINE_SYNC_EVENT_pb2, self.roomInfo)
            getObj.room_timing_line_sync_event()
            msgData = getObj.to_obj(payload)
            self.roomItemId = msgData.roomItemId
            if self.roomItemId == self.lastRoomItemId:  # 获取最后一个itemId
                self.roomItemLastDuration = msgData.duration
                self.roomItemLastProgress = msgData.progress
            roomItemInfo = list(filter(lambda x: x.get('id') == self.roomItemId, self.itemList))[0]
            self.roomItemType = roomItemInfo.get('type')
            self.roomItemSubType = roomItemInfo.get('subType')
            log.info(f'房间时间轴进度同步，消息：{msgData}')
        elif msgCode == 'START_ROOM_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, START_ROOM_EVENT_pb2, self.roomInfo)
            getObj.start_room_event_pb2()
            msgData = getObj.to_obj(payload)
            log.info(f'房间开始，消息：{msgData}')
            self.roomItemId = msgData.roomItemId
            self.start_room()
        elif msgCode == 'PLAYER_ENTRY_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, PLAYER_ENTRY_EVENT_pb2, self.roomInfo)
            getObj.player_entry_event()
            msgData = getObj.to_obj(payload)
            for i in msgData.players:
                if i.accountId not in self.ENTER_SEND_RATE:
                    self.ENTER_SEND_RATE.append(i.accountId)
            log.info(f'用户进入房间消息，消息：{msgData}，ENTER_SEND_RATE={self.ENTER_SEND_RATE}')
        elif msgCode == 'ENTRY_GROUPING_EVENT':
            payload = msgData.payload
            log.info(f'入场分组完成消息-payload，消息：{msgData}')
            getObj = ProtoBufQuickBurning(self.mqttClient, ENTRY_GROUPING_EVENT_pb2, self.roomInfo)
            getObj.entry_grouping_event()
            msgLength = getObj.byte_length(payload)
            msgData = getObj.to_obj(payload)
            log.info(f'入场分组完成消息，消息：{msgData}')
            for i in msgData.groups:
                myCode = i.code
                getGroupAccountIds = [i.accountId for i in i.players]
                log.info(f'获取到分组：{myCode} {getGroupAccountIds}')
                if int(self.accountId) in getGroupAccountIds:
                    self.playergroupTopicB = \
                        [self.customizeTopicPrefix + i.topicSuffix for i in i.channels if i.type == 'BROADCAST'][0]
                    self.playergroupTopicC = \
                        [self.customizeTopicPrefix + i.topicSuffix for i in i.channels if i.type == 'CONTROL'][0]
                    log.info(f'在分组里：{self.accountId}：{self.playergroupTopicB} {self.playergroupTopicC}')
                    EventReport.success(request_type="MQTT",
                                        name=f"获取到分组：(b={self.playergroupTopicB}，c={self.playergroupTopicC})",
                                        response_time=TimeUtil.now() - startProcessTimestamp,
                                        response_length=msgLength)
                    self.mqttClient.subscribe(*[self.playergroupTopicB], *[self.playergroupTopicC])
                    self.mqttClient.playergroupTopicB = self.playergroupTopicB
                    self.mqttClient.playergroupTopicC = self.playergroupTopicC
                    EventReport.success(request_type="MQTT",
                                        name=f"入场分组完成消息({topic})",
                                        response_time=TimeUtil.now() - startProcessTimestamp,
                                        response_length=msgLength)
                    self.ENTRY_GROUPING_EVENT = True
                    break

        elif msgCode == 'ENTRY_GROUP_UPDATE_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, ENTRY_GROUP_UPDATE_EVENT_pb2, self.roomInfo)
            getObj.entry_group_update_event()
            msgData = getObj.to_obj(payload)
            log.info(f'入场分组组员变更消息，消息：{msgData}')
        elif msgCode == 'END_ROOM_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, END_ROOM_EVENT_pb2, self.roomInfo)
            getObj.end_room_event()
            msgData = getObj.to_obj(payload)
            log.info(f'房间结束，消息：{msgData}')
            self.RoomExit = True
        elif msgCode == 'COACH_ENTER_EVENT':
            log.info(f'教练入场')
        elif msgCode == 'COACH_START_GUIDE_EVENT':
            self.skeleton_event_accountIds = self.accountId
            log.info(f'教练开始巡场')
        elif msgCode == 'COACH_END_GUIDE_EVENT':
            self.skeleton_event_accountIds = None
            log.info(f'教练结束巡场')
        elif msgCode == 'COACH_GUIDE_DETAIL_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, COACH_GUIDE_DETAIL_EVENT_pb2, self.roomInfo)
            getObj.coach_guide_detail_event()
            msgData = getObj.to_obj(payload)
            log.info(f'教练发送巡场指导数据，消息：{msgData}')
        elif msgCode == 'COACH_END_GUIDE_EVENT':
            log.info(f'教练结束巡场指导')
        elif msgCode == 'COLLECTIVE_CHALLENGE_SHOW_PLAYERS_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, COLLECTIVE_CHALLENGE_SHOW_PLAYERS_EVENT_pb2, self.roomInfo)
            getObj.collective_challenge_show_players_event()
            msgData = getObj.to_obj(payload)
            log.info(f'合力挑战准备下发挑战目标和展示玩家的消息，消息：{msgData}')
            endTimeStamp = TimeUtil.now()
            EventReport.success(request_type="MQTT",
                                name=f"合力挑战准备下发挑战目标和展示玩家的消息({topic})",
                                response_time=endTimeStamp - startTimeStamp,
                                response_length=getObj.byte_length(payload)
                                )
        elif msgCode == 'PK_SERVER_TRANSFER_PLAYER_DATA_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, PK_SERVER_TRANSFER_PLAYER_DATA_EVENT_pb2, self.roomInfo)
            getObj.pk_server_transfer_player_data_event()
            msgData = getObj.to_obj(payload)
            log.info(f'PK(合力挑战、红蓝PK)服务端转发用户实时数据消息到房间，消息：{msgData}')
            endTimeStamp = TimeUtil.now()
            EventReport.success(request_type="MQTT",
                                name=f"PK(合力挑战、红蓝PK)服务端转发用户实时数据消息到房间({topic})",
                                response_time=endTimeStamp - startTimeStamp,
                                response_length=getObj.byte_length(payload)
                                )
        elif msgCode == 'COLLECTIVE_CHALLENGE_PROGRESS_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, COLLECTIVE_CHALLENGE_PROGRESS_EVENT_pb2, self.roomInfo)
            getObj.collective_challenge_progress_event()
            msgData = getObj.to_obj(payload)
            log.info(f'合力挑战进行中下发总挑战次数和鼓励语消息，消息：{msgData}')
            endTimeStamp = TimeUtil.now()
            EventReport.success(request_type="MQTT",
                                name=f"合力挑战进行中下发总挑战次数和鼓励语消息({topic})",
                                response_time=endTimeStamp - startTimeStamp,
                                response_length=getObj.byte_length(payload)
                                )
        elif msgCode == 'COLLECTIVE_CHALLENGE_SUMMARY_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, COLLECTIVE_CHALLENGE_SUMMARY_EVENT_pb2, self.roomInfo)
            getObj.collective_challenge_summary_event()
            msgData = getObj.to_obj(payload)
            log.info(f'合力挑战总结页下发消息，消息：{msgData}')
            endTimeStamp = TimeUtil.now()
            EventReport.success(request_type="MQTT",
                                name=f"合力挑战总结页下发消息({topic})",
                                response_time=endTimeStamp - startTimeStamp,
                                response_length=getObj.byte_length(payload)
                                )
        elif msgCode == 'BOTH_PK_GROUPING_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, BOTH_PK_GROUPING_EVENT_pb2, self.roomInfo)
            getObj.both_pk_grouping_event()
            msgData = getObj.to_obj(payload)
            log.info(f'红蓝PK分组完成消息，消息：{msgData}')
            endTimeStamp = TimeUtil.now()
            EventReport.success(request_type="MQTT",
                                name=f"红蓝PK分组完成消息({topic})",
                                response_time=endTimeStamp - startTimeStamp,
                                response_length=getObj.byte_length(payload)
                                )
        elif msgCode == 'BOTH_PK_PROGRESS_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, BOTH_PK_PROGRESS_EVENT_pb2, self.roomInfo)
            getObj.both_pk_progress_event()
            msgData = getObj.to_obj(payload)
            log.info(f'红蓝PK进行中下发总挑战次数和鼓励语消息，消息：{msgData}')
            endTimeStamp = TimeUtil.now()
            EventReport.success(request_type="MQTT",
                                name=f"红蓝PK进行中下发总挑战次数和鼓励语消息({topic})",
                                response_time=endTimeStamp - startTimeStamp,
                                response_length=getObj.byte_length(payload)
                                )
        elif msgCode == 'BOTH_PK_SUMMARY_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, BOTH_PK_SUMMARY_EVENT_pb2, self.roomInfo)
            getObj.both_pk_summary_event()
            msgData = getObj.to_obj(payload)
            log.info(f'红蓝PK总结页下发消息，消息：{msgData}')
            endTimeStamp = TimeUtil.now()
            EventReport.success(request_type="MQTT",
                                name=f"红蓝PK总结页下发消息({topic})",
                                response_time=endTimeStamp - startTimeStamp,
                                response_length=getObj.byte_length(payload)
                                )
        elif msgCode == 'STAGE_SHOW_RESULT_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, STAGE_SHOW_RESULT_EVENT_pb2, self.roomInfo)
            getObj.stage_show_result_event()
            msgData = getObj.to_obj(payload)
            log.info(f'房间抢镜的计算结果，消息：{msgData}')
            self.showRoomItemId = msgData.roomItemId
            self.VirgoBShow = True
            endTimeStamp = TimeUtil.now()
            EventReport.success(request_type="MQTT",
                                name=f"房间抢镜的计算结果下发消息({topic})",
                                response_time=endTimeStamp - startTimeStamp,
                                response_length=getObj.byte_length(payload)
                                )

        elif msgCode == 'PLAYER_TRAINING_MOMENT_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, PLAYER_TRAINING_MOMENT_EVENT_pb2, self.roomInfo)
            getObj.player_training_moment_event()
            msgData = getObj.to_obj(payload)
            log.info(f'用户瞬时运动消息下发({topic})，消息：{msgData}')
            endTimeStamp = TimeUtil.now()
            EventReport.success(request_type="MQTT",
                                name=f"用户瞬时运动消息下发({topic})",
                                response_time=endTimeStamp - startTimeStamp,
                                response_length=getObj.byte_length(payload)
                                )
        elif msgCode == 'PLAYER_HIGH_FIVE_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, PLAYER_HIGH_FIVE_EVENT_pb2, self.roomInfo)
            getObj.player_high_five_event()
            msgData = getObj.to_obj(payload)
            log.info(f'击掌结果上报，消息：{msgData}')
            self.HIGH_FIVE = True
            endTimeStamp = TimeUtil.now()
            EventReport.success(request_type="MQTT",
                                name=f"击掌结果上报消息下发({topic})",
                                response_time=endTimeStamp - startTimeStamp,
                                response_length=getObj.byte_length(payload)
                                )
        elif msgCode == 'MC_COACH_REPORT_SKELETON_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, MC_COACH_REPORT_SKELETON_EVENT_pb2, self.roomInfo)
            getObj.mc_coach_report_skeleton_event()
            msgData = getObj.to_obj(payload)
            log.info(f'教练通知骨骼点上报指令，消息：{msgData}')
            self.WEBBREPORT = True
        elif msgCode == 'MC_COACH_STOP_REPORT_SKELETON_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, MC_COACH_STOP_REPORT_SKELETON_EVENT_pb2, self.roomInfo)
            getObj.mc_coach_stop_report_skeleton_event()
            msgData = getObj.to_obj(payload)
            log.info(f'教练通知骨骼点停止上报指令，消息：{msgData}')
            self.WEBBREPORT = False
        elif msgCode == 'COACH_SKELETON_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, ASSIGN_STAGE_SHOW_SKELETON_EVENT_pb2, self.roomInfo)
            getObj.coach_skeleton_event()
            msgData = getObj.to_obj(payload)
            log.info(f'web端显示骨骼点，消息：{msgData}')
        elif msgCode == 'ASSIGN_STAGE_SHOW_SKELETON_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, ASSIGN_STAGE_SHOW_SKELETON_EVENT_pb2, self.roomInfo)
            getObj.assign_stage_show_skeleton_event()
            msgData = getObj.to_obj(payload)
            log.info(f'教练指定上镜，消息：{msgData}')
            self.skeleton_event_accountIds = msgData.accountId
        elif msgCode == 'BARRAGE_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, BARRAGE_EVENT_pb2, self.roomInfo)
            getObj.barrage_event()
            msgData = getObj.to_obj(payload)
            log.info(f'弹幕下发消息，消息：{msgData}')
        elif msgCode == 'COACH_POST_EMOJI_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, COACH_POST_EMOJI_EVENT_pb2, self.roomInfo)
            getObj.coach_post_emoji_event()
            msgData = getObj.to_obj(payload)
            log.info(f'教练发送表情，消息：{msgData}')
        elif msgCode == 'SEND_ONLINE_PLAYER_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, SEND_ONLINE_PLAYER_EVENT_pb2, self.roomInfo)
            getObj.send_online_player_event()
            msgData = getObj.to_obj(payload)
            log.info(f'玩家退出发送房间在线玩家总数和15个玩家信息、当前退出玩家ID，消息：{msgData}')
        elif msgCode == 'ENTRY_GROUP_NEWLY_CREATED_EVENT':
            payload = msgData.payload
            getObj = ProtoBufQuickBurning(self.mqttClient, ENTRY_GROUPING_EVENT_pb2, self.roomInfo)
            getObj.entry_group_newly_created_event()
            msgData = getObj.to_obj(payload)
            log.info(f'产生新的入场分组消息（新玩家中途进入且当前分组已满员的情况），消息：{msgData}')
        else:
            log.info(f'不支持的消息类型，msgCode：{msgCode}')

    def iotCloseCallback(self):
        self.mqttClient.disconnect()
        self.iotWasBroken = True
