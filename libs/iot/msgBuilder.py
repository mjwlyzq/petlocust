import hashlib
import json
import random
import time
import uuid
from paho.mqtt.client import Client

from datas.bones import get_bones
from libs.iot.fitureEnum import IotMsgTypeEnum, BusinessTypeEnum, IotAppTypeEnum
from libs.iot.protobuf_operation import ProtoBufQuickBurning
from libs.logger import log
from libs.timeUtil import TimeUtil
from libs.protobuf_file import quick_burning_pb2, PLAYER_TRAINING_MOMENT_EVENT_pb2, \
    ASSIGN_STAGE_SHOW_SKELETON_EVENT_pb2, PLAYER_HIGH_FIVE_EVENT_pb2


class IotMsgBuilder:
    def __init__(self):
        pass

    @staticmethod
    def build_tpl():
        return {
            "v": None,
            "sessionId": None,
            "msgType": None,
            "msgId": None,
            "destType": None,
            "destId": None,
            "ack": None,
            "ts": None,
            "tag": None,
            "payload": None,
            "destApp": None,
            "srcApp": None,
            "ext": None,
            "sign": None,
        }

    @staticmethod
    def wrap_sign(m, secret):
        sign_plain = ''
        sign_plain += str(m["v"]) if m["v"] is not None else ""
        sign_plain += str(m["sessionId"]) if m["sessionId"] is not None else ""
        sign_plain += str(m["msgType"]) if m["msgType"] is not None else ""
        sign_plain += str(m["msgId"]) if m["msgId"] is not None else ""
        sign_plain += str(m["destType"]) if m["destType"] is not None else ""
        sign_plain += str(m["destId"]) if m["destId"] is not None else ""
        sign_plain += str(m["tag"]) if m["tag"] is not None else ""
        sign_plain += str(m["payload"]) if m["payload"] is not None else ""
        sign_plain += str(m["ack"]) if m["ack"] is not None else ""
        sign_plain += str(m["ts"]) if m["ts"] is not None else ""
        sign_plain += str(m["srcApp"]) if m["srcApp"] is not None else ""
        sign_plain += str(m["destApp"]) if m["destApp"] is not None else ""
        sign_plain += str(m["ext"]) if m["ext"] is not None else ""
        sign_plain += secret
        sign = hashlib.md5(sign_plain.encode(encoding='UTF-8')).hexdigest()
        m['sign'] = sign
        return m

    @staticmethod
    def build_HB(client: Client):
        try:
            m = IotMsgBuilder.build_tpl()
            m["v"] = 2
            m["sessionId"] = client.cfg["sessionId"]
            m["msgType"] = IotMsgTypeEnum.HB.value
            m["ts"] = str(int(round(time.time() * 1000)))
            m = IotMsgBuilder.wrap_sign(m, client.cfg["secret"])
            return m
        except Exception as e:
            log.error(f'创建心跳消息异常 clientId={client.clientId} e={e}')
            raise Exception('创建心跳消息异常')

    @staticmethod
    def build_HI(client: Client):
        m = IotMsgBuilder.build_tpl()
        m['v'] = 2
        m['sessionId'] = client.cfg.get("sessionId")
        m['msgType'] = IotMsgTypeEnum.HI.value
        m['msgId'] = str(uuid.uuid4())
        m['destType'] = BusinessTypeEnum.SESSION.value
        m['destId'] = client.cfg.get("sessionId")
        m['tag'] = 'INIT'
        m['ack'] = 1
        m['ts'] = int(round(time.time() * 1000))
        m['srcApp'] = IotAppTypeEnum.taurus.value
        m['destApp'] = IotAppTypeEnum.virgo.value
        m['ext'] = None
        m['payload'] = None
        IotMsgBuilder.wrap_sign(m, client.cfg.get("secret"))
        return m

    @staticmethod
    def build_request_connect(client: Client):
        m = IotMsgBuilder.build_tpl()
        m['v'] = 1
        m['sessionId'] = client.cfg.get("sessionId")
        m['msgType'] = IotMsgTypeEnum.MSG.value
        m['msgId'] = str(uuid.uuid4())
        m['destType'] = BusinessTypeEnum.SESSION.value
        m['destId'] = client.cfg["sessionId"]
        m['tag'] = 'MSG'
        m['ack'] = 1
        m['ts'] = int(round(time.time() * 1000))
        content = {
            "env": "qa",
            "appKey": "qEaLKIrIIgabW9znqnXIvaWopI6BVbm2",
            "token": client.token,
            "weight": "65.0",
            "height": 170.00,
            "userName": "Locust测试",
            "avatarUrl": "http://dev-oss1.fiture.com/avatarUrl/b5ab248c87774cf6b90d7e3dd9e64417.jpg",
            "accountId": client.userinfo.get("authentication").get("accountId"),
            "age": 31,
            "gender": 0,
            "forceConnect": True,
            "connectType": "manual",
            "versionCode": "30200",
            "versionName": "3.2.0",
            "client": "taurus_android"
        }
        payload = {"ac": "request_connect", "content": content, "number": 1}
        m['payload'] = json.dumps(payload)
        IotMsgBuilder.wrap_sign(m, client.cfg["secret"])
        return m

    @staticmethod
    def build_RTS(client: Client, ext: dict):
        m = IotMsgBuilder.build_tpl()
        m['v'] = 2
        m['sessionId'] = client.cfg.get("sessionId")
        m['msgType'] = IotMsgTypeEnum.EVENT.value
        m['msgId'] = str(uuid.uuid4())
        # m['destType'] = BusinessTypeEnum.SESSION.value
        # m['destId'] = client.cfg["sessionId"]
        m['tag'] = 'STADIUM'
        m['srcApp'] = ".virgo"
        m['ack'] = 0
        m['ts'] = TimeUtil.now()
        content = dict(
            accountId=str(ext.get("accountId")),
            calories=ext.get("calories"),
            currentTimestamp=TimeUtil.now(),
            duration=ext.get("duration"),
            effectiveDuration=ext.get("effectiveDuration"),
            playDuration=ext.get("playDuration"),
            roomId=ext.get("roomId"),
            score=ext.get("score"),
            trainingRecordId=str(ext.get("trainingRecordId")),
            unit="score",
            verseId=str(ext.get("verseId")),
            wearHrmEffectiveDuration=0
        )
        payload = dict(tag="VERSE_REALTIME", version=1379, content=content)
        m['payload'] = json.dumps(payload)
        IotMsgBuilder.wrap_sign(m, client.cfg["secret"])
        return m

    @staticmethod
    def build_Bones(client: Client, ext: dict):
        m = IotMsgBuilder.build_tpl()
        m['v'] = 2
        m['sessionId'] = client.cfg.get("sessionId")
        m['msgType'] = IotMsgTypeEnum.EVENT.value
        m['msgId'] = str(uuid.uuid4())
        # m['destType'] = BusinessTypeEnum.SESSION.value
        # m['destId'] = client.cfg["sessionId"]
        m['tag'] = 'STADIUM'
        m['srcApp'] = ".virgo"
        m['ack'] = 0
        m['ts'] = TimeUtil.now()
        content = dict(
            accountId=str(ext.get("accountId")),
            contentId=ext.get("contentId"),
            bonesData=ext.get("bonesData"),
            currentTimestamp=TimeUtil.now(),
        )
        payload = dict(tag="STAGE_REPORT_SKELETON", version=1430, content=content)
        m['payload'] = json.dumps(payload)
        IotMsgBuilder.wrap_sign(m, client.cfg["secret"])
        return m

    @staticmethod
    def build_Bones_v2(client: Client, ext: dict):
        m = IotMsgBuilder.build_tpl()
        m['v'] = 2
        m['sessionId'] = client.cfg.get("sessionId")
        m['msgType'] = IotMsgTypeEnum.EVENT.value
        m['msgId'] = str(uuid.uuid4())
        # m['destType'] = BusinessTypeEnum.SESSION.value
        # m['destId'] = client.cfg["sessionId"]
        m['tag'] = 'STADIUM'
        m['srcApp'] = ".virgo"
        m['ack'] = 0
        m['ts'] = TimeUtil.now()
        content = dict(
            accountId=str(ext.get("accountId")),
            contentId=ext.get("contentId"),
            bonesData=ext.get("bonesData"),
            currentTimestamp=TimeUtil.now(),
        )
        payload = dict(tag="STAGE_REPORT_SKELETON_V2", version=1430, content=content)
        m['payload'] = json.dumps(payload)
        IotMsgBuilder.wrap_sign(m, client.cfg["secret"])
        return m

    @staticmethod
    def build_Bones_v3(client: Client, ext: dict):
        m = IotMsgBuilder.build_tpl()
        m['v'] = 2
        m['sessionId'] = client.cfg.get("sessionId")
        m['msgType'] = IotMsgTypeEnum.EVENT.value
        m['msgId'] = str(uuid.uuid4())
        # m['destType'] = BusinessTypeEnum.SESSION.value
        # m['destId'] = client.cfg["sessionId"]
        m['tag'] = 'MULTIPLAYER'
        m['srcApp'] = ".virgo"
        m['ack'] = 0
        m['ts'] = TimeUtil.now()
        content = dict(
            showType="BATTLE_TIME",
            currentTimestamp=TimeUtil.now(),
            clientVersion=1500,
            reportTimestamp=TimeUtil.now(),
            **ext
        )
        payload = dict(tag=ext.get('tag'), version=1, content=content)
        m['payload'] = json.dumps(payload)
        IotMsgBuilder.wrap_sign(m, client.cfg["secret"])
        log.info(f'模拟发送消息：{json.dumps(m)}')
        return m

    @staticmethod
    def build_scores_together(client: Client, ext: dict):
        m = IotMsgBuilder.build_tpl()
        m['v'] = 2
        m['sessionId'] = client.cfg.get("sessionId")
        m['msgType'] = IotMsgTypeEnum.EVENT.value
        m['msgId'] = str(uuid.uuid4())
        # m['destType'] = BusinessTypeEnum.SESSION.value
        # m['destId'] = client.cfg["sessionId"]
        m['tag'] = 'MULTIPLAYER'
        m['srcApp'] = ".virgo"
        m['ack'] = 0
        m['ts'] = TimeUtil.now()
        content = dict(
            roomId=str(ext.get("roomId")),
            roomItemId=str(ext.get("roomItemId")),
            accountId=str(ext.get("accountId")),
            trainingRecordId=str(ext.get("trainingRecordId")),
            currentTimestamp=TimeUtil.now(),
            calories=str(ext.get("calories")),
            duration=str(ext.get("duration")),
            effectiveDuration=str(ext.get("effectiveDuration")),
            playDuration=str(ext.get("playDuration")),
            score=str(ext.get("score")),
            unit=str(ext.get("unit")),
            wearHrmEffectiveDuration=str(ext.get("wearHrmEffectiveDuration")),
            effectiveness=str(ext.get("effectiveness")),
        )
        payload = dict(tag=str(ext.get('tag')), version=1500, content=content)
        m['payload'] = json.dumps(payload)
        log.info(f'分数上报pubTopic；{m}')
        IotMsgBuilder.wrap_sign(m, client.cfg["secret"])
        return m


    @staticmethod
    def build_group_class_together(client: Client, ext: dict):
        m = IotMsgBuilder.build_tpl()
        m['v'] = 2
        m['sessionId'] = client.cfg.get("sessionId")
        m['msgType'] = IotMsgTypeEnum.EVENT.value
        m['msgId'] = str(uuid.uuid4())
        # m['destType'] = BusinessTypeEnum.SESSION.value
        # m['destId'] = client.cfg["sessionId"]
        m['tag'] = 'MULTIPLAYER'
        m['srcApp'] = ".virgo"
        m['ack'] = 0
        m['ts'] = TimeUtil.now()
        content = dict(**ext)
        payload = dict(tag=str(ext.get('tag')), version=1500, content=content)
        m['payload'] = json.dumps(payload)
        log.info(f'团课数据上报pubTopic；{m}')
        IotMsgBuilder.wrap_sign(m, client.cfg["secret"])
        return m


