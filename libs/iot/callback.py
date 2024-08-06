import json
from paho.mqtt.client import Client, MQTTMessage, ReasonCodes
from libs.logger import log
from libs.iot.fitureEnum import MQTTClientStatus
from libs.eventReport import EventReport


class IotFitureMsgCallback:

    @staticmethod
    def get_clientId(client):
        return str(client._client_id, encoding='utf-8')


class IotCallback(IotFitureMsgCallback):

    @staticmethod
    def connect_callback(client: Client, userdata, flags, rc, properties=None):
        client.status = MQTTClientStatus.CS_BROKER_YES
        log.debug(
            f'IOT Broker连接成功 clientId={IotFitureMsgCallback.get_clientId(client)} accountId:{userdata.get("userinfo").get("authentication").get("accountId")} rc={rc}')
        defaultTopic = userdata["cfg"]["mqttPassport"]["subscribeTopic"]
        client.subscribe(defaultTopic)
        log.debug(f"Subscribed Topic: {defaultTopic}")
        for topic in client.extTopics:
            client.subscribe(topic)
            log.debug(f"Subscribed Topic: {topic}")

    @staticmethod
    def subscribe_callback(client: Client, userdata, mid, rc: ReasonCodes, properties=None):
        client.status = MQTTClientStatus.CS_SUBSCRIPTION_YES
        log.debug(f'IOT Topic 订阅成功 clientId={IotCallback.get_clientId(client)} mid={mid},rc={rc[0].json()}')
        client.connect_device()

    @staticmethod
    def on_message_callback(client, userdata, msg: MQTTMessage):
        # fMsg = json.loads(msg.payload)
        log.debug(f'IOT 消息到达 clientId={IotCallback.get_clientId(client)} payload={msg.payload}')
        if client.messageHandler:
            client.messageHandler(msg.payload, msg.topic, client.host, client.port)

    @staticmethod
    def on_publish_callback(client, userdata, mid):
        log.debug(
            f'IOT 消息发送 成功 clientId={IotCallback.get_clientId(client)} deviceSN:{userdata.get("userinfo").get("virgo_headers").get("deviceSN")} mid={mid}')

    @staticmethod
    def disconnect_callback(client, userdata, rc, properties=None):
        try:
            log.warning(f'IOT 连接已断开 clientId={IotCallback.get_clientId(client)} rc={rc}')
            if client:
                client.disconnect()
                if client.closeCallback:
                    client.closeCallback()
        except Exception as err:
            log.warning(f'IOT 连接已断开 回调函数异常 clientId={IotCallback.get_clientId(client)} 异常 e={e}')
            EventReport.failure(request_type="MQTT",
                                name=f"Disconnected-rc({rc})",
                                response_time=0,
                                response_length=0,
                                exception=err)
        else:
            EventReport.success(request_type="MQTT",
                                name=f"Disconnected-rc({rc})",
                                response_time=0,
                                response_length=0)


class IotNewCallback(IotFitureMsgCallback):

    @staticmethod
    def connect_callback(client: Client, userdata, flags, rc, properties=None):
        client.status = MQTTClientStatus.CS_BROKER_YES
        log.info(
            f'IOT Broker连接成功 clientId={IotFitureMsgCallback.get_clientId(client)} accountId:{userdata.get("userinfo").get("authentication").get("accountId")} rc={rc}')
        subTopicsC = userdata["cfg"]["subTopicsC"]
        client.subscribe(subTopicsC)
        log.debug(f"Subscribed Topic: {subTopicsC}")
        for topic in client.extTopics:
            client.subscribe(topic)
            log.debug(f"Subscribed Topic: {topic}")

    @staticmethod
    def subscribe_callback(client: Client, userdata, mid, rc: ReasonCodes, properties=None):
        client.status = MQTTClientStatus.CS_SUBSCRIPTION_YES
        log.debug(f'IOT Topic 订阅成功 clientId={IotCallback.get_clientId(client)} mid={mid},rc={rc[0].json()}')
        client.connect_device()

    @staticmethod
    def on_message_callback(client, userdata, msg: MQTTMessage):
        # fMsg = json.loads(msg.payload)
        log.debug(f'IOT 消息到达 clientId={IotCallback.get_clientId(client)} payload={msg.payload}')
        if client.messageHandler:
            client.messageHandler(msg.payload, msg.topic, client.host, client.port)

    @staticmethod
    def on_publish_callback(client, userdata, mid):
        log.debug(
            f'IOT 消息发送 成功 clientId={IotCallback.get_clientId(client)} deviceSN:{userdata.get("userinfo").get("virgo_headers").get("deviceSN")} mid={mid}')

    @staticmethod
    def on_log(client, userdata, level, buf):
        log.debug(
            f'IOT 收到log消息 成功 clientId={IotCallback.get_clientId(client)} deviceSN:{userdata.get("userinfo").get("virgo_headers").get("deviceSN")} level={level}, buf={buf}')

    @staticmethod
    def disconnect_callback(client, userdata, rc, properties=None):
        try:
            log.warning(f'IOT 连接已断开 clientId={IotCallback.get_clientId(client)} rc={rc}')
            if client:
                client.disconnect()
                if client.closeCallback:
                    client.closeCallback()
        except Exception as err:
            log.warning(f'IOT 连接已断开 回调函数异常 clientId={IotCallback.get_clientId(client)} 异常 e={e}')
            EventReport.failure(request_type="MQTT",
                                name=f"Disconnected-rc({rc})",
                                response_time=0,
                                response_length=0,
                                exception=err)
        else:
            EventReport.success(request_type="MQTT",
                                name=f"Disconnected-rc({rc})",
                                response_time=0,
                                response_length=0)