from enum import Enum


class IotMsgTypeEnum(Enum):
    HB = "HB"
    HI = "HI"
    MSG = "MSG"
    NOT_FOUND = "NOTFOUND"
    RESET = "RESET"
    FIN = "FIN"
    CLOSE = "CLOSE"
    EVENT = "EVENT"
    ACK = "ACK"


class IotProtocol(Enum):
    MQTTv31 = 3
    MQTTv311 = 4
    MQTTv5 = 5


class IotTransport(Enum):
    tcp = "tcp"
    websockets = "websockets"
    wss = "websockets"  # wss 是 websockets 的简写 主要用于微信环境


class BusinessTypeEnum(Enum):
    SESSION = 'SESSION'
    taurus = 'taurus'
    virgo = 'virgo'
    # store_applet = 'store_applet'


class IotAppTypeEnum(Enum):
    taurus = 'taurus'
    # ios_taurus = 'ios.taurus'
    store_applet = 'store_applet'
    android_fsf = 'android.fsf'
    android_rdm = 'android.rdm'
    virgo = 'virgo'
    wallcome = 'wallcome'
    skywalking = 'skywalking'


class UserClientEnum(Enum):
    taurus = 'taurus'
    virgo = 'virgo'

    pisces = 'pisces'
    fsf = 'fsf'
    rdm = 'rdm'
    skywalking = 'skywalking'

    aries = 'aries'
    # fsf = 'fsf'
    rdm4power = 'rdm4power'


class MQTTClientStatus(Enum):
    CS_CLIENT_INITED = 'CS_CLIENT_INITED'  # 客户端初始化完毕

    CS_BROKER_INITED = 'CS_BROKER_INITED'  # 待连接broker
    CS_BROKER_YES = 'CS_BROKER_YES'  # 已连接broker
    CS_BROKER_NO = 'CS_BROKER_NO'  # 未连接broker

    CS_SUBSCRIPTION_YES = 'CS_SUBSCRIPTION_YES'  # 订阅成功
    CS_SUBSCRIPTION_NO = 'CS_SUBSCRIPTION_NO'  # 订阅失败

    CS_CLIENT_YES = 'CS_CLIENT_YES'  # 已可进行业务使用
    CS_CLIENT_NO = 'CS_CLIENT_NO'  # 不可进行业务使用

    CS_PAIR_YES = 'CS_PAIR_YES'  # 已连接对端
    CS_PAIR_NO = 'CS_PAIR_NO'  # 已断开对端连接