class IotNewMsgBuilder:
    def __init__(self):
        pass

    @staticmethod
    def build_tpl():
        return {
            "v": None,
            "sessionId": None,
            "msgType": None,
            "msgId": None,
            "destType": None,
            "destId": None,
            "ack": None,
            "ts": None,
            "tag": None,
            "payload": None,
            "destApp": None,
            "srcApp": None,
            "ext": None,
            "sign": None,
        }

    @staticmethod
    def wrap_sign(m, secret):
        sign_plain = ''
        sign_plain += str(m["v"]) if m["v"] is not None else ""
        sign_plain += str(m["sessionId"]) if m["sessionId"] is not None else ""
        sign_plain += str(m["msgType"]) if m["msgType"] is not None else ""
        sign_plain += str(m["msgId"]) if m["msgId"] is not None else ""
        sign_plain += str(m["destType"]) if m["destType"] is not None else ""
        sign_plain += str(m["destId"]) if m["destId"] is not None else ""
        sign_plain += str(m["tag"]) if m["tag"] is not None else ""
        sign_plain += str(m["payload"]) if m["payload"] is not None else ""
        sign_plain += str(m["ack"]) if m["ack"] is not None else ""
        sign_plain += str(m["ts"]) if m["ts"] is not None else ""
        sign_plain += str(m["srcApp"]) if m["srcApp"] is not None else ""
        sign_plain += str(m["destApp"]) if m["destApp"] is not None else ""
        sign_plain += str(m["ext"]) if m["ext"] is not None else ""
        sign_plain += secret
        sign = hashlib.md5(sign_plain.encode(encoding='UTF-8')).hexdigest()
        m['sign'] = sign
        return m

    @staticmethod
    def build_HB(client: Client):
        try:
            m = IotMsgBuilder.build_tpl()
            m["v"] = 2
            m["sessionId"] = client.cfg["sessionId"]
            m["msgType"] = IotMsgTypeEnum.HB.value
            m["ts"] = str(int(round(time.time() * 1000)))
            m = IotMsgBuilder.wrap_sign(m, client.cfg["secret"])
            return m
        except Exception as e:
            log.error(f'创建心跳消息异常 clientId={client.clientId} e={e}')
            raise Exception('创建心跳消息异常')

    @staticmethod
    def build_HI(Client, kwargs):
        p = ProtoBufQuickBurning(Client, quick_burning_pb2, kwargs)
        # p.msgCode = 'PLAYER_ENTRY_EVENT'  # 用户进入房间消息
        # - 消息协议中使用了priority来表明消息处理的优先级, 值越小, 优先级越高.
        # - 服务端publish消息时, 可以指定priority.当没有指定priority时, 默认control消息的priority为0, 非control消息(broadcast消息)
        # 的priority为100.
        # - 端 - 端之间的消息的priority完全由客户端自行设置.建议不重要的消息priority使用100, 重要的消息priority使用50, 始终保证服务端发布的control消息的优先级最高.
        p.default_filed(kwargs.get('tags'))
        getStr = p.to_str()
        length = p.byte_length(getStr)
        return p.to_str(), length

    @staticmethod
    def build_motion_message(Client, kwargs):
        p = ProtoBufQuickBurning(Client, PLAYER_TRAINING_MOMENT_EVENT_pb2, kwargs)
        playerScoreITEM = p.person.PlayerScore()
        playerScoreTOTAL = p.person.PlayerScore()
        playerScoreMODULE = p.person.PlayerScore()
        playerScoreBurntnGpotin = p.person.PlayerScore()
        playerScoreKEYFRAME = p.person.PlayerScore()
        playerScoreKEYFRAMETOTAL = p.person.PlayerScore()
        playerFeedback = p.person.Feedback()
        playerPerformanceTotal = p.person.Performance()
        playerPerformanceItem = p.person.Performance()
        p.player_training_moment_event()
        p.person.accountId = int(Client.userinfo.get('authentication').get('accountId'))
        p.person.heartRate = kwargs.get('heartRate')
        p.person.heartRatePercent = int(kwargs.get('heartRate') / 200 * 100)
        p.person.calories = kwargs.get('calories')
        p.person.burningPoints = kwargs.get('burningPoints')
        p.person.skeletonRecognized = True
        p.person.fakeHeartRate = 1
        p.person.currentTimestamp = int(time.time())
        p.person.roomItemId = Client.roomItemId
        p.person.roomItemType = Client.roomItemType
        p.person.roomItemSubType = Client.roomItemSubType
        p.person.score = kwargs.get('score')
        p.person.unit = "SCORE"
        p.person.serverTransfer = 0
        p.person.movementPerformance.movementId = 1
        p.person.movementPerformance.repeats = 2
        p.person.movementPerformance.rate = 3.00

        # 星
        playerScoreITEM.score = kwargs.get('playerScore', 0.0)
        playerScoreITEM.unit = 'STAR'
        playerScoreITEM.type = 'ITEM'

        playerScoreTOTAL.score = kwargs.get('playerScore', 0.0)
        playerScoreTOTAL.unit = 'STAR'
        playerScoreTOTAL.type = 'TOTAL'

        playerScoreMODULE.score = kwargs.get('playerScore', 0.0)
        playerScoreMODULE.unit = 'STAR'
        playerScoreMODULE.type = 'MODULE'

        playerScoreKEYFRAME.score = kwargs.get('keyframe', 0.0)
        playerScoreKEYFRAME.unit = 'SCORE'
        playerScoreKEYFRAME.type = 'KEYFRAME'

        playerScoreKEYFRAMETOTAL.score = kwargs.get('keyframeTotal', 0.0)
        playerScoreKEYFRAMETOTAL.unit = 'SCORE'
        playerScoreKEYFRAMETOTAL.type = 'KEYFRAME_TOTAL'

        playerScoreBurntnGpotin.score = 1.0
        playerScoreBurntnGpotin.unit = 'BURNING_POINT'
        playerScoreBurntnGpotin.type = 'INCR'

        p.person.scores.extend([playerScoreITEM, playerScoreTOTAL, playerScoreMODULE, playerScoreKEYFRAME, playerScoreKEYFRAMETOTAL, playerScoreBurntnGpotin])
        # p.person.teamScores.extend([playerScoreITEM, playerScoreTOTAL, playerScoreMODULE, playerScoreKEYFRAME, playerScoreKEYFRAMETOTAL])

        playerFeedback.key = 'AWESOME'  # 超赞
        playerFeedback.repeats = kwargs.get('awesome', 0)
        playerFeedback.type = 'REAL_TIME'

        p.person.feedback.extend([playerFeedback])

        playerPerformanceTotal.resonance = kwargs.get('resonance', 0)  # 同频共振次数
        playerPerformanceTotal.type = 'TOTAL'

        playerPerformanceItem.resonance = kwargs.get('resonance', 0)  # 同频共振次数
        playerPerformanceItem.type = 'ITEM'

        p.person.performance.extend([playerPerformanceTotal, playerPerformanceItem])

        getStr = p.to_str()
        length = p.byte_length(getStr)
        log.info(f'发送的数据：{p.to_obj(getStr)}')
        return getStr, length

    @staticmethod
    def build_all(Client, msgCode, payload, kwargs):
        p = ProtoBufQuickBurning(Client, quick_burning_pb2, kwargs)
        p.default_filed(kwargs.get('tags'))
        p.person.msgCode = msgCode
        p.person.payload = payload
        getStr = p.to_str()
        log.info(f'发送消息全部：{p.to_obj(getStr)}')
        length = p.byte_length(getStr)
        return p.to_str(), length

    @staticmethod
    def build_bone_points(Client, kwargs):
        p = ProtoBufQuickBurning(Client, ASSIGN_STAGE_SHOW_SKELETON_EVENT_pb2, kwargs)
        p.assign_stage_show_skeleton_event()
        p.person.accountId = int(Client.userinfo.get('authentication').get('accountId'))
        p.person.skeletonData = random.choice(get_bones())
        myHeartRate = random.randint(60, 200)
        p.person.heartRate = int(myHeartRate / 200 * 100)
        p.person.heartRatePercent = random.randint(60, 190)
        getStr = p.to_str()
        log.info(f'发送骨骼点数据解析：{p.to_obj(getStr)}')
        length = p.byte_length(getStr)
        return getStr, length

    @staticmethod
    def build_high_fives_result(Client, kwargs):
        p = ProtoBufQuickBurning(Client, PLAYER_HIGH_FIVE_EVENT_pb2, kwargs)
        p.player_high_five_event()
        p.person.accountId = int(Client.userinfo.get('authentication').get('accountId'))
        p.person.success = 10
        p.person.currentTimestamp = int(time.time())
        getStr = p.to_str()
        log.info(f'击掌发送Topic数据：{p.to_obj(getStr)}')
        length = p.byte_length(getStr)
        return getStr, length

    @staticmethod
    def build_request_connect(client: Client):
        m = IotMsgBuilder.build_tpl()
        m['v'] = 1
        m['sessionId'] = client.cfg.get("sessionId")
        m['msgType'] = IotMsgTypeEnum.MSG.value
        m['msgId'] = str(uuid.uuid4())
        m['destType'] = BusinessTypeEnum.SESSION.value
        m['destId'] = client.cfg["sessionId"]
        m['tag'] = 'MSG'
        m['ack'] = 1
        m['ts'] = int(round(time.time() * 1000))
        content = {
            "env": "qa",
            "appKey": "qEaLKIrIIgabW9znqnXIvaWopI6BVbm2",
            "token": client.token,
            "weight": "65.0",
            "height": 170.00,
            "userName": "Locust测试",
            "avatarUrl": "http://dev-oss1.fiture.com/avatarUrl/b5ab248c87774cf6b90d7e3dd9e64417.jpg",
            "accountId": client.userinfo.get("authentication").get("accountId"),
            "age": 31,
            "gender": 0,
            "forceConnect": True,
            "connectType": "manual",
            "versionCode": "30200",
            "versionName": "3.2.0",
            "client": "taurus_android"
        }
        payload = {"ac": "request_connect", "content": content, "number": 1}
        m['payload'] = json.dumps(payload)
        IotMsgBuilder.wrap_sign(m, client.cfg["secret"])
        return m

    @staticmethod
    def build_RTS(client: Client, ext: dict):
        m = IotMsgBuilder.build_tpl()
        m['v'] = 2
        m['sessionId'] = client.cfg.get("sessionId")
        m['msgType'] = IotMsgTypeEnum.EVENT.value
        m['msgId'] = str(uuid.uuid4())
        # m['destType'] = BusinessTypeEnum.SESSION.value
        # m['destId'] = client.cfg["sessionId"]
        m['tag'] = 'STADIUM'
        m['srcApp'] = ".virgo"
        m['ack'] = 0
        m['ts'] = TimeUtil.now()
        content = dict(
            accountId=str(ext.get("accountId")),
            calories=ext.get("calories"),
            currentTimestamp=TimeUtil.now(),
            duration=ext.get("duration"),
            effectiveDuration=ext.get("effectiveDuration"),
            playDuration=ext.get("playDuration"),
            roomId=ext.get("roomId"),
            score=ext.get("score"),
            trainingRecordId=str(ext.get("trainingRecordId")),
            unit="score",
            verseId=str(ext.get("verseId")),
            wearHrmEffectiveDuration=0
        )
        payload = dict(tag="VERSE_REALTIME", version=1379, content=content)
        m['payload'] = json.dumps(payload)
        IotMsgBuilder.wrap_sign(m, client.cfg["secret"])
        return m

    @staticmethod
    def build_Bones(client: Client, ext: dict):
        m = IotMsgBuilder.build_tpl()
        m['v'] = 2
        m['sessionId'] = client.cfg.get("sessionId")
        m['msgType'] = IotMsgTypeEnum.EVENT.value
        m['msgId'] = str(uuid.uuid4())
        # m['destType'] = BusinessTypeEnum.SESSION.value
        # m['destId'] = client.cfg["sessionId"]
        m['tag'] = 'STADIUM'
        m['srcApp'] = ".virgo"
        m['ack'] = 0
        m['ts'] = TimeUtil.now()
        content = dict(
            accountId=str(ext.get("accountId")),
            contentId=ext.get("contentId"),
            bonesData=ext.get("bonesData"),
            currentTimestamp=TimeUtil.now(),
        )
        payload = dict(tag="STAGE_REPORT_SKELETON", version=1430, content=content)
        m['payload'] = json.dumps(payload)
        IotMsgBuilder.wrap_sign(m, client.cfg["secret"])
        return m

    @staticmethod
    def build_Bones_v2(client: Client, ext: dict):
        m = IotMsgBuilder.build_tpl()
        m['v'] = 2
        m['sessionId'] = client.cfg.get("sessionId")
        m['msgType'] = IotMsgTypeEnum.EVENT.value
        m['msgId'] = str(uuid.uuid4())
        # m['destType'] = BusinessTypeEnum.SESSION.value
        # m['destId'] = client.cfg["sessionId"]
        m['tag'] = 'STADIUM'
        m['srcApp'] = ".virgo"
        m['ack'] = 0
        m['ts'] = TimeUtil.now()
        content = dict(
            accountId=str(ext.get("accountId")),
            contentId=ext.get("contentId"),
            bonesData=ext.get("bonesData"),
            currentTimestamp=TimeUtil.now(),
        )
        payload = dict(tag="STAGE_REPORT_SKELETON_V2", version=1430, content=content)
        m['payload'] = json.dumps(payload)
        IotMsgBuilder.wrap_sign(m, client.cfg["secret"])
        return m

    @staticmethod
    def build_Bones_v3(client: Client, ext: dict):
        m = IotMsgBuilder.build_tpl()
        m['v'] = 2
        m['sessionId'] = client.cfg.get("sessionId")
        m['msgType'] = IotMsgTypeEnum.EVENT.value
        m['msgId'] = str(uuid.uuid4())
        # m['destType'] = BusinessTypeEnum.SESSION.value
        # m['destId'] = client.cfg["sessionId"]
        m['tag'] = 'MULTIPLAYER'
        m['srcApp'] = ".virgo"
        m['ack'] = 0
        m['ts'] = TimeUtil.now()
        content = dict(
            showType="BATTLE_TIME",
            currentTimestamp=TimeUtil.now(),
            clientVersion=1500,
            reportTimestamp=TimeUtil.now(),
            **ext
        )
        payload = dict(tag=ext.get('tag'), version=1, content=content)
        m['payload'] = json.dumps(payload)
        IotMsgBuilder.wrap_sign(m, client.cfg["secret"])
        log.info(f'模拟发送消息：{json.dumps(m)}')
        return m

    @staticmethod
    def build_scores_together(client: Client, ext: dict):
        m = IotMsgBuilder.build_tpl()
        m['v'] = 2
        m['sessionId'] = client.cfg.get("sessionId")
        m['msgType'] = IotMsgTypeEnum.EVENT.value
        m['msgId'] = str(uuid.uuid4())
        # m['destType'] = BusinessTypeEnum.SESSION.value
        # m['destId'] = client.cfg["sessionId"]
        m['tag'] = 'MULTIPLAYER'
        m['srcApp'] = ".virgo"
        m['ack'] = 0
        m['ts'] = TimeUtil.now()
        content = dict(
            roomId=str(ext.get("roomId")),
            roomItemId=str(ext.get("roomItemId")),
            accountId=str(ext.get("accountId")),
            trainingRecordId=str(ext.get("trainingRecordId")),
            currentTimestamp=TimeUtil.now(),
            calories=str(ext.get("calories")),
            duration=str(ext.get("duration")),
            effectiveDuration=str(ext.get("effectiveDuration")),
            playDuration=str(ext.get("playDuration")),
            score=str(ext.get("score")),
            unit=str(ext.get("unit")),
            wearHrmEffectiveDuration=str(ext.get("wearHrmEffectiveDuration")),
            effectiveness=str(ext.get("effectiveness")),
        )
        payload = dict(tag=str(ext.get('tag')), version=1500, content=content)
        m['payload'] = json.dumps(payload)
        log.info(f'分数上报pubTopic；{m}')
        IotMsgBuilder.wrap_sign(m, client.cfg["secret"])
        return m


    @staticmethod
    def build_group_class_together(client: Client, ext: dict):
        m = IotMsgBuilder.build_tpl()
        m['v'] = 2
        m['sessionId'] = client.cfg.get("sessionId")
        m['msgType'] = IotMsgTypeEnum.EVENT.value
        m['msgId'] = str(uuid.uuid4())
        # m['destType'] = BusinessTypeEnum.SESSION.value
        # m['destId'] = client.cfg["sessionId"]
        m['tag'] = 'MULTIPLAYER'
        m['srcApp'] = ".virgo"
        m['ack'] = 0
        m['ts'] = TimeUtil.now()
        content = dict(**ext)
        payload = dict(tag=str(ext.get('tag')), version=1500, content=content)
        m['payload'] = json.dumps(payload)
        log.info(f'团课数据上报pubTopic；{m}')
        IotMsgBuilder.wrap_sign(m, client.cfg["secret"])
        return m